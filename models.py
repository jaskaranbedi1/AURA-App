from dataclasses import dataclass
from datetime import datetime
from typing import Optional

    
# Represents a journal entry stored in MongoDB.
    
@dataclass
class JournalEntry:
    text: str
    sentiment_label: Optional[str]
    sentiment_score: Optional[float]
    timestamp: datetime
    tag: Optional[str] = None   # tag added by decorator
