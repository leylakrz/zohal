import enum


class NotificationType(enum.Enum):
    TEST = "test"
    MERCHANT_STATISTICS = "merchant_statistics"


class NotificationStatus(enum.Enum):
    PENDING = "PENDING"
    SUCCESSFUL = "SUCCESSFUL"
    FAILED = "FAILED"
