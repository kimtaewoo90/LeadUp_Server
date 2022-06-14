# -*- coding:utf-8 -*-

import sqlite3
from flask import Flask, url_for, render_template, request, redirect, session, flash

import pandas as pd
import numpy as np
import sys
from datetime import datetime

# upbit modules
import modules.upbit as upbit

# web sockets
import upbit_websockets as ws
import asyncio
import logging
import traceback

# schedule
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
app.secret_key = "234231432423"
app.config['CoinGo_DB'] = 'db/user_db.sqlite3'

# RSI Strategy
# initial RSI

# rsi_dict = dict()
def calcRSI(market_name):
    
    rsi_dict = dict()
    
    for i in range(len(market_name)):
        candle_datas = upbit.get_candle(market_name[i], '60', 200)
        
        rsi_df = upbit.get_candle_rsi(candle_datas)
        # if i == 0:
        #     print("{0} RSI : {1}".format(market_name[i], rsi_df))
            
        rsi_dict[market_name[i]] = rsi_df
    
    return rsi_dict


def real_time_RSI(close_price_list, current_price, period=14):
    
    close_price_sr = pd.Series(close_price_list.append(current_price))
    
    U = np.where(close_price_sr.diff(1) > 0, close_price_sr.diff(1), 0)
    D = np.where(close_price_sr.diff(1) < 0, close_price_sr.diff(1), 0)
    
    AU = pd.Series(U).rolling(window=period).mean()
    AD = pd.Series(D).rolling(window=period).mean()
    
    RSI = AU / (AD + AU) * 100
    
    return RSI

# Current Price

# Balance
def available_balance():
    return upbit.get_krwbal()


# Initial set up
def init_setup():
    item_list = upbit.get_items("KRW")
    market_name = []
    market_kr_name = []
    
    for market in range(len(item_list)):
        market_name.append(item_list[market]['market'])
        market_kr_name.append(item_list[market]['korean_name'])
        
    return market_name, market_kr_name
    

# TODO: WebSocket 이랑 RSI 계산 및 주문 등은 Thread를 따로 줘야겠다.
@app.route('/')
def home():
    
    # strategy
    first_touch_30 = []
    second_touch_30 = []  # buy
    first_touch_70 = []
    second_touch_70 = []  # sell
    
    market_name, market_kr_name = init_setup()
    rsi_df = calcRSI(market_name)
    
    try_again = True
    once_in_hour = True
    
    
    try:
        # ---------------------------------------------------------------------
        # Logic Start!
        # ---------------------------------------------------------------------
        # 웹소켓 시작
        # asyncio.run(ws.main(market_name))
        
        # calculate realtime rsi during every 1 hour (60 mins candle)
        # TODO: 60분봉 마지막 price를 웹소켓을 통해 받은 현재가를 사용하여 RSI 계속 계산.
        
        while(True):
            
            # after 60 mins
            if datetime.now().minute == 0 and once_in_hour is True:
                rsi_df = calcRSI(market_name)
                try_again = True
                once_in_hour = False
            
            if datetime.now().minute == 1:
                once_in_hour = True    
            
            if try_again is True:
                try_again = False
                
                for i in range(len(market_name)):
                    rsi = rsi_df[market_name[i]].iloc[-1]["RSI"]
                    times = rsi_df[market_name[i]].iloc[-1]["candle_date_time_kst"]
                    ticker = market_name[i]
                    
                    if ticker not in first_touch_30:
                        if rsi < 30:
                            first_touch_30.append(ticker)
                            if ticker in second_touch_70:
                                second_touch_70.remove(ticker)
                                
                    elif ticker in first_touch_30:
                        if rsi > 30 and rsi < 38:
                            # 매수
                            second_touch_30.append(ticker)
                            first_touch_30.remove(ticker)
                            print("Ticker : {0}, Buy_price : {1}".format(ticker, rsi_df[ticker].iloc[-1]["close"]))
                            
                    
                    elif ticker in second_touch_30 and ticker not in first_touch_70:
                        if rsi > 70:
                            first_touch_70.append(ticker)
                            second_touch_30.remove(ticker)
                            
                    elif market_name[i] in first_touch_70:
                        if rsi < 70:
                            # 매도
                            second_touch_70.append(ticker)
                            first_touch_70.remove(ticker)
                            print("Ticker : {0}, Sell_price : {1}".format(ticker, rsi_df[ticker].iloc[-1]["close"]))
                            
                print("[{0}] : First_30 = {1}".format(times, first_touch_30))
                print("[{0}] : Second_30 = {1}".format(times, second_touch_30))
                print("[{0}] : First_70 = {1}".format(times, first_touch_70))
                print("[{0}] : Second_30 = {1}".format(times, second_touch_70))
                print("==" * 30)
                    
            
            # print(datetime.now().minute)
        
        
        
        
        
    
    except KeyboardInterrupt:
        logging.error("KeyboardInterrupt Exception 발생!")
        logging.error(traceback.format_exc())
        sys.exit(-100)
 
    except Exception:
        logging.error("Exception 발생!")
        logging.error(traceback.format_exc())
        sys.exit(-200)
    
    return render_template('index.html')
    
    

@app.route('/get_items')
def get_items():
    
    return upbit.get_items("KRW")



if __name__ == "__main__":
    
    app.run(debug=True)