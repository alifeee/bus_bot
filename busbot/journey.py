"""Class and methods for journeys
"""

import datetime
from dataclasses import dataclass
from typing import Optional
from .stop import Stop


@dataclass
class Journey:
    """Bus journey"""

    journey_id: str
    type: str
    stops: list[Stop]
    day: datetime.date

    start_stop: Optional[Stop] = None
    end_stop: Optional[Stop] = None
