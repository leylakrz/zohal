import logging
import random
from abc import ABC, abstractmethod

from mongoengine import EmbeddedDocument

from apps.notifications.enums import NotificationType
from apps.notifications.exeptions import TemplateNotFound
from apps.notifications.models import NotificationTemplateModel, MerchantNotificationInfoModel, \
    NotificationEmbeddedDocument, SMSNotification, EmailNotification, PushNotification, TelegramNotification


class Medium(ABC):
    GLOBAL_NAME: str = ...  # identifier of this class, field name in collections, etc

    def get_model_embedded_field(self, merchant_id: str, notification_type: NotificationType, tokens: dict):
        template: EmbeddedDocument = self.get_template(notification_type)
        embedded_field: NotificationEmbeddedDocument = self.create_embedded_field(template, merchant_id, tokens)
        return embedded_field

    def get_template(self, notification_type: NotificationType) -> EmbeddedDocument:
        try:
            template = NotificationTemplateModel.objects(notification_type=notification_type).get()
        except NotificationTemplateModel.DoesNotExist:
            logging.error("Template Not Found for medium=%s notification_type=%s",
                          self.GLOBAL_NAME, notification_type)
            raise TemplateNotFound

        medium_template = getattr(template, self.GLOBAL_NAME)
        if not medium_template:
            raise TemplateNotFound

        return medium_template

    @abstractmethod
    def create_embedded_field(self, template: EmbeddedDocument, merchant_id: str,
                              tokens: dict) -> NotificationEmbeddedDocument:
        ...

    def send(self, merchant_id, embedded_field: NotificationEmbeddedDocument) -> bool:
        merchant_notification_info = MerchantNotificationInfoModel.get_or_none(merchant_id)
        if not merchant_notification_info:
            return False
        return self._send(merchant_notification_info, embedded_field)

    def _send(self,
              merchant_notification_info: MerchantNotificationInfoModel,
              embedded_field=NotificationEmbeddedDocument):
        """
        in real projects, this method must be an abstractmethod and each medium must choose an available provider.
        """
        print(f"merchant_notification_info={merchant_notification_info.to_mongo().to_dict()} "
              f"embedded_field={embedded_field.to_mongo().to_dict()}")
        return random.choice([True, False])


class SMSMedium(Medium):
    GLOBAL_NAME = "sms"

    def create_embedded_field(self, template: EmbeddedDocument, merchant_id: str,
                              tokens: dict) -> SMSNotification:
        return SMSNotification(
            text=template["text"].format(
                total_count=tokens["total_count"],
                total_amount=tokens["total_amount"],
            ),
        )


class EmailMedium(Medium):
    GLOBAL_NAME = "email"

    def create_embedded_field(self, template: EmbeddedDocument, merchant_id: str,
                              tokens: dict) -> EmailNotification:
        return EmailNotification(
            subject=template["subject"],
            body=template["body"].format(
                total_count=tokens["total_count"],
                total_amount=tokens["total_amount"],
            ),
        )


class PushMedium(Medium):
    GLOBAL_NAME = "push"

    def create_embedded_field(self, template: EmbeddedDocument, merchant_id: str,
                              tokens: dict) -> PushNotification:
        raise NotImplemented


class TelegramMedium(Medium):
    GLOBAL_NAME = "telegram"

    def create_embedded_field(self, template: EmbeddedDocument, merchant_id: str,
                              tokens: dict) -> TelegramNotification:
        raise NotImplemented
