import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient


# Load environment variables
load_dotenv()
token = os.getenv("HF_TOKEN")
if not token:
    raise SystemExit("Please set HF_TOKEN in .env (HF_TOKEN=hf_...)")


# Initialize Hugging Face client
client = InferenceClient(api_key=token)


# Analyze sentiment (test)
result = client.text_classification(
    "Software Architecture rocks!",
    model="cardiffnlp/twitter-roberta-base-sentiment",
    top_k=1 
)


# Print output
print("\nSentiment score:")

r = result[0]

if r.label == "LABEL_0":
    sentiment = "negative"
elif r.label == "LABEL_1":
    sentiment = "neutral"
elif r.label == "LABEL_2":
    sentiment = "positive"
    
print(f"{sentiment.capitalize()}: {round(r.score * 100, 2)}%")



