import jdatetime

from apps.transactions.constants import TRANSACTION_DAILY_CHART_KEY_FORMAT


def gregorian_datetime_to_jalali_date_str(gregorian_datetime):
    return jdatetime.datetime.fromgregorian(datetime=gregorian_datetime).strftime(TRANSACTION_DAILY_CHART_KEY_FORMAT)


def number_to_jalali_month_name(num):
    return jdatetime.date.j_months_fa[num - 1]
