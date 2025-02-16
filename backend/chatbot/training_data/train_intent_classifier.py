import pandas as pd
from sklearn.model_selection import train_test_split
from transformers import (
    DistilBertForSequenceClassification,
    DistilBertTokenizer,
    Trainer,
    TrainingArguments,
    EarlyStoppingCallback
)
from datasets import Dataset
import numpy as np
from sklearn.metrics import accuracy_score
import nlpaug.augmenter.word as naw


MODEL_NAME = "distilbert-base-multilingual-cased"
DATASET_PATH = "/Users/julianrivera/Documents/StoneERPTest/stone-chatbot/backend/chatbot/training_data/intents.csv"
MODEL_SAVE_PATH = "./intent_model"

df = pd.read_csv(DATASET_PATH)

aug = naw.SynonymAug(aug_src='wordnet')
augmented_texts = []
augmented_labels = []

for _, row in df.iterrows():
    augmented = aug.augment(row['text'], n=2)
    augmented_texts.extend(augmented)
    augmented_labels.extend([row['intent']]*len(augmented))
    
df_augmented = pd.DataFrame({'text': augmented_texts, 'intent': augmented_labels})
df = pd.concat([df, df_augmented])

intent_labels = df['intent'].unique().tolist()
label2id = {label: i for i, label in enumerate(intent_labels)}
df['label'] = df['intent'].map(label2id)

train_df, val_df = train_test_split(df, test_size=0.2, stratify=df['intent'])

tokenizer = DistilBertTokenizer.from_pretrained(MODEL_NAME)

def tokenize(batch):
    return tokenizer(
        batch['text'], 
        padding=True, 
        truncation=True,
        max_length=128,
        return_tensors="pt"
    )

train_dataset = Dataset.from_pandas(train_df).map(tokenize, batched=True)
val_dataset = Dataset.from_pandas(val_df).map(tokenize, batched=True)

training_args = TrainingArguments(
    output_dir='./results',
    num_train_epochs=15,
    per_device_train_batch_size=16,
    evaluation_strategy='epoch',
    logging_steps=50,
    learning_rate=2e-5,
    weight_decay=0.01,
    save_strategy='epoch',
    load_best_model_at_end=True,
    metric_for_best_model="accuracy",
    greater_is_better=True,
    save_total_limit=2,
)

def compute_metrics(pred):
    labels = pred.label_ids
    preds = pred.predictions.argmax(-1)
    return {'accuracy': accuracy_score(labels, preds)}

model = DistilBertForSequenceClassification.from_pretrained(
    MODEL_NAME,
    num_labels=len(intent_labels),
    id2label={v: k for k, v in label2id.items()}
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    compute_metrics=compute_metrics,
    callbacks=[EarlyStoppingCallback(early_stopping_patience=3)]
)


print("Iniciando entrenamiento...")
trainer.train()
print("Guardando modelo...")
trainer.save_model(MODEL_SAVE_PATH)
tokenizer.save_pretrained(MODEL_SAVE_PATH)
print(f"Modelo guardado en: {MODEL_SAVE_PATH}")


