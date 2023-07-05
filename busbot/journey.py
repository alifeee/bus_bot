"""Class and methods for journeys
"""

import datetime
from dataclasses import dataclass
from stop import Stop


@dataclass
class Journey:
    """Bus journey"""

    journey_id: str
    type: str
    stops: list[Stop]
    day: datetime.date
