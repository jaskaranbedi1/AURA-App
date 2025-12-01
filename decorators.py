from models import JournalEntry

#Decorator Pattern
# This class takes a JournalEntry and adds a simple mood tag based on its sentiment.
class TaggingDecorator:

    def __init__(self, entry: JournalEntry):
        self.entry = entry

    def add_tag(self) -> JournalEntry:
        label = self.entry.sentiment_label
        score = self.entry.sentiment_score

        # Default tag if entry doesn't have sentiment info
        tag = "unrated"

        # Only calculate a tag if both label and score exist.
        if label is not None and score is not None:
            if label == "positive":
                tag = "very positive" if score >= 0.80 else "positive"
            elif label == "neutral":
                tag = "neutral"
            elif label == "negative":
                tag = "needs attention" if score >= 0.80 else "negative"

        # save tag into the entry and return it
        self.entry.tag = tag
        return self.entry
