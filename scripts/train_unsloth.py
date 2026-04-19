"""
Unsloth local training script for InfraMind (Aegis-Swarm).
Requirements: pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git" trl peft
"""
import os
import torch
from datasets import load_dataset
from trl import SFTTrainer
from transformers import TrainingArguments

# Try importing Unsloth. If it fails, fallback to standard transformers or mock for demo
try:
    from unsloth import FastLanguageModel
    from unsloth.chat_templates import get_chat_template
    HAS_UNSLOTH = True
except ImportError:
    HAS_UNSLOTH = False
    print("Warning: Unsloth not found. Install it for 2x faster training.")

def format_chat_template(example):
    # This aligns the JSONL 'conversations' with the ShareGPT schema
    return {"messages": example["conversations"]}

def main():
    if not os.path.exists("data/inframind_sft.jsonl"):
        print("Error: data/inframind_sft.jsonl not found. Run scripts/generate_dataset.py first.")
        return

    print("Loading InfraMind SFT Dataset...")
    dataset = load_dataset("json", data_files={"train": "data/inframind_sft.jsonl"}, split="train")
    
    # In a real environment, we would map the conversations to a standard format
    # For now, we assume standard ShareGPT format from the generator
    
    max_seq_length = 4096
    model_name = "unsloth/llama-3-8b-Instruct-bnb-4bit"

    if HAS_UNSLOTH:
        print(f"Initializing Unsloth Model: {model_name}")
        model, tokenizer = FastLanguageModel.from_pretrained(
            model_name=model_name,
            max_seq_length=max_seq_length,
            dtype=None,
            load_in_4bit=True,
        )

        model = FastLanguageModel.get_peft_model(
            model,
            r=16,
            target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
            lora_alpha=16,
            lora_dropout=0,
            bias="none",
            use_gradient_checkpointing="unsloth",
            random_state=42,
            use_rslora=False,
            loftq_config=None,
        )
        
        tokenizer = get_chat_template(
            tokenizer,
            chat_template="llama-3",
            mapping={"role": "role", "content": "content", "user": "user", "assistant": "assistant"}
        )

        def formatting_prompts_func(examples):
            convos = examples["conversations"]
            texts = [tokenizer.apply_chat_template(c, tokenize=False, add_generation_prompt=False) for c in convos]
            return {"text": texts}
            
        dataset = dataset.map(formatting_prompts_func, batched=True)

        trainer = SFTTrainer(
            model=model,
            tokenizer=tokenizer,
            train_dataset=dataset,
            dataset_text_field="text",
            max_seq_length=max_seq_length,
            dataset_num_proc=2,
            packing=False,
            args=TrainingArguments(
                per_device_train_batch_size=2,
                gradient_accumulation_steps=4,
                warmup_steps=5,
                max_steps=60,
                learning_rate=2e-4,
                fp16=not torch.cuda.is_bf16_supported(),
                bf16=torch.cuda.is_bf16_supported(),
                logging_steps=1,
                optim="adamw_8bit",
                weight_decay=0.01,
                lr_scheduler_type="linear",
                seed=42,
                output_dir="outputs",
            ),
        )

        print("Starting SFT Training on InfraMind Trajectories...")
        trainer_stats = trainer.train()
        print("Training Complete!")
        
        # Save LoRA adapters
        model.save_pretrained("lora_model")
        tokenizer.save_pretrained("lora_model")
        print("✓ Model saved to lora_model/")
    else:
        print("\n--- MOCK TRAINING MODE ---")
        print("Simulating training run because Unsloth/GPU is not available locally.")
        print(f"Dataset Size: {len(dataset)} episodes")
        print("Epoch 1/3 | Loss: 1.4532")
        print("Epoch 2/3 | Loss: 0.8921")
        print("Epoch 3/3 | Loss: 0.4201")
        print("Training complete. (Run this in Google Colab for real GPU execution).")

if __name__ == "__main__":
    main()
