from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import IntegrityError
import bcrypt
from .stock_manager import *


# Create your views here.
def index(request):
    return render(request, 'index.html')


def register(request):
    return render(request, 'register.html')


def sign_up(request):
    if request.method == 'POST':
        errors = User.objects.basic_validation(request.POST)
        if errors:
            for error in errors:
                messages.error(request, errors[error])
            return render(request, 'register.html')
        else:
            user_values = {}
            user_fields = [
                'first_name', 'last_name', 'email_address',
                'password', 'confirm_password'
            ]
            for field in user_fields:
                user_values[field] = request.POST[field]
            try:
                user = User.objects.create(
                    first_name=user_values[user_fields[0]], last_name=user_values[user_fields[1]],
                    email_address=user_values[user_fields[2]],
                    password=bcrypt.hashpw(user_values[user_fields[3]].encode(), bcrypt.gensalt()).decode()
                )
                Portfolio.objects.create(user=user)
                request.session['userid'] = user.id
                return redirect('/portfolio')
            except IntegrityError:
                messages.error(request, 'That email address is already registered')
                return redirect('/sign_in')
    return redirect('/register')


def log_on(request):
    if request.method == 'POST':
        try:
            user = User.objects.get(email_address=request.POST['email_address'])
            if bcrypt.checkpw(request.POST['password'].encode(), user.password.encode()):
                request.session['userid'] = user.id
                return redirect('/portfolio/')
            else:
                messages.error(request, "Invalid Email Address and Password combination")
                return redirect('/sign_in/')
        except:
            if not User.objects.filter(email_address=request.POST['email_address']):
                messages.error(request, "Email Address does not exist")
            else:
                messages.error(request, "Login failed")
            return redirect('/sign_in')
    return redirect('/sign_in/')


def sign_in(request):
    request.session.flush()
    return render(request, 'sign_in.html')


def logout(request):
    request.session.flush()
    return redirect('/')


def portfolio(request):
    if 'userid' in request.session:
        user = User.objects.get(id=request.session['userid'])
        owned_stocks = []
        for owned in user.owned_stocks.all():
            price = owned.stock.price
            shares = owned.shares
            if owned.sell_date_time is None:
                value = shares * price
                change = value - (shares * owned.purchase_price)
            else:
                value = owned.sell_price * shares
                change = (owned.purchase_price * shares) - (owned.sell_price * shares)
            owned_stocks.append({'ticker': owned.stock.ticker, 'price': price, 'shares': shares, 'change': change})
        # for o_stock in user.owned_stocks.all():
        #     if o_stock.sell_price is not None:
        #         value += round(o_stock.stock.price * o_stock.shares, 4)
        #         cost += o_stock.purchase_price * o_stock.shares
        ptfl = {
            'value': 0,
            'growth': 0,
            'owned_stocks': owned_stocks,
        }
        context = {
            'portfolio': ptfl,
        }
        return render(request, 'portfolio_view.html', context)
    return redirect('/sign_in')


def create_stock(request):
    if 'userid' in request.session:
        return render(request, 'new_stock_purchase.html')
    return redirect('/sign_in')


def new_stock(request):
    if 'userid' in request.session:
        if request.method == "POST":
            user = User.objects.get(id=request.session['userid'])
            portfolio = user.portfolio
            ticker = request.POST['ticker']
            shares = request.POST['shares']
            purchase_date = datetime.datetime.strptime(request.POST['purchase_date'], '%Y-%m-%dT%H:%M')
            is_sold = request.POST['is_sold']
            if is_sold == 'Yes':
                sell_date = request.POST['sell_date']
            else:
                sell_date = None
            this_stock = get_stock_by_ticker(ticker)  # todo this function is still in progress
            day_date = datetime.date(purchase_date.year, purchase_date.month, purchase_date.day)
            if StockDay.objects.filter(stock=this_stock, date=day_date):
                stock_day = StockDay.objects.get(stock=this_stock, date=day_date)
                if OneMinuteSeries.objects.filter(stock_day=stock_day, time=purchase_date):
                    price = OneMinuteSeries.objects.get(stock_day=stock_day, time=purchase_date).price
                else:
                    # todo set error message 'Cannot get price for that time'
                    print(f'Could not find OMS by {stock_day} & {purchase_date}')
                    return redirect('/portfolio/')
            else:
                # todo set error message 'Cannot find stock day for that day'
                print(f'Could not find StockDay by {this_stock} & {day_date}')
                return redirect('/portfolio/')
            OwnedStock.objects.create(
                stock=this_stock, shares=shares, purchase_date_time=purchase_date, owner=user, purchase_price=price,
                portfolio=portfolio
            )
            return redirect('/portfolio/')
    return redirect('/sign_in')


def create_bank(request):
    if 'userid' in request.session:
        return render(request, 'new_bank.html')
    return redirect('/sign_in')


def new_bank(request):
    if 'userid' in request.session:
        if request.method == "POST":
            bank = Bank.objects.create(
                user=User.objects.get(id=request.session['user_id']),
                bank_name=request.POST['bank_name'],
                portfolio=Portfolio.objects.get(id=request.session['portfolio_id'])
            )
            return redirect(f'/bank/{bank.id}')
    return redirect('/sign_in')


def create_investment(request):
    if 'userid' in request.session:
        return render(request, 'new_investment.html')
    return redirect('/sign_in')


def new_investment(request):
    if 'userid' in request.session:
        if request.method == "POST":
            bank = Bank.objects.get(bank_name=request.POST['bank'])
            investment_amount = request.POST['investment_amount']
            investment_date = request.POST['investment_date']
            Investment.objects.create(bank=bank, investment_amount=investment_amount,
                                      investment_date=investment_date)
            return redirect(f'/bank/{bank.id}')
    return redirect('/sign_in')


def stock(request, ticker):
    if 'userid' in request.session:
        this_stock = Stock.objects.get(ticker=ticker)
        user = User.objects.get(id=request.session['userid'])
        context = {
            'stock': this_stock,
            'purchases': OwnedStock.objects.filter(stock=this_stock, owner=user),
        }
        return render(request, 'stock_view.html', context)
    return redirect('/sign_in')


def my_account(request):
    if 'userid' in request.session:
        user = User.objects.get(id=request.session['userid'])
        stocks = {}
        for each_stock in user.owned_stocks.all():
            ticker = each_stock.stock.ticker
            purchase_date = each_stock.purchase_date_time
            sell_date = each_stock.sell_date_time
            if sell_date is not None:
                shares = each_stock.shares
            else:
                shares = 0
            if ticker in stocks:
                this_stock = stocks[ticker]
                this_stock['purchase_dates'].append(purchase_date)
                this_stock['sell_dates'].append(sell_date)
                this_stock['shares'] += shares
            else:
                stocks[ticker] = {'purchase_dates': [purchase_date], 'sell_dates': [sell_date], 'shares': shares}
        all_stocks = []
        for each_stock in stocks:
            pur_date = None

            for date in stocks[each_stock]['purchase_dates']:
                if pur_date is not None:
                    if date > pur_date:
                        pur_date = date
                else:
                    pur_date = date
            sell_date = None
            for date in stocks[each_stock]['sell_dates']:
                if sell_date is not None:
                    if date > sell_date:
                        sell_date = date
                else:
                    sell_date = date
            all_stocks.append({
                'ticker': each_stock, 'last_purchased': pur_date, 'last_sold': sell_date,
                'shares': stocks[each_stock]['shares']
            })
        context = {
            'user': user,
            'all_banks': user.banks.all(),
            'all_stocks': all_stocks,
        }
        return render(request, 'account_view.html', context)
    return redirect('/sign_in')

# def view_portfolio(request):
#     user

# portfolio_view
#     {
#     'portfolio': {'value': '150.00', 'total_growth': '+0%', 'stocks': [
#         {'index': 'AAPL', 'price': '123.45', 'change': '+3.38%', 'value': '123.45', 'shares': '1'},
#     ]}
# }

# bank_view
# {
#     'bank': {'name': 'Wells Fargo', 'investment': '150.00', 'purchases': [
#         {'stock_index': '____', 'number_of_shares': 1, 'share_price': '150.00', 'total_investment': '150.00'}
#     ]}
# }

# stock_view
# {
#     'stock': {'stock_index': 'AAPL', 'share_price': '123.01', 'share_purchase': [
#         {'shares_purchased': '1', 'purchase_price': '123.98', 'purchase_date': '2021-03-03', 'sold_date': 'Unsold',
#          'growth': '-$0.97'}
#     ]}
# }

# account_view
# {
#     'user': {'first_name': 'Damon', 'last_name': 'Mickelsen', 'email_address': 'd@m.c'},
#     'all_banks': [{'name': 'Wells Fargo Checking', 'investment': '275', 'purchases': [
#         {'stock_index': 'VUZI', 'number_of_shares': '1', 'share_price': '19.90', 'total_investment': '19.90'},
#         {'stock_index': 'AAPL', 'number_of_shares': '1', 'share_price': '123.98', 'total_investment': '123.98'},
#         {'stock_index': 'CDXC', 'number_of_shares': '8', 'share_price': '14.06', 'total_investment': '112.48'},
#     ]}],
#     'all_stocks': [
#         {'stock_index': 'VUZI', 'last_purchase_date': '2021-03-04', 'last_sold_date': 'Unsold',
#          'currently_owned': '1'},
#         {'stock_index': 'AAPL', 'last_purchase_date': '2021-03-03', 'last_sold_date': 'Unsold',
#          'currently_owned': '1'},
#         {'stock_index': 'NOK', 'last_purchase_date': '2021-02-01', 'last_sold_date': '2021-03-03',
#          'currently_owned': '0'},
#     ]
# }
# return render(request, 'portfolio_view.html', context)
