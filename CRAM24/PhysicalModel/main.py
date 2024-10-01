import torch
import os
from transformers import Trainer, TrainingArguments, AutoModelForCausalLM, AutoTokenizer
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import cpu_count
from accelerate import init_empty_weights, load_checkpoint_and_dispatch

# Clear CUDA memory before starting the training to free up any cached memory
torch.cuda.empty_cache()

# Set CUDA environment variable to manage memory fragmentation
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"

# Get the number of CPUs allocated by Slurm (if available), or fall back to cpu_count()
num_cpus = int(os.getenv('SLURM_CPUS_PER_TASK', cpu_count()))
print(f"Number of available CPUs (from SLURM or fallback): {num_cpus}")

# Set the folder for offloading model parts to disk in the current directory
offload_folder = os.path.join(os.getcwd(), "offload_tmp")
os.makedirs(offload_folder, exist_ok=True)

# Download the model locally
model_name = "mattshumer/Reflection-Llama-3.1-70B"
local_model_path = os.path.join(os.getcwd(), "local_model")  # Local folder to store the model
os.makedirs(local_model_path, exist_ok=True)

# Load the model and tokenizer from Hugging Face and save locally
model = AutoModelForCausalLM.from_pretrained(model_name, cache_dir=local_model_path)
tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=local_model_path)

# Offload parts of the model to reduce memory usage and enable multi-GPU support
model = load_checkpoint_and_dispatch(
    model,
    local_model_path,  # Pass the local path containing the downloaded model
    device_map="auto",  # Offloads parts to CPU, GPU, or disk as necessary
    offload_folder=offload_folder  # Specify the offload folder
)

# If multiple GPUs are available, use DataParallel
if torch.cuda.device_count() > 1:
    print(f"Using {torch.cuda.device_count()} GPUs")
    model = torch.nn.DataParallel(model)

# Define the training arguments
training_args = TrainingArguments(
    fp16=True,  # Set to True to use FP16 precision (or False if GPU doesn't support it)
    bf16=torch.cuda.is_bf16_supported(),  # Use BF16 if supported, otherwise FP16
    gradient_checkpointing=True,  # Enable gradient checkpointing to reduce memory usage
    logging_steps=1,
    output_dir="outputs",
    optim="adamw_8bit",  # Use 8-bit Adam optimizer to further reduce memory usage
    seed=3407,
    per_device_train_batch_size=16,  # Lowered batch size to reduce memory usage
    gradient_accumulation_steps=8,  # Increased gradient accumulation to simulate a larger batch size
    num_train_epochs=1,
    dataloader_num_workers=num_cpus,  # Utilizing available CPU cores for data loading
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

# Test the model with multiple example prompts using multi-threading
def generate_score_for_prompt(prompt):
    input_ids = tokenizer(prompt, return_tensors="pt").input_ids
    generated_output = model.generate(input_ids)
    return int(generated_output)  # Assuming the output can be converted into an integer score

# List of test prompts
test_prompts = [
    "Score this system: Doors are unlocked at all times",
    "Score this system: All systems have administrator access by default",
    "Score this system: Security patches are not applied regularly"
]

# Number of threads for parallel inference, using the same number of CPUs
num_threads = num_cpus

# Utilize ThreadPoolExecutor for concurrent inference
with ThreadPoolExecutor(max_workers=num_threads) as executor:
    scores = list(executor.map(generate_score_for_prompt, test_prompts))

for prompt, score in zip(test_prompts, scores):
    print(f"Prompt: {prompt}\nGenerated integer score: {score}\n")

# Save and push the model to Hugging Face Hub
model.module.save_pretrained("lora_model") if torch.cuda.device_count() > 1 else model.save_pretrained("lora_model")
model.module.save_pretrained("outputs") if torch.cuda.device_count() > 1 else model.save_pretrained("outputs")

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
