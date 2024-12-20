from http import HTTPMethod

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from apps.transactions.serializers import TransactionChartSerializer
from apps.transactions.services import TransactionService


class TransactionViewSet(GenericViewSet):
    @action(methods=[HTTPMethod.GET], detail=False, url_path="chart/raw/(?P<chart_type>\w+)/(?P<mode>\w+)")
    def chart_raw(self, request, chart_type, mode):
        args: dict = self._validate_chart_args(chart_type, mode, request.GET)
        data = TransactionService().get_chart_raw(**args)
        return Response(data=data, status=status.HTTP_200_OK)

    @action(methods=[HTTPMethod.GET], detail=False, url_path="chart/(?P<chart_type>\w+)/(?P<mode>\w+)")
    def chart(self, request, chart_type, mode):
        args: dict = self._validate_chart_args(chart_type, mode, request.GET)
        data = TransactionService().get_chart(**args)
        return Response(data=data, status=status.HTTP_200_OK)

    def _validate_chart_args(self, chart_type, mode, request_get) -> dict:
        serializer = TransactionChartSerializer(data={
            "chart_type": chart_type,
            "mode": mode,
            **request_get.dict()
        })
        serializer.is_valid(raise_exception=True)
        return serializer.data
