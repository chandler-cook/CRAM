# Import necessary libraries
import os
from unsloth import FastLanguageModel  # Import custom language model library
import torch  # PyTorch for model and training operations
from trl import SFTTrainer  # Trainer for supervised fine-tuning
from transformers import TrainingArguments  # Arguments for model training
from datasets import load_dataset, concatenate_datasets, Dataset, Value, Features  # Dataset management

# Retrieving Hugging Face token from environment variable
hf_token = os.getenv('HF_TOKEN')    # Using environment variable as access token instead of hard coding

# Defining maximum sequence length for the model
max_seq_length = 2048

# Loading the original dataset from a remote URL
original_dataset = load_dataset("json", data_files={"train": "https://huggingface.co/datasets/laion/OIG/resolve/main/unified_chip2.jsonl"}, split="train")
print("Original dataset features:", original_dataset.features)  # Print dataset features

# Loading an additional dataset from a local file with data to fin-tune the model
additional_dataset = load_dataset("json", data_files={"train": "my_dataset.jsonl"}, split="train")
print("Additional dataset features:", additional_dataset.features)  # Print features of the additional dataset

# Function to preprocess the additional dataset
def preprocess_dataset(dataset):
    text_data = []
    for example in dataset:
        text_entry = f"{example['prompt']} {example['response']}"  # Concatenate 'prompt' and 'response'
        text_data.append({"text": text_entry})  # Ensure key matches original dataset's expected structure
    # Defining the features of the dataset
    features = Features({"text": Value(dtype='string')})
    # Create and return a dataset from the preprocessed data
    return Dataset.from_dict({"text": [item["text"] for item in text_data]}, features=features)

# Applying preprocessing to the additional dataset
additional_dataset = preprocess_dataset(additional_dataset)

# Combining the original and additional datasets
combined_dataset = concatenate_datasets([original_dataset, additional_dataset])

# Loading the pre-trained Mistral model
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/mistral-7b-bnb-4bit",  # Model name
    max_seq_length=max_seq_length,  # Maximum sequence length
    dtype=None,  # Data type for the model
    load_in_4bit=True,  # Load the model in 4-bit precision
)

# Preparing the model for inference
model = FastLanguageModel.for_inference(model)

# Defining a function to generate text using the model
def generate_text(text):
    inputs = tokenizer(text, return_tensors="pt").to("cuda:0")  # Tokenize and move to GPU
    outputs = model.generate(**inputs, max_new_tokens=20)  # Generate text
    print(tokenizer.decode(outputs[0], skip_special_tokens=True))  # Decode and print the generated text

# Generating and print text before training
print("Before training\n")
generate_text("List the top 5 most popular movies of all time.")

# Performing model patching and apply Fast LoRA (Low-Rank Adaptation) weights
model = FastLanguageModel.get_peft_model(
    model,
    r=16,  # Rank of the LoRA adapter
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",  # Target modules for LoRA adaptation
                    "gate_proj", "up_proj", "down_proj",
                    "embed_tokens", "lm_head"],
    lora_alpha=16,  # Scaling factor for LoRA
    lora_dropout=0,  # Dropout rate for LoRA
    bias="none",  # Bias setting for LoRA
    use_gradient_checkpointing=True,  # Use gradient checkpointing to save memory
    random_state=3407,  # Random seed
    max_seq_length=max_seq_length,  # Maximum sequence length
    use_rslora=False,  # Use RSLora if set to True
    loftq_config=None,  # Configuration for LoFTQ (if any)
)

# Define and configure the trainer
trainer = SFTTrainer(
    model=model,
    train_dataset=combined_dataset,  # Use the combined dataset for training
    dataset_text_field="text",  # Field in dataset containing text
    max_seq_length=max_seq_length,  # Maximum sequence length
    tokenizer=tokenizer,
    args=TrainingArguments(
        per_device_train_batch_size=2,  # Batch size per device
        gradient_accumulation_steps=4,  # Accumulate gradients over multiple steps
        warmup_steps=10,  # Number of warmup steps
        max_steps=60,  # Total number of training steps
        fp16=not torch.cuda.is_bf16_supported(),  # Use FP16 precision if supported
        bf16=torch.cuda.is_bf16_supported(),  # Use BF16 precision if supported
        logging_steps=1,  # Log training metrics every step
        output_dir="outputs",  # Directory to save training outputs
        optim="adamw_8bit",  # Optimizer type
        seed=3407,  # Random seed
    ),
)

# Training the model
trainer.train()

# Generating and printing text after training
print("\n ######## \nAfter training\n")
generate_text("List the top 5 most popular movies of all time.")

# Saving and pushing the trained model to Hugging Face Hub
model.save_pretrained("lora_model")  # Save model weights
model.save_pretrained_merged("outputs", tokenizer, save_method="merged_16bit")  # Save model with merged weights
model.push_to_hub_merged("gradams/PhysicalSecurityScoring-merged", tokenizer, save_method="merged_16bit", token=os.environ.get(hf_token))  # Push model to hub with merged weights
model.push_to_hub("gradams/PhysicalSecurityScoring", tokenizer, save_method="lora", token=os.environ.get(hf_token))  # Push model to hub with LoRA weights
