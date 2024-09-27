import os
import torch
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP
from unsloth import FastLanguageModel
from trl import SFTTrainer
from transformers import TrainingArguments
from datasets import load_dataset, Dataset, Value, Features
import torch.multiprocessing as mp

# Function to initialize the distributed environment
def setup(rank, world_size):
    os.environ['MASTER_ADDR'] = '127.0.0.1'  # Master node address
    os.environ['MASTER_PORT'] = '29500'      # Master node port
    os.environ['WORLD_SIZE'] = str(world_size)
    os.environ['RANK'] = str(rank)
    
    dist.init_process_group(backend='nccl', rank=rank, world_size=world_size)
    torch.cuda.set_device(rank)

# Load dataset
my_dataset = load_dataset("json", data_files={"train": "my_dataset.jsonl"}, split="train")

# Preprocess dataset
def preprocess_dataset(dataset):
    text_data = []
    for example in dataset:
        text_data.append({"text": example['prompt'], "response": int(example['response'])})
    features = Features({"text": Value(dtype='string'), "response": Value(dtype='int32')})
    return Dataset.from_dict({"text": [item["text"] for item in text_data], "response": [item["response"] for item in text_data]}, features=features)

my_dataset = preprocess_dataset(my_dataset)

# Load model and tokenizer
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/mistral-7b-bnb-4bit",
    max_seq_length=2048,
    dtype=None,
    load_in_4bit=True
)

# Tokenization function
def tokenize_function(examples):
    return tokenizer(examples["text"], padding="max_length", truncation=True, max_length=2048)

# Tokenize dataset
tokenized_dataset = my_dataset.map(tokenize_function, batched=True)

# Add labels
def add_labels(examples):
    examples["labels"] = examples["response"]
    return examples

tokenized_dataset = tokenized_dataset.map(add_labels, batched=True)

# Function to set up the distributed model
def prepare_model(rank, world_size):
    setup(rank, world_size)  # Setup distributed environment
    
    # Move model to the GPU with the specific rank
    model.to(rank)
    
    # Wrap model with DistributedDataParallel
    model = DDP(model, device_ids=[rank])
    
    return model

# Training arguments
training_args = TrainingArguments(
    per_device_train_batch_size=2,
    gradient_accumulation_steps=4,
    warmup_steps=10,
    max_steps=400,
    fp16=not torch.cuda.is_bf16_supported(),
    bf16=torch.cuda.is_bf16_supported(),
    logging_steps=1,
    output_dir="outputs",
    optim="adamw_8bit",
    seed=3407,
)

# Main function for distributed training
def main(rank, world_size):
    model = prepare_model(rank, world_size)
    
    # Initialize the trainer
    trainer = SFTTrainer(
        model=model,
        train_dataset=tokenized_dataset,
        dataset_text_field="text",
        max_seq_length=2048,
        tokenizer=tokenizer,
        args=training_args
    )
    
    # Start training
    trainer.train()

# Entry point for distributed training
if __name__ == "__main__":
    world_size = 3  # Adjust based on the number of GPUs available
    
    # Use torch multiprocessing to spawn multiple processes
    mp.spawn(main, args=(world_size,), nprocs=world_size, join=True)


"""""
Need to add these envornment variable to establish connection: 

export MASTER_ADDR="127.0.0.1"  # Set this to the master node's IP address
export MASTER_PORT=29500  # Set to a free port for the master connection
export WORLD_SIZE=3  # Number of nodes being distributed between
export RANK=0  # This will be pw each node preference will be set

"""""

"""
Alternate implementation:
import os
import torch
import torch.multiprocessing as mp

def setup(rank, world_size):
    os.environ['MASTER_ADDR'] = '127.0.0.1'  # Master node address
    os.environ['MASTER_PORT'] = '29500'      # Master node port
    os.environ['WORLD_SIZE'] = str(world_size)
    os.environ['RANK'] = str(rank)

    dist.init_process_group(backend='nccl', init_method='env://', rank=rank, world_size=world_size)
    torch.cuda.set_device(rank)

# Rest of your code remains the same

if __name__ == "__main__":
    world_size = 3  # Set based on your GPU count
    mp.spawn(main, args=(world_size,), nprocs=world_size, join=True)

"""

"""
To Launch the Script on Each Node:

On Node 1 (with 2 GPUs), run the script using the following command. This will start two processes on this node (one for each GPU):


MASTER_ADDR="10.71.71.1" MASTER_PORT=29500 WORLD_SIZE=3 RANK=0 python -m torch.distributed.launch --nproc_per_node=2 your_script.py

    MASTER_ADDR="10.71.71.1": This is the IP address of the master node.
    MASTER_PORT=29500: A free port for distributed communication.
    WORLD_SIZE=3: Total number of processes across all nodes (2 GPUs on Node 1 + 1 GPU on Node 2).
    RANK=0: This node will have ranks 0 and 1 (one for each GPU).

    

On Node 2 (with 1 GPU), run the following command:

MASTER_ADDR="10.71.71.1" MASTER_PORT=29500 WORLD_SIZE=3 RANK=2 python -m torch.distributed.launch --nproc_per_node=1 your_script.py

    RANK=2: The rank is 2 because Node 1 uses ranks 0 and 1.
"""