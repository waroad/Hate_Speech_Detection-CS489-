from datasets import load_dataset
from transformers import BertForSequenceClassification, TrainingArguments, Trainer, AutoTokenizer, \
    AutoModelForSequenceClassification
import torch
import numpy as np
from transformers import AutoTokenizer, AutoModel
from transformers import DataCollatorWithPadding
from sklearn.metrics import label_ranking_average_precision_score
from transformers import TextClassificationPipeline
import tqdm
from transformers.pipelines.base import KeyDataset
from sklearn.metrics import classification_report

# Load model and tokenizer
model = AutoModelForSequenceClassification.from_pretrained('plm')
tokenizer = AutoTokenizer.from_pretrained("beomi/KcELECTRA-base")

# Initialize pipeline
pipe = TextClassificationPipeline(
    model=model,
    tokenizer=tokenizer,
    device=0,
    return_all_scores=True,
    function_to_apply='sigmoid'
)

# List of labels to ignore
ignore_labels = {'기타 혐오', '악플/욕설', 'clean'}

# Function to filter and print results
def print_filtered_results(text):
    print(f"Input text: {text}")
    for result in pipe(text)[0]:
        if result['label'] not in ignore_labels:
            print(f"{result['label']}: {result['score']:.4f}")
    print("\n")

# Process input texts
#print_filtered_results("이래서 여자는 게임을 하면 안된다")
#print_filtered_results("여자는 예쁘다")
#print_filtered_results("한남 재기하라")

detection_results = pipe("이래서 여자는 게임을 하면 안된다")[0]
for result in detection_results:
            label = result['label']
            score = result['score']
            print(result)