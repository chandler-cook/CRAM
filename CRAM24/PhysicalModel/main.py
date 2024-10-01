import torch
import os
from transformers import Trainer, TrainingArguments, AutoModelForCausalLM, AutoTokenizer
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import cpu_count
from accelerate import init_empty_weights, load_checkpoint_and_dispatch

# Clearing CUDA memory before starting the training to free up any cached memory
torch.cuda.empty_cache()

# Setting CUDA environment variable to manage memory fragmentation
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"

# Getting the number of CPUs allocated by Slurm (if available), or fall back to cpu_count()
num_cpus = int(os.getenv('SLURM_CPUS_PER_TASK', cpu_count()))
print(f"Number of available CPUs (from SLURM or fallback): {num_cpus}")

# Setting the folder for offloading model parts to disk in the current directory
offload_folder = os.path.join(os.getcwd(), "offload_tmp")
os.makedirs(offload_folder, exist_ok=True)

# Setting the local directory to save the model after fine-tuning
local_model_path = os.path.join(os.getcwd(), "local_model")
os.makedirs(local_model_path, exist_ok=True)

# Downloading and loading the model and tokenizer from Hugging Face
model_name = "mattshumer/Reflection-Llama-3.1-70B"
model = AutoModelForCausalLM.from_pretrained(model_name, cache_dir=local_model_path)
tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=local_model_path)

# Saving the pre-trained model to local_model before training (optional)
model.save_pretrained(local_model_path)
tokenizer.save_pretrained(local_model_path)

# Offloading parts of the model to reduce memory usage and enable multi-GPU support
model = load_checkpoint_and_dispatch(
    model,
    local_model_path,  # Local model path
    device_map="auto",  # Offloads parts to CPU, GPU, or disk as necessary
    offload_folder=offload_folder  # Specify the offload folder
)

# If multiple GPUs are available, use DataParallel
if torch.cuda.device_count() > 1:
    print(f"Using {torch.cuda.device_count()} GPUs")
    model = torch.nn.DataParallel(model)

# Defining the training arguments
training_args = TrainingArguments(
    fp16=True,  # Set to True to use FP16 precision (or False if GPU doesn't support it)
    bf16=torch.cuda.is_bf16_supported(),  # Using BF16 if supported, otherwise FP16
    gradient_checkpointing=True,  # Enabling gradient checkpointing to reduce memory usage
    logging_steps=1,
    output_dir="outputs",
    optim="adamw_8bit",  # Using 8-bit Adam optimizer to further reduce memory usage
    seed=3407,
    per_device_train_batch_size=16,  # Lowered batch size to reduce memory usage
    gradient_accumulation_steps=8,  # Increased gradient accumulation to simulate a larger batch size
    num_train_epochs=1,  # Use this instead of 'max_steps' to ensure at least one epoch of training
    dataloader_num_workers=num_cpus,  # Utilize available CPU cores for data loading
)

# Initialize the Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset="my_dataset.jsonl",  # Replace with your actual dataset
)

# Train the model using available processors
def train_model():
    trainer.train()

# Training the model
train_model()

# Save the fine-tuned model to the local_model directory
print(f"Saving fine-tuned model to {local_model_path}")
model.save_pretrained(local_model_path)
tokenizer.save_pretrained(local_model_path)

# Save the fine-tuned model to 'outputs' directory as well (optional)
model.save_pretrained("outputs")
tokenizer.save_pretrained("outputs")

# Optionally push the model to Hugging Face Hub
if torch.cuda.device_count() > 1:
    model.module.push_to_hub("gradams/PhysicalSecurityScoring")
else:
    model.push_to_hub("gradams/PhysicalSecurityScoring")

# Optionally save merged weights if available
if hasattr(model, 'save_pretrained_merged'):
    if torch.cuda.device_count() > 1:
        model.module.save_pretrained_merged("outputs", tokenizer, save_method="merged_16bit")
        model.module.push_to_hub_merged("gradams/PhysicalSecurityScoring-merged", tokenizer, save_method="merged_16bit", token=os.getenv('HF_TOKEN'))
    else:
        model.save_pretrained_merged("outputs", tokenizer, save_method="merged_16bit")
        model.push_to_hub_merged("gradams/PhysicalSecurityScoring-merged", tokenizer, save_method="merged_16bit", token=os.getenv('HF_TOKEN'))
