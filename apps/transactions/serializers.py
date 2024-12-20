from rest_framework import serializers

from apps.transactions.constants import TRANSACTION_CHART_TYPE_CHOICES, TRANSACTION_CHART_MODE_CHOICES


class TransactionChartSerializer(serializers.Serializer):
    chart_type = serializers.ChoiceField(choices=TRANSACTION_CHART_TYPE_CHOICES)
    mode = serializers.ChoiceField(choices=TRANSACTION_CHART_MODE_CHOICES)
    merchant_id = serializers.CharField(max_length=24, min_length=24, default=None)
