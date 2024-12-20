from apps.notifications.enums import NotificationType
from apps.notifications.services import SMSMedium, EmailMedium, PushMedium, TelegramMedium

NOTIFICATION_TYPE_TO_MEDIUM: dict[NotificationType, list] = {
    NotificationType.MERCHANT_STATISTICS.value: [
        SMSMedium,
        EmailMedium,
    ],
}

MEDIUM_GLOBAL_NAME_TO_MEDIUM = {
    SMSMedium.GLOBAL_NAME: SMSMedium,
    EmailMedium.GLOBAL_NAME: EmailMedium,
    PushMedium.GLOBAL_NAME: PushMedium,
    TelegramMedium.GLOBAL_NAME: TelegramMedium,
}
