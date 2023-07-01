"""Class and methods for stops
"""

from dataclasses import dataclass


@dataclass
class Stop:
    """Bus stop"""

    id: str
    name: str
