"""Class and methods for stops
"""

from dataclasses import dataclass
import datetime


@dataclass
class Stop:
    """Bus stop"""

    stop_id: str
    name: str

    # when part of a journey, the stop has a specific journey-unqiue id
    # and other metadata
    journey_stop_id: str = None
    journey_stop_time: datetime.datetime = None
