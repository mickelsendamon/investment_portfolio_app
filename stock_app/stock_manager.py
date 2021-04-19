import datetime
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.fundamentaldata import FundamentalData
from django.core.exceptions import ObjectDoesNotExist
from .models import *

call_api = 'HEVP9JW30KNJFNM1'


def connect_time_series_api(key=call_api):
    api_connect = TimeSeries(key)
    return api_connect


def connect_fundamental_data_api(key=call_api):
    api_connect = FundamentalData(key)
    return api_connect


def get_stock_by_ticker(ticker):
    if Stock.objects.filter(ticker=ticker):
        return Stock.objects.get(ticker=ticker)
    else:
        return add_new_stock_data(ticker)


def get_stock_day_by_stock(this_stock, this_date):
    if StockDay.objects.filter(stock=this_stock, date=this_date):
        return StockDay.objects.get(stock=this_stock, date=this_date)
    else:
        return add_new_stock_day(this_stock, this_date)


def add_new_stock_day(this_stock, this_date):
    return StockDay.objects.create(
        stock=this_stock, date=this_date, day_open=None, day_close=None, day_high=None, day_low=None
    )


def get_oms_open_and_close(day_stock):
    close_oms = None
    open_oms = None
    for oms in day_stock.time_series_days.all():
        if close_oms is None:
            close_oms = oms
        else:
            if oms.time > close_oms.time:
                close_oms = oms
        if open_oms is None:
            open_oms = oms
        else:
            if oms.time < open_oms.time:
                open_oms = oms
    day_stock.day_open = open_oms.price
    day_stock.day_close = close_oms.price


def add_new_stock_data(ticker):
    api = connect_fundamental_data_api()
    company_data, meta_data = api.get_company_overview(ticker)
    description = company_data['Description']
    yr_high = company_data['52WeekHigh']
    yr_low = company_data['52WeekLow']
    fifty_moving_avg = company_data['50DayMovingAverage']
    two_hun_moving_avg = company_data['200DayMovingAverage']
    this_stock = Stock.objects.create(
        ticker=ticker, after_ticker='', price=0.0, description=description, fifty_two_week_high=yr_high,
        fifty_two_week_low=yr_low, fifty_day_moving_average=fifty_moving_avg,
        two_hundred_day_moving_average=two_hun_moving_avg
    )
    # todo make api call to get stock price data
    api = connect_time_series_api()
    time_data, results = api.get_intraday(ticker, '1min', outputsize='full')
    stock_days = []
    for day in time_data:
        date_str = day[:10]
        date_datetime = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        this_date = datetime.date(date_datetime.year, date_datetime.month, date_datetime.day)
        data = time_data[day]
        stock_day = get_stock_day_by_stock(this_stock, this_date)
        stock_days.append(stock_day)
        oms = OneMinuteSeries.objects.create(time=day, price=data['4. close'], stock_day=stock_day)
        if stock_day.day_high is None:
            stock_day.day_high = oms.price
        else:
            if int(oms.price) > int(stock_day.day_high):
                stock_day.day_high = oms.price
        if stock_day.day_low is None:
            stock_day.day_low = oms.price
        else:
            if int(oms.price) < int(stock_day.day_low):
                stock_day.day_low = oms.price
    closest = None
    closest_day = None
    today = datetime.date(
        datetime.datetime.today().year, datetime.datetime.today().month, datetime.datetime.today().day
    )
    for stock_day in stock_days:
        get_oms_open_and_close(stock_day)
        if closest is None:
            closest = stock_day
            closest_day = stock_day.date
        else:
            if today - stock_day.date < today - closest_day:
                closest = stock_day
                closest_day = stock_day.date
    print(closest_day, ' ', vars(closest))
    this_stock.price = closest.day_close
    this_stock.save()
    return this_stock


def get_stock_daily_data(idx, av_api):
    output, meta = av_api.get_daily(symbol=idx, outputsize='full')
    return meta, output


# from stock_app.models import *
# 
# from alpha_vantage.timeseries import TimeSeries
#
# import datetime
#
# api = TimeSeries('HEVP9JW30KNJFNM1')
#
# stock_data = api.get_intraday('AAPL', '1min', outputsize='full')
#
# time_data = stock_data[0]
#
# for day in time_data:
#
#     day_data = time_data[day]
#
#     # Date used for StockDay
#     day_date = datetime.datetime.strptime(day, '%Y-%m-%d %H:%M:%S')
#
#     # GET STOCK
#     if Stock.objects.filter(ticker='IBM'):
#         stock = Stock.objects.get(ticker='IBM')
#     else:
#         stock = create_new_stock('IBM', time_data=True)
#
#     # GET STOCK DAY
#     if StockDay.objects.filter(date=day_date, stock=stock):
#         stock_day = StockDay.objects.get(ticker='IBM')
#     else:
#         ex
#     stock_day = StockDay.objects.create(date=day_date, stock=stock, day_open=0.0, day_close=0.0, day_high=0.0,
#                                         day_low=0.0)
#
# # CREATE OMS
# oms_one = OneMinuteSeries.objects.create(time=day_date, price=day_data['4. close'], stock_day=stock_day)
