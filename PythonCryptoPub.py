import time
import pyupbit
import datetime
import numpy as np

access = 'your access code'
secret = 'your secret code'

def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(ticker=ticker)["orderbook_units"][0]["ask_price"]

def update_k(update_range):
    def get_ror(k):
        df['range'] = (df['high'] - df['low']) * k
        df['target'] = df['open'] + df['range'].shift(1)

        df['ror'] = np.where(df['high'] > df['target'],
                            df['close'] / df['target'],
                            1)

        ror = df['ror'].cumprod()[-2]
        return ror

    df = pyupbit.get_ohlcv("KRW-BTC", interval="day", count=update_range)
    best_ror=0
    best_k=0
    ror=0
    for k in np.arange(0.01, 1.01, 0.01):
        ror=get_ror(k)
        if ror > best_ror:
            best_ror=ror
            best_k=k
    print('Best ror: ', best_ror,'\n')
    print('Best K: ', best_k)
    return best_k

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")

# 자동매매 시작
k=update_k(7)
print(get_balance)

while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-BTC")
        end_time = start_time + datetime.timedelta(days=1)

        if start_time < now < end_time - datetime.timedelta(seconds=10):
            target_price = get_target_price("KRW-BTC", k)
            current_price = get_current_price("KRW-BTC")
            if target_price < current_price:
                krw = get_balance("KRW")
                if krw > 5000:
                    upbit.buy_market_order("KRW-BTC", krw*0.9995)
        

        else:
            btc = get_balance("BTC")
            if btc > 0.00008:
                upbit.sell_market_order("KRW-BTC", btc*0.9995)
            k= update_k(7)
        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)