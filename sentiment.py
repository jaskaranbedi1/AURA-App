from huggingface_hub import InferenceClient

#Initialize HuggingFace inference client.
   
def init_hf_client(hf_token: str):
    return InferenceClient(api_key=hf_token)

# Call Hugging Face sentiment model and mapping labels to negative/neutral/positive
def get_sentiment(client: InferenceClient, text):

    result = client.text_classification(
        text,
        model="cardiffnlp/twitter-roberta-base-sentiment",
        top_k=1
    )

    r = result[0]

#label mapping 
    if r.label == "LABEL_0":
        sentiment = "negative"
    elif r.label == "LABEL_1":
        sentiment = "neutral"
    elif r.label == "LABEL_2":
        sentiment = "positive"
    else:
        sentiment = r.label  # fallback, just in case

    return sentiment, float(r.score)

