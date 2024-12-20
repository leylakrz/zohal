import datetime

import jdatetime
from django.core.management import BaseCommand

from apps.transactions.constants import TRANSACTION_DAILY_CHART_KEY_FORMAT
from apps.transactions.models import TransactionModel, TransactionSummaryModel
from apps.utils.general import gregorian_datetime_to_jalali_date_str, number_to_jalali_month_name


class Command(BaseCommand):
    help = "Summarize Transactions"

    def handle(self, *args, **kwargs):
        TransactionSummaryModel.objects().delete()  # in real projects, we must update the existing summaries

        all_merchant_ids = TransactionModel.get_distinct_merchant_ids() + [None]
        for merchant_id in all_merchant_ids:
            daily_chart = TransactionModel.group_by_all_types(merchant_id)
            # TODO: refactor to apply DRY
            TransactionSummaryModel(
                merchantId=merchant_id,
                daily_charts=self._get_daily_chart_raw(daily_chart),
                weekly_charts=self._get_weekly_chart_raw(daily_chart),
                monthly_charts=self._get_monthly_chart_raw(daily_chart),
            ).save()

    def _get_daily_chart_raw(self, daily_chart: list[dict]) -> list[dict]:
        daily_chart_processed = []
        for index, day in enumerate(daily_chart):
            daily_chart_processed.append({
                "key": gregorian_datetime_to_jalali_date_str(day["datetime"]),
                **day
            })
            # generate empty days between current and next dates
            try:
                daily_chart_processed.extend(
                    self._generate_empty_days(day["datetime"], daily_chart[index + 1]["datetime"])
                )
            except IndexError:  # it's the last existing date in db
                pass

        return daily_chart_processed

    @staticmethod
    def _generate_empty_days(start_datetime: datetime.datetime, end_datetime: datetime.datetime) -> list[dict]:
        """
        generate empty days if some days have no value in db
        """
        empty_days_chart: list[dict] = []
        empty_days = (end_datetime - start_datetime).days - 1
        if empty_days:
            end_datetime = jdatetime.datetime.fromgregorian(datetime=end_datetime)
            next_empty_day = end_datetime + jdatetime.timedelta(days=1)
            for days in range(empty_days):
                empty_days_chart.append({
                    "datetime": next_empty_day.togregorian(),
                    "key": next_empty_day.strftime(TRANSACTION_DAILY_CHART_KEY_FORMAT),
                    "totalCount": 0,
                    "totalAmount": 0,
                })
                next_empty_day += jdatetime.timedelta(days=1)
        return empty_days_chart

    @staticmethod
    def _get_weekly_chart_raw(daily_chart: list[dict]) -> list[dict]:
        weekly_chart = {}
        for day in daily_chart:
            jalali_key = jdatetime.datetime.fromgregorian(datetime=day["datetime"])
            year = jalali_key.year
            week = int(jalali_key.strftime("%W"))

            if year not in weekly_chart:
                weekly_chart[year] = {}
            if week not in weekly_chart[year]:
                weekly_chart[year][week] = {"totalCount": 0, "totalAmount": 0}
            weekly_chart[year][week]["totalCount"] += day["totalCount"]
            weekly_chart[year][week]["totalAmount"] += day["totalAmount"]

        weekly_chart_processed: list[dict] = []
        existing_years = list(weekly_chart.keys())
        first_year = existing_years[0]
        first_week = list(weekly_chart[first_year].keys())[0]
        last_year = existing_years[-1]
        last_week = list(weekly_chart[last_year].keys())[-1]

        # generate empty weeks and serialize data
        for year in range(first_year, last_year + 1):
            start_week = 1 if year != first_year else first_week
            end_week = 53 if year != last_year else last_week
            for week in range(start_week, end_week + 1):
                try:
                    total_count = weekly_chart[year][week]["totalCount"]
                    total_amount = weekly_chart[year][week]["totalAmount"]
                except KeyError:
                    total_count = 0
                    total_amount = 0
                weekly_chart_processed.append({
                    "key": f"هفته {week} سال {year}",
                    "year": year,
                    "week": week,
                    "totalCount": total_count,
                    "totalAmount": total_amount,
                })
        return weekly_chart_processed

    @staticmethod
    def _get_monthly_chart_raw(daily_chart: list[dict]) -> list[dict]:
        monthly_chart = {}
        for day in daily_chart:
            jalali_key = jdatetime.datetime.fromgregorian(datetime=day["datetime"])
            year = jalali_key.year
            month = jalali_key.month

            if year not in monthly_chart:
                monthly_chart[year] = {}
            if month not in monthly_chart[year]:
                monthly_chart[year][month] = {"totalCount": 0, "totalAmount": 0}
            monthly_chart[year][month]["totalCount"] += day["totalCount"]
            monthly_chart[year][month]["totalAmount"] += day["totalAmount"]

        monthly_chart_processed: list[dict] = []
        existing_years = list(monthly_chart.keys())
        first_year = existing_years[0]
        first_month = list(monthly_chart[first_year].keys())[0]
        last_year = existing_years[-1]
        last_month = list(monthly_chart[last_year].keys())[-1]

        # generate empty months and serialize data
        for year in range(first_year, last_year + 1):
            start_month = 1 if year != first_year else first_month
            end_month = 12 if year != last_year else last_month
            for month in range(start_month, end_month + 1):
                try:
                    total_count = monthly_chart[year][month]["totalCount"]
                    total_amount = monthly_chart[year][month]["totalAmount"]
                except KeyError:
                    total_count = 0
                    total_amount = 0
                monthly_chart_processed.append({
                    "key": f"{number_to_jalali_month_name(month)} {year}",
                    "year": year,
                    "month": month,
                    "totalCount": total_count,
                    "totalAmount": total_amount,
                })

        return monthly_chart_processed
