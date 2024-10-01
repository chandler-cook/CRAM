import torch
import os
from transformers import Trainer, TrainingArguments, AutoModelForCausalLM, AutoTokenizer
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import cpu_count

# Get and print the number of available CPUs using multiprocessing.cpu_count()
num_cpus = cpu_count()
print(f"Number of available CPUs: {num_cpus}")


# Load the model and tokenizer
model_name = "mattshumer/Reflection-Llama-3.1-70B"
model = AutoModelForCausalLM.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)

# If multiple GPUs are available, use DataParallel
if torch.cuda.device_count() > 1:
    print(f"Using {torch.cuda.device_count()} GPUs")
    model = torch.nn.DataParallel(model)

# Define the training arguments
training_args = TrainingArguments(
    fp16=not torch.cuda.is_bf16_supported(),
    bf16=torch.cuda.is_bf16_supported(),
    logging_steps=1,
    output_dir="outputs",
    optim="adamw_8bit",
    seed=3407,
    per_device_train_batch_size=32,
    gradient_accumulation_steps=4,
    num_train_epochs=1,
    dataloader_num_workers=num_cpus  # Utilizing available CPU cores for data loading
)

# Initialize the Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset="my_dataset.jsonl"
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
