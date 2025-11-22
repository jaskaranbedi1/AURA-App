from huggingface_hub import InferenceClient
from abc import ABC, abstractmethod

# Strategy Pattern: common interface for all sentiment analyzers

class SentimentStrategy(ABC):

    @abstractmethod
    def get_sentiment(self, text: str):
        pass


# Concrete Strategy using HuggingFace Inference API.
class HuggingFaceSentimentStrategy(SentimentStrategy):

    def __init__(self, hf_token: str):
        self.client = InferenceClient(api_key=hf_token)

    # Call Hugging Face sentiment model and mapping labels to negative/neutral/positive
    def get_sentiment(self, text):
        result = self.client.text_classification(
            text,
            model="cardiffnlp/twitter-roberta-base-sentiment",
            top_k=1
        )

        r = result[0]

        # label mapping 
        if r.label == "LABEL_0":
            label = "negative"
        elif r.label == "LABEL_1":
            label = "neutral"
        elif r.label == "LABEL_2":
            label = "positive"
        else:
            label = r.label

        return label, float(r.score)