from mongoengine import Document, StringField
from mongoengine import ObjectIdField, IntField, DateTimeField, ListField, EmbeddedDocument, \
    EmbeddedDocumentField


class TransactionModel(Document):
    meta = {
        "collection": "transaction",
        "indexes": ["merchantId"]
    }

    merchantId = ObjectIdField(required=True)
    amount = IntField(required=True)
    createdAt = DateTimeField(required=True)


class TransactionChart(EmbeddedDocument):
    meta = {
        'abstract': True
    }

    key = StringField(required=True)
    totalAmount = IntField(required=True)
    totalCount = IntField(required=True)


class TransactionDailyChart(TransactionChart):
    datetime = DateTimeField(required=True)


class TransactionWeeklyChart(TransactionChart):
    year = IntField(required=True)
    week = IntField(required=True)


class TransactionMonthlyChart(TransactionChart):
    year = IntField(required=True)
    month = IntField(required=True)


class TransactionSummaryModel(Document):
    meta = {
        "collection": "transaction_summary",
        "indexes": ["merchantId"]
    }

    merchantId = ObjectIdField()
    daily_charts = ListField(EmbeddedDocumentField(TransactionDailyChart))
    weekly_charts = ListField(EmbeddedDocumentField(TransactionWeeklyChart))
    monthly_charts = ListField(EmbeddedDocumentField(TransactionMonthlyChart))
