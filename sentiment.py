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
    

# Proxy pattern: wraps Wraps a real SentimentStrategy and caches sentiment results for repeated texts to avoid unnecessary API calls. 
class CachingSentimentProxy(SentimentStrategy):
    
    def __init__(self, real_strategy: SentimentStrategy):
        self._real_strategy = real_strategy
        self._cache: dict[str, tuple[str, float]] = {}

    def get_sentiment(self, text):
        # If we've seen this text before, return cached result
        if text in self._cache:
            return self._cache[text]

        # Otherwise delegate to the real strategy and cache the result
        label, score = self._real_strategy.get_sentiment(text)
        self._cache[text] = (label, score)
        return label, score