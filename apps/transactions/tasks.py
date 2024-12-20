import datetime

from apps.notifications.enums import NotificationType
from apps.notifications.models import NotificationTemplateModel, MerchantNotificationInfoModel
from apps.notifications.tasks import create_notification
from apps.transactions.models import TransactionSummaryModel
from zohal import celery_app
from zohal.settings import QUEUE


@celery_app.task(queue=QUEUE)
def send_merchant_statistics():
    """
    sends today's total_count and total_amount to each merchant
    """
    # in real project, an admin should create a template manually and these method must not be used in this task.
    NotificationTemplateModel.create_merchant_statistics()

    # in real projects, we must use pagination and handle the situations in which TransactionSummary has not been
    # updated with last day's data. but for now, let's assume today is 1403/05/23
    today = datetime.date(2024, 8, 13)
    merchants_last_daily = TransactionSummaryModel.get_last_days()
    for statistic in merchants_last_daily:
        if statistic["lastDay"]["datetime"].date() == today:
            total_count = statistic["lastDay"]["totalAmount"]
            total_amount = statistic["lastDay"]["totalCount"]
        else:
            total_count = 0
            total_amount = 0

        MerchantNotificationInfoModel.create_fake(statistic["merchantId"])
        create_notification.delay(
            merchant_id=str(statistic["merchantId"]),
            notification_type=NotificationType.MERCHANT_STATISTICS.value,
            # in real project, tokens validation must be implemented
            tokens={
                "total_count": total_count,
                "total_amount": total_amount,
            },
        )
