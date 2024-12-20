import datetime
from datetime import timedelta

import jdatetime

from apps.transactions.constants import TRANSACTION_DAILY_CHART_KEY_FORMAT
from apps.transactions.models import TransactionModel, TransactionSummaryModel
from apps.utils.general import gregorian_datetime_to_jalali_date_str, number_to_jalali_month_name


class TransactionService:
    def get_chart_raw(self, chart_type: str, mode: str, merchant_id: str | None) -> list[dict]:
        daily_chart = TransactionModel.group_by_type(chart_type, merchant_id)
        if not daily_chart:
            return []
        return getattr(self, f"_get_{mode}_chart_raw")(daily_chart)

    def _get_daily_chart_raw(self, daily_chart: list[dict]) -> list[dict]:
        daily_chart_processed = []
        for index, day in enumerate(daily_chart):
            daily_chart_processed.append({
                "key": gregorian_datetime_to_jalali_date_str(day["datetime"]),
                "value": day["value"]
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
            next_empty_day = end_datetime + timedelta(days=1)
            for days in range(empty_days):
                empty_days_chart.append({
                    "key": next_empty_day.strftime(TRANSACTION_DAILY_CHART_KEY_FORMAT),
                    "value": 0,
                })
                next_empty_day += timedelta(days=1)
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
            weekly_chart[year][week] = weekly_chart[year].get(week, 0) + day["value"]

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
                    value = weekly_chart[year][week]
                except KeyError:
                    value = 0
                weekly_chart_processed.append({
                    "key": f"هفته {week} سال {year}",
                    "value": value
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
            monthly_chart[year][month] = monthly_chart[year].get(month, 0) + day["value"]

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
                    value = monthly_chart[year][month]
                except KeyError:
                    value = 0
                monthly_chart_processed.append({
                    "key": f"{number_to_jalali_month_name(month)} {year}",
                    "value": value
                })

        return monthly_chart_processed

    @staticmethod
    def get_chart(chart_type: str, mode: str, merchant_id: str | None):
        return TransactionSummaryModel.get_chart(chart_type, mode, merchant_id)
