# --- Do not remove these libs ---
import numpy as np  # noqa
import pandas as pd  # noqa
from pandas import DataFrame, Series
from freqtrade.strategy.interface import IStrategy
from freqtrade.strategy.hyper import IntParameter
# --------------------------------
# Add your lib to import here
import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib
from datetime import datetime
from freqtrade.persistence import Trade
from freqtrade.strategy.hyper import DecimalParameter, IntParameter

import logging
logger = logging.getLogger(__name__)
###Hyperopt this spaces buy roi stoploss

class ADX_RSI(IStrategy):
    buy_rsi = IntParameter(10, 30, default=29, space="buy") 
    buy_adx = IntParameter(25, 40, default=39, space="buy")
    #sell_rsi = IntParameter(70, 95, default=70, space="sell")
      
   
    #105/2000:   1244 trades. 741/494/9 Wins/Draws/Losses. Avg profit   0.68%. Median profit   0.22%. ((225 days))
    #Total profit  12492.51785256 USD ( 1249.25%). Avg duration 7:42:00 min. Objective: -22.71919

    # ROI table:
    minimal_roi = {
        "0": 0.154,
        "11": 0.08,
        "34": 0.026,
        "80": 0
    }

    # Stoploss:
    stoploss = -0.346
   
    # Trailing stop:
    trailing_stop = False
    trailing_stop_positive = 0.011
    trailing_stop_positive_offset = 0.085
    trailing_only_offset_is_reached = True

    # Optimal timeframe for the strategy 
    timeframe = '5m'
    
    # Experimental settings (configuration will overide these if set)
    use_sell_signal = True
    sell_profit_only = True
    sell_profit_offset = 0.0
    ignore_roi_if_buy_signal = False
    
    # Optional order type mapping
    order_types = {
        'buy': 'market',
        'sell': 'market',
        'stoploss': 'market',
        'stoploss_on_exchange': False
    }

    # run "populate_indicators" only for new candle
    process_only_new_candles = False
    
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14) # overbought and oversold conditions
        dataframe['adx'] = ta.ADX(dataframe, timeperiod=14) #trend detection
        #dataframe['sma12'] = ta.SMA(dataframe, timeperiod=12) #guard
        #dataframe['sma50'] = ta.SMA(dataframe, timeperiod=50) #guard
    
        return dataframe

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
              
        dataframe.loc[
            (
                ((dataframe["rsi"] <= self.buy_rsi.value)) & #oversold condition
                ((dataframe["adx"] >= self.buy_adx.value)) & #verify trend
                #((dataframe["sma12"]) < (dataframe["sma50"])) & #guard
                (dataframe['volume'] > 0) # volume above zero
            )
        ,'buy'] = 1
        return dataframe

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        #disabled
        dataframe.loc[
            (
                #((dataframe["rsi"] >= self.sell_rsi.value)) & #overbought condition
                #((dataframe["adx"] >= 25)) & #verify trend
                #((dataframe["sma12"]) > (dataframe["sma50"])) & #guard
                (dataframe['volume'] > 0) # volume above zero
            )
        ,'sell'] = 0
        return dataframe
