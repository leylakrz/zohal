import datetime
import logging

from bson import ObjectId
from mongoengine import StringField, EnumField, Document, ObjectIdField, EmbeddedDocumentField, EmbeddedDocument, \
    DateTimeField

from apps.notifications.enums import NotificationType, NotificationStatus


class SmsTemplate(EmbeddedDocument):
    text = StringField(required=True)


class EmailTemplate(EmbeddedDocument):
    subject = StringField(required=True)
    body = StringField(required=True)


class PushTemplate(EmbeddedDocument):
    text = StringField(required=True)


class TelegramTemplate(EmbeddedDocument):
    text = StringField(required=True)


class NotificationTemplateModel(Document):
    meta = {
        "collection": "notification_template",
    }
    notification_type = EnumField(NotificationType, required=True)
    sms = EmbeddedDocumentField(SmsTemplate)
    email = EmbeddedDocumentField(EmailTemplate)
    push = EmbeddedDocumentField(PushTemplate)
    telegram = EmbeddedDocumentField(TelegramTemplate)

    @classmethod
    def create_merchant_statistics(cls):
        # sms
        try:
            cls.objects(notification_type=NotificationType.MERCHANT_STATISTICS.value).get()
        except cls.DoesNotExist:
            cls(
                notification_type=NotificationType.MERCHANT_STATISTICS.value,
                sms=SmsTemplate(
                    text="total count = {total_count}\ntotal amount = {total_amount}"
                ),
                email=EmailTemplate(
                    subject="Merchant Statistics",
                    body="total count = {total_count}\ntotal amount = {total_amount}"
                )
            ).save()


class MerchantNotificationInfoModel(Document):
    meta = {
        "collection": "merchant_notification_info",
        "indexes": ["merchantId"]
    }
    merchantId = ObjectIdField(required=True)
    phone_number = StringField(required=False)
    email_address = StringField(required=False)
    push_token = StringField(required=False)
    telegram_id = StringField(required=False)

    @classmethod
    def create_fake(cls, merchant_id: ObjectId):
        try:
            cls.objects(merchantId=merchant_id).get()
        except cls.DoesNotExist:
            cls(
                merchantId=merchant_id,
                phone_number="fake",
                email_address="fake",
                push_token="fake",
                telegram_id="fake",
            ).save()

    @classmethod
    def get_or_none(cls, merchant_id: ObjectId):
        try:
            return cls.objects(merchantId=merchant_id).get()
        except cls.DoesNotExist as e:
            logging.error(e)
            return


class NotificationEmbeddedDocument(EmbeddedDocument):
    meta = {
        'abstract': True
    }

    status = EnumField(NotificationStatus, default=NotificationStatus.PENDING)
    datetime = DateTimeField()  # when sending notification has been successful or has failed

    def set_status(self, status: NotificationStatus, datetime):
        self.datetime = datetime
        self.status = status.value


class SMSNotification(NotificationEmbeddedDocument):
    text = StringField(required=True)


class EmailNotification(NotificationEmbeddedDocument):
    subject = StringField(required=True)
    body = StringField(required=True)


class PushNotification(NotificationEmbeddedDocument):
    text = StringField(required=True)


class TelegramNotification(NotificationEmbeddedDocument):
    text = StringField(required=True)


class NotificationModel(Document):
    meta = {
        "collection": "notification",
        "indexes": ["merchantId"]
    }
    merchantId = ObjectIdField(required=True)
    notification_type = EnumField(NotificationType, required=True)
    sms = EmbeddedDocumentField(SMSNotification)
    email = EmbeddedDocumentField(EmailNotification)
    push = EmbeddedDocumentField(PushNotification)
    telegram = EmbeddedDocumentField(TelegramNotification)

    @classmethod
    def get_or_none(cls, id: str):
        try:
            return cls.objects(id=ObjectId(id)).get()
        except cls.DoesNotExist as e:
            logging.error(e)
            return

    def set_status(self, field_name, status: NotificationStatus):
        getattr(self, field_name).set_status(status=status, datetime=datetime.datetime.now())
        self.save()
