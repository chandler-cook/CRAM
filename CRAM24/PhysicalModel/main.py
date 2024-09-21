# Import necessary libraries
import os
from unsloth import FastLanguageModel
import torch
from trl import SFTTrainer
from transformers import TrainingArguments
from datasets import load_dataset, concatenate_datasets, Dataset, Value, Features


hf_token = os.getenv('HF_TOKEN')    # Using eniornment variable as access token instead of hard coding


max_seq_length = 2048

# Load the original dataset from the URL
original_dataset = load_dataset("json", data_files={"train": "https://huggingface.co/datasets/laion/OIG/resolve/main/unified_chip2.jsonl"}, split="train")
print("Original dataset features:", original_dataset.features)

# Load your additional dataset from a local file
additional_dataset = load_dataset("json", data_files={"train": "my_dataset.jsonl"}, split="train")
print("Additional dataset features:", additional_dataset.features)

# Preprocess the additional dataset
def preprocess_dataset(dataset):
    text_data = []
    for example in dataset:
        text_entry = f"{example['prompt']} {example['response']}"
        text_data.append({"text": text_entry})  # Ensure key matches original dataset's expected structure
    # Create a dataset and define features using Features
    features = Features({"text": Value(dtype='string')})
    return Dataset.from_dict({"text": [item["text"] for item in text_data]}, features=features)

# Preprocess the additional dataset
additional_dataset = preprocess_dataset(additional_dataset)

# Combine the datasets
combined_dataset = concatenate_datasets([original_dataset, additional_dataset])

# 2. Load Mistral model
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/mistral-7b-bnb-4bit",
    max_seq_length=max_seq_length,
    dtype=None,
    load_in_4bit=True,
)

# Ensure the model is set for inference
model = FastLanguageModel.for_inference(model)

# 3. Before training
def generate_text(text):
    inputs = tokenizer(text, return_tensors="pt").to("cuda:0")
    outputs = model.generate(**inputs, max_new_tokens=20)
    print(tokenizer.decode(outputs[0], skip_special_tokens=True))

print("Before training\n")
generate_text("List the top 5 most popular movies of all time.")

# 4. Do model patching and add fast LoRA weights and training
model = FastLanguageModel.get_peft_model(
    model,
    r=16,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                    "gate_proj", "up_proj", "down_proj",
                    "embed_tokens", "lm_head"],
    lora_alpha=16,
    lora_dropout=0,
    bias="none",
    use_gradient_checkpointing=True,
    random_state=3407,
    max_seq_length=max_seq_length,
    use_rslora=False,
    loftq_config=None,
)

trainer = SFTTrainer(
    model=model,
    train_dataset=combined_dataset,  # Use the combined dataset
    dataset_text_field="text",
    max_seq_length=max_seq_length,
    tokenizer=tokenizer,
    args=TrainingArguments(
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,
        warmup_steps=10,
        max_steps=60,
        fp16=not torch.cuda.is_bf16_supported(),
        bf16=torch.cuda.is_bf16_supported(),
        logging_steps=1,
        output_dir="outputs",
        optim="adamw_8bit",
        seed=3407,
    ),
)
trainer.train()

print("\n ######## \nAfter training\n")
generate_text("List the top 5 most popular movies of all time.")

# 5. Save and push to Hub
model.save_pretrained("lora_model")
model.save_pretrained_merged("outputs", tokenizer, save_method="merged_16bit")
model.push_to_hub_merged("gradams/PhysicalSecurityScoring-merged", tokenizer, save_method="merged_16bit", token=os.environ.get(hf_token))
model.push_to_hub("gradams/PhysicalSecurityScoring", tokenizer, save_method="lora", token=os.environ.get(hf_token))
