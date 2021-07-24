"""jpholidayのお試し記録
やること
* jpholidayで休日を出す
* カスタムの休日を出せるようにする
* pandas.datatimeindex(https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DatetimeIndex.html)に変換できるようにする
"""
import jpholiday
from datetime import date, timedelta, timezone

from pandas import DatetimeIndex

# jpholidayで休日を出す
def holidays():
    # 指定範囲の祝日を取得
    result = jpholiday.between(date(2021, 7, 1), date(2021, 10, 1))
    print("------result------")
    print(result)
    print(type(result))
    for r in result:
        print(type(r))
        print(r)


def customed_holidays():
    # 東証の休日を追加
    class TSEHoliday(jpholiday.OriginalHoliday):
        def _is_holiday(self, date):
            # 年末年始は休み
            month = date.month
            day = date.day
            if month == 12 and day in [31]:
                return True
            elif month == 1 and day in [1, 2, 3]:
                return True
            # 土日は休み
            if date.weekday() >= 5:
                return True
            return False

        def _is_holiday_name(self, date):
            # 年末年始は休み
            month = date.month
            day = date.day
            if month == 12 and day in [31]:
                return "年末年始休暇"
            elif month == 1 and day in [1, 2, 3]:
                return "年末年始休暇"
            # 土日は休み
            if date.weekday() == 5:
                return "土曜日"
            if date.weekday() == 6:
                return "日曜日"

    results = jpholiday.year_holidays(2021)
    print(results)
    print(f"2021年の休日は{len(results)}間")

    for y in range(2000, 2030):
        results = jpholiday.year_holidays(y)
        print(f"{y}年の休日は{len(results)}間")


def jpholidays_to_datetimeindex():
    class TSEHoliday(jpholiday.OriginalHoliday):
        def _is_holiday(self, date):
            # 年末年始は休み
            month = date.month
            day = date.day
            if month == 12 and day in [31]:
                return True
            elif month == 1 and day in [1, 2, 3]:
                return True
            # 土日は休み
            if date.weekday() >= 5:
                return True
            return False

        def _is_holiday_name(self, date):
            # 年末年始は休み
            month = date.month
            day = date.day
            if month == 12 and day in [31]:
                return "年末年始休暇"
            elif month == 1 and day in [1, 2, 3]:
                return "年末年始休暇"
            # 土日は休み
            if date.weekday() == 5:
                return "土曜日"
            if date.weekday() == 6:
                return "日曜日"

    results = jpholiday.year_holidays(2021)
    JST = timezone(timedelta(hours=+9), "JST")

    index = DatetimeIndex([day for day, _ in results], tz=JST)
    print(index)


def main():
    # holidays()
    # customed_holidays()
    jpholidays_to_datetimeindex()


if __name__ == "__main__":
    main()
