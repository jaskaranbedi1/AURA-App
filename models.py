from dataclasses import dataclass
from datetime import datetime
from typing import Optional

    
# Class Represents a journal entry stored in MongoDB.
# It holds the text the user wrote, the sentiment results,the timestamp when it was created, and a mood tag(optionl).
    
@dataclass
class JournalEntry:
    text: str                                # The actual journal text
    sentiment_label: Optional[str]           # "positive", "neutral", "negative", or None
    sentiment_score: Optional[float]          # The model's confidence score (0.0 - 1.0)
    timestamp: datetime                       # When the entry was created
    tag: Optional[str] = None                 # tag added by TaggingDecorator
