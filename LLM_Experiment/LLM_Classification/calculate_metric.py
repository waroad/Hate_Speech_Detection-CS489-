import os
import pandas as pd
import numpy as np
from sklearn.metrics import precision_score, recall_score, f1_score

promptTemplate_dir = './prompt_template.txt'
output_answer_dataset = './output_answer_dataset'
right_answer_dir = os.path.join(output_answer_dataset, "right_answer")

unsmile_labels = [
    "여성/가족",
    "남성",
    "성소수자",
    "인종/국적",
    "연령",
    "지역",
    "종교",
    "기타 혐오",
    "악플/욕설",
    "clean"
]

def filter_clean_labels(s: str):
    if s == "clean":
        return "Clean"
    elif s == "기타 혐오":
        return "기타혐오"
    return s

def is_right_formatOutput(answer: str):
    for category in unsmile_labels:
        category = filter_clean_labels(category)
        if not (f"({category}:0)" in answer or f"({category}:1)" in answer):
            return False
        if f"({category}:0)" in answer and f"({category}:1)" in answer:
            return False
    return True

def get_inferred_labels_from_response(response: str):
    """Extracts inferred labels from the response text."""
    inferred_labels = []
    for category in unsmile_labels:
        category = filter_clean_labels(category)
        if f"({category}:1)" in response:
            inferred_labels.append(np.int64(1))
        elif f"({category}:0)" in response:
            inferred_labels.append(np.int64(0))
        #else:
            #inferred_labels.append(np.int64(0))  # Default to 0 if not found
    return inferred_labels

if __name__ == "__main__":
    # Read the dataset
    file_path = 'unsmile_valid_v1.0.tsv'
    df = pd.read_csv(file_path, sep='\t')

    # List all files in the right_answer directory and extract the indices
    answered_files = [f for f in os.listdir(right_answer_dir) if f.endswith('.txt')]
    answered_indices = [int(f.split('.')[0]) for f in answered_files]

    # Prepare lists to compare ground truth and inferred results
    all_true_labels = []
    all_inferred_labels = []

    for index in answered_indices:
        row = df.iloc[index]
        true_labels = [row[label] for label in unsmile_labels]

        # Read the corresponding answer file
        answer_file_path = os.path.join(right_answer_dir, f"{index}.txt")
        with open(answer_file_path, 'r', encoding='utf-8') as file:
            response = file.read()

        if is_right_formatOutput(response):
            inferred_labels = get_inferred_labels_from_response(response)
            all_true_labels.append(true_labels)
            all_inferred_labels.append(inferred_labels)

    # Convert the lists into label-wise data for metric calculations
    all_true_labels = pd.DataFrame(all_true_labels, columns=unsmile_labels)
    all_inferred_labels = pd.DataFrame(all_inferred_labels, columns=unsmile_labels)

    # Print label-wise precision, recall, and F1-score
    print("Label-wise Metrics:")
    for label in unsmile_labels:
        precision = precision_score(all_true_labels[label], all_inferred_labels[label], zero_division=1)
        recall = recall_score(all_true_labels[label], all_inferred_labels[label], zero_division=1)
        f1 = f1_score(all_true_labels[label], all_inferred_labels[label], zero_division=1)

        print(f"{label}:")
        print(f"  Precision: {precision:.4f}")
        print(f"  Recall: {recall:.4f}")
        print(f"  F1-Score: {f1:.4f}\n")
