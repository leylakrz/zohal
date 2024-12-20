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

    @classmethod
    def group_by_all_types(cls, merchant_id: str | None) -> list[dict]:
        pipeline = cls._generate_base_chart_pipeline(merchant_id)

        pipeline.extend([
            {
                "$group": {
                    "_id": "$adjustedDate",
                    "totalCount": {"$count": {}},
                    "totalAmount": {"$sum": "$amount"},
                }
            },
            {
                "$project": {
                    "datetime": "$_id",
                    "totalCount": 1,
                    "totalAmount": 1,
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

    @classmethod
    def get_distinct_merchant_ids(cls) -> list:
        """
        in real projects, there is a merchant collection.
        """
        return list(cls.objects.distinct(field="merchantId"))


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

    @classmethod
    def get_chart(cls, chart_type: str, mode: str, merchant_id: str | None) -> list[dict]:
        match chart_type:
            case constants.COUNT:
                project_value = "totalCount"
            case constants.AMOUNT:
                project_value = "totalAmount"
            case _:
                raise ValueError("Invalid chart_type")

        field_name = f"{mode}_charts"

        pipeline = [
            {"$match": {"merchantId": ObjectId(merchant_id)}},
            {
                "$project": {
                    "key": f"$${field_name}.key",
                    "value": f"$${field_name}.{project_value}",
                }
            },
        ]
        return list(cls.objects.aggregate(pipeline))

    @classmethod
    def get_last_days(cls):
        pipeline = [
            {
                "$match": {
                    "merchantId": {"$ne": None}
                }
            },
            {
                "$project": {
                    "merchantId": 1,
                    "lastDay": {
                        "$arrayElemAt": ["$daily_charts", -1]
                    }
                }
            }
        ]

        return list(cls.objects.aggregate(pipeline))
