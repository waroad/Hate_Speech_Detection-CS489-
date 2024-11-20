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
import csv

def preprocess_function(examples):
    tokenized_examples = tokenizer(str(examples["문장"]))
    tokenized_examples['labels'] = torch.tensor(examples["labels"], dtype=torch.float)
    return tokenized_examples

# Load the dataset
dataset = load_dataset('smilegate-ai/kor_unsmile')
print(dataset["train"][0])
unsmile_labels = ["여성/가족", "남성", "성소수자", "인종/국적", "연령", "지역", "종교", "기타 혐오", "악플/욕설", "clean"]
tokenizer = AutoTokenizer.from_pretrained("beomi/KcELECTRA-base")
tokenized_dataset = dataset.map(preprocess_function)
tokenized_dataset.set_format(type='torch', columns=['input_ids', 'labels', 'attention_mask', 'token_type_ids'])

data_collator = DataCollatorWithPadding(tokenizer=tokenizer)
num_labels = len(unsmile_labels)

model = AutoModelForSequenceClassification.from_pretrained(
    "beomi/KcELECTRA-base",
    num_labels=num_labels,
    problem_type="multi_label_classification"
)
model.config.id2label = {i: label for i, label in zip(range(num_labels), unsmile_labels)}
model.config.label2id = {label: i for i, label in zip(range(num_labels), unsmile_labels)}

def compute_metrics(x):
    return {
        'lrap': label_ranking_average_precision_score(x.label_ids, x.predictions),
    }

batch_size = 50

args = TrainingArguments(
    output_dir="model_output",
    evaluation_strategy="epoch",
    learning_rate=2e-5,
    per_device_train_batch_size=batch_size,
    per_device_eval_batch_size=batch_size,
    num_train_epochs=10,
    save_strategy='epoch',
    load_best_model_at_end=True,
    metric_for_best_model='lrap',
    greater_is_better=True,
)

trainer = Trainer(
    model=model,
    args=args,
    train_dataset=tokenized_dataset["train"],
    eval_dataset=tokenized_dataset["valid"],
    compute_metrics=compute_metrics,
    tokenizer=tokenizer,
    data_collator=data_collator
)

# For training, uncomment below lines
# trainer.train()
# trainer.save_model("test1")

# Load the pre-trained model for testing
model = AutoModelForSequenceClassification.from_pretrained('./plm')

pipe = TextClassificationPipeline(
    model=model,
    tokenizer=tokenizer,
    device=0,
    return_all_scores=True,
    function_to_apply='sigmoid'
)

# Sample inference
for result in pipe("이래서 여자는 게임을 하면 안된다")[0]:
    print(result)
for result in pipe("여자는 예쁘다")[0]:
    print(result)
for result in pipe("한남 재기하라")[0]:
    print(result)

# Function to convert output to predicted labels in a format for writing
def get_predicated_label_dict(output_labels, min_score=0.5):
    return {label: int(output_labels[i]['score'] > min_score) for i, label in enumerate(unsmile_labels)}

# Save inference results to a TSV file
with open('inference_results.tsv', 'w', newline='', encoding='utf-8') as tsvfile:
    fieldnames = ['문장'] + unsmile_labels
    writer = csv.DictWriter(tsvfile, fieldnames=fieldnames, delimiter='\t')
    writer.writeheader()

    for i, out in enumerate(tqdm.tqdm(pipe(KeyDataset(dataset['valid'], '문장')))):
        sentence = dataset['valid'][i]['문장']
        predicted_labels_dict = get_predicated_label_dict(out, 0.5)
        predicted_labels_dict['문장'] = sentence
        
        writer.writerow(predicted_labels_dict)

print("Inference results saved to inference_results.tsv")
