# Import necessary libraries
import os
from unsloth import FastLanguageModel  # Import custom language model library
import torch  # PyTorch for model and training operations
from trl import SFTTrainer  # Trainer for supervised fine-tuning
from transformers import TrainingArguments  # Arguments for model training
from datasets import load_dataset, Dataset, Value, Features  # Dataset management
import re  # For extracting integer score

# Retrieving Hugging Face token from environment variable
hf_token = os.getenv('HF_TOKEN')  # Using environment variable as access token instead of hard coding

# Defining maximum sequence length for the model
max_seq_length = 2048

# Loading the dataset from a local file with data to finetune the model
my_dataset = load_dataset("json", data_files={"train": "my_dataset.jsonl"}, split="train")
print("My dataset features:", my_dataset.features)  # Print features of the dataset

# Function to preprocess the dataset
def preprocess_dataset(dataset):
    text_data = []
    for example in dataset:
        # Keep the response as an integer
        text_data.append({"text": example['prompt'], "response": int(example['response'])})  # Convert response to int

    # Define the features with correct types: text as string and response as int
    features = Features({
        "text": Value(dtype='string'),
        "response": Value(dtype='int32')  # Keep response as an integer
    })
    
    # Return dataset with correct feature types
    return Dataset.from_dict({
        "text": [item["text"] for item in text_data], 
        "response": [item["response"] for item in text_data]
    }, features=features)

# Applying preprocessing to the dataset
my_dataset = preprocess_dataset(my_dataset)

# Loading the pre-trained Mistral model
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/mistral-7b-bnb-4bit",  # Model name
    max_seq_length=max_seq_length,  # Maximum sequence length
    dtype=None,  # Data type for the model
    load_in_4bit=True,  # Load the model in 4-bit precision
)

# Preparing the model for inference
model = FastLanguageModel.for_inference(model)

# Tokenizing the dataset
def tokenize_function(examples):
    return tokenizer(examples["text"], padding="max_length", truncation=True, max_length=max_seq_length)

# Apply tokenization
tokenized_dataset = my_dataset.map(tokenize_function, batched=True)

# Add labels (responses) back to the tokenized dataset
def add_labels(examples):
    examples["labels"] = examples["response"]  # Add response as labels for supervised learning
    return examples

# Add labels
tokenized_dataset = tokenized_dataset.map(add_labels, batched=True)

# Check the tokenized dataset structure
print(tokenized_dataset[0])

# Function to extract the score (integer) from the model's output text
def extract_score(output_text):
    # Search for the first number in the output text
    match = re.search(r'\d+', output_text)  # Find the first integer
    if match:
        return int(match.group(0))  # Return the integer as the score
    return "Invalid score"  # Return an error if no integer is found

# Function to generate integer score using the model
def generate_integer_score(prompt):
    inputs = tokenizer(prompt, return_tensors="pt").to("cuda:0")  # Tokenize input
    outputs = model.generate(**inputs, max_new_tokens=3, num_return_sequences=1)  # Restrict generation length
    output_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return extract_score(output_text)  # Post-process to ensure integer output

# Performing model patching and applying Fast LoRA (Low-Rank Adaptation) weights
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
    train_dataset=tokenized_dataset,  # Use the tokenized dataset for training
    dataset_text_field="text",  # Field in dataset containing text
    max_seq_length=max_seq_length,  # Maximum sequence length
    tokenizer=tokenizer,
    args=TrainingArguments(
        per_device_train_batch_size=2,  # Batch size per device                 
        gradient_accumulation_steps=4,  # Accumulate gradients over multiple steps          
        warmup_steps=10,  # Number of warmup steps
        max_steps=400,  # Total number of training steps                                 
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

# Test the model with an example prompt
test_prompt = "Score this system: Doors are unlocked at all times"
generated_score = generate_integer_score(test_prompt)
print(f"Generated integer score: {generated_score}")

# Saving and pushing the trained model to Hugging Face Hub
model.save_pretrained("lora_model")  # Save model weights
model.save_pretrained_merged("outputs", tokenizer, save_method="merged_16bit")  # Save model with merged weights
model.push_to_hub_merged("gradams/PhysicalSecurityScoring-merged", tokenizer, save_method="merged_16bit", token=os.getenv('HF_TOKEN'))  # Push model to hub with merged weights
model.push_to_hub("gradams/PhysicalSecurityScoring", tokenizer, save_method="lora", token=os.getenv('HF_TOKEN'))  # Push model to hub with LoRA weights
