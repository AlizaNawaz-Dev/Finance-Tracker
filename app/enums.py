import enum

class CapitalAction(enum.Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAW = "WITHDRAW"

class WithdrawalStatus(enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"  # <-- Make sure this is UPPECASE "APPROVED"
    REJECTED = "REJECTED"