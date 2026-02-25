from enum import Enum


class EEventState(Enum):
    NEW = "new"
    SETTLED = "settled"
    REFUNDED = "refunded"
