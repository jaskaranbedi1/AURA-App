from datetime import datetime, timezone
from models import JournalEntry

#Factory Pattern
# Class provides a central place to create JournalEntry objects 
    
class EntryFactory:

    @staticmethod
    def create(text, sentiment_label, sentiment_score):
        # Every entry gets a timestamp automatically when created.
        timestamp = datetime.now(timezone.utc)

        return JournalEntry(
            text=text,
            sentiment_label=sentiment_label,
            sentiment_score=sentiment_score,
            timestamp=timestamp
        )
