from bson import ObjectId
from mongoengine import Document, StringField
from mongoengine import ObjectIdField, IntField, DateTimeField, ListField, EmbeddedDocument, \
    EmbeddedDocumentField

from apps.transactions import constants


class TransactionModel(Document):
    meta = {
        "collection": "transaction",
        "indexes": ["merchantId"]
    }

    merchantId = ObjectIdField(required=True)
    amount = IntField(required=True)
    createdAt = DateTimeField(required=True)

    @classmethod
    def _generate_base_chart_pipeline(cls, merchant_id: str | None) -> list[dict]:
        match merchant_id:
            case None:
                pipeline = []
            case _:
                pipeline = [{"$match": {"merchantId": ObjectId(merchant_id)}}]

        pipeline.extend([
            {
                "$addFields": {
                    "adjustedDate": {
                        "$dateFromParts": {
                            "year": {"$year": "$createdAt"},
                            "month": {"$month": "$createdAt"},
                            "day": {"$dayOfMonth": "$createdAt"}
                        }
                    }
                }
            },
        ])

        return pipeline

    @classmethod
    def group_by_type(cls, chart_type: str, merchant_id: str | None) -> list[dict]:
        pipeline = cls._generate_base_chart_pipeline(merchant_id)

        match chart_type:
            case constants.COUNT:
                group_value = {"$count": {}}
            case constants.AMOUNT:
                group_value = {"$sum": "$amount"}
            case _:
                raise ValueError("Invalid chart_type")

        pipeline.extend([
            {
                "$group": {
                    "_id": "$adjustedDate",
                    "value": group_value,
                }
            },
            {
                "$project": {
                    "datetime": "$_id",
                    "value": 1,
                    "_id": 0
                }
            },
            {
                "$sort": {
                    "datetime": 1
                }
            },
        ])
        return list(cls.objects.aggregate(pipeline))


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
