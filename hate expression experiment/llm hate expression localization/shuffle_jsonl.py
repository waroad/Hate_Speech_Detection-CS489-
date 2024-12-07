import json
import random

# File paths
input_file = "output_responses.jsonl"
output_file = "shuffled_output_responses.jsonl"

# Read the JSONL file and load data
with open(input_file, 'r', encoding='utf-8') as f:
    lines = [json.loads(line) for line in f]

# Shuffle the data
random.shuffle(lines)

# Update the indices and rename the 'idx' key
for new_idx, item in enumerate(lines):
    item["random_idx"] = new_idx  # Add new random index
    item["original_idx"] = item.pop("idx")  # Rename 'idx' to 'original idx'

# Write the shuffled data back to a new JSONL file
with open(output_file, 'w', encoding='utf-8') as f:
    for item in lines:
        f.write(json.dumps(item, ensure_ascii=False) + '\n')

print(f"Shuffled JSONL file saved to {output_file}")
