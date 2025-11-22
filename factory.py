from datetime import datetime, timezone
from models import JournalEntry

#Factory Pattern: Central place to create JournalEntry objects 
    
class EntryFactory:

    @staticmethod
    def create(text, sentiment_label, sentiment_score):
        return JournalEntry(
            text=text,
            sentiment_label=sentiment_label,
            sentiment_score=sentiment_score,
            timestamp=datetime.now(timezone.utc),
        )
