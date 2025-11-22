from models import JournalEntry

#Decorator Pattern: Adds a high-level mood tag to a JournalEntry based on its sentiment label and score
class TaggingDecorator:

    def __init__(self, entry: JournalEntry):
        self.entry = entry

    def add_tag(self) -> JournalEntry:
        label = self.entry.sentiment_label
        score = self.entry.sentiment_score

        # Default tag if we don't have sentiment info
        tag = "unrated"

        if label is not None and score is not None:
            if label == "positive":
                tag = "very positive" if score >= 0.80 else "positive"
            elif label == "neutral":
                tag = "neutral"
            elif label == "negative":
                tag = "needs attention" if score >= 0.80 else "negative"

        # Attach tag to the entry and return it
        self.entry.tag = tag
        return self.entry
