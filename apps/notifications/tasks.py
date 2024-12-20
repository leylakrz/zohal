from bson import ObjectId
from celery import group

from apps.notifications.constants import NOTIFICATION_TYPE_TO_MEDIUM, MEDIUM_GLOBAL_NAME_TO_MEDIUM
from apps.notifications.enums import NotificationType, NotificationStatus
from apps.notifications.exeptions import TemplateNotFound
from apps.notifications.models import NotificationModel
from apps.notifications.services import Medium
from zohal import celery_app
from zohal.settings import QUEUE


@celery_app.task(queue=QUEUE)
def create_notification(merchant_id, notification_type: NotificationType, tokens: dict):
    notification = NotificationModel(
        merchantId=ObjectId(merchant_id),
        notification_type=notification_type,
    )
    mediums = NOTIFICATION_TYPE_TO_MEDIUM[notification_type]
    medium_global_names = []
    for medium in mediums:
        try:
            embedded_field_value = medium().get_model_embedded_field(merchant_id, notification_type, tokens)
        except TemplateNotFound:
            pass
        else:
            setattr(notification, medium.GLOBAL_NAME, embedded_field_value)
            medium_global_names.append(medium.GLOBAL_NAME)
    notification.save()
    group([
        send_notification.s(notification_id=str(notification.id), medium_global_name=medium_global_name)
        for medium_global_name in medium_global_names
    ]).apply_async()


@celery_app.task(queue=QUEUE, bind=True, retry_kwargs={"max_retries": 3, "countdown": 0.5})
def send_notification(self, notification_id, medium_global_name):
    notification = NotificationModel.get_or_none(notification_id)
    if not notification:
        return False

    medium: Medium = MEDIUM_GLOBAL_NAME_TO_MEDIUM[medium_global_name]()
    result = medium.send(notification.merchantId, getattr(notification, medium_global_name))
    if not result:
        if self.request.retries == self.max_retries:
            notification.set_status(medium_global_name, NotificationStatus.FAILED)
        else:
            self.retry()
    else:
        notification.set_status(medium_global_name, NotificationStatus.SUCCESSFUL)

    return result
