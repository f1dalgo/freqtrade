
# --- Do not remove these libs ---
from freqtrade.strategy import IStrategy
from typing import Dict, List
from functools import reduce
from pandas import DataFrame
# --------------------------------

import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib
from freqtrade.strategy import IStrategy
from freqtrade.strategy import IntParameter
from freqtrade.strategy import CategoricalParameter
from pandas import DataFrame


class Strategy0011(IStrategy):
    """
    Strategy 001
    author@: Gerald Lonlas
    github@: https://github.com/freqtrade/freqtrade-strategies

    How to use it?
    > python3 ./freqtrade/main.py -s Strategy001
    """

    INTERFACE_VERSION: int = 3

    # Minimal ROI designed for the strategy.
    # This attribute will be overridden if the config file contains "minimal_roi"
    # ROI table:
     # ROI table:
    minimal_roi = {
        "0": 0.763,
        "10116": 0.422,
        "13357": 0.144,
        "18302": 0
    }





    # Optimal stoploss designed for the strategy
    # This attribute will be overridden if the config file contains "stoploss"
    # Stoploss:
    stoploss = -0.343

    

    # Optimal timeframe for the strategy
    timeframe = '1d'

   # Trailing stop:
    trailing_stop = True
    trailing_stop_positive = 0.011
    trailing_stop_positive_offset = 0.078
    trailing_only_offset_is_reached = True



    # run "populate_indicators" only for new candle
    process_only_new_candles = False

    # Experimental settings (configuration will overide these if set)
    use_exit_signal = True
    exit_profit_only = False
    ignore_roi_if_entry_signal = True

    # Optional order type mapping
    order_types = {
        'entry': 'limit',
        'exit': 'limit',
        'stoploss': 'market',
        'stoploss_on_exchange': False
    }
   # buy_volumeAVG = IntParameter(low=50, high=300, default=70, space='buy', optimize=True)
    rsi_buy = IntParameter(low=1, high=100, default=51, space='buy', optimize=True)
    rsi_sell = IntParameter(low=1, high=100, default=49, space='sell', optimize=True)
    ema9_buy = IntParameter(low=1, high=100, default=9, space='buy', optimize=True)

    buy_params = {
        
       # 'buy_volumeAVG': 150,
        #'atr_period': 14,
        #'atr_multiplier': 2,
        "rsi_buy": 51,
        
        'ema9_buy': 9

    }
    sell_params = {        
       
        "rsi_sell": 50,
        
    }

    def informative_pairs(self):
        """
        Define additional, informative pair/interval combinations to be cached from the exchange.
        These pair/interval combinations are non-tradeable, unless they are part
        of the whitelist as well.
        For more information, please consult the documentation
        :return: List of tuples in the format (pair, interval)
            Sample: return [("ETH/USDT", "5m"),
                            ("BTC/USDT", "15m"),
                            ]
        """
        return []
    
    #buy_adx = IntParameter(20, 30, default=25)

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Adds several different TA indicators to the given DataFrame

        Performance Note: For the best performance be frugal on the number of indicators
        you are using. Let uncomment only the indicator you are using in your strategies
        or your hyperopt configuration, otherwise you will waste your memory and CPU usage.
        """

        dataframe['ema8'] = ta.EMA(dataframe, timeperiod=3)
        dataframe['ema9'] = ta.EMA(dataframe, timeperiod=9)
      #  dataframe['ema21'] = ta.EMA(dataframe, timeperiod=100)
       # dataframe['adx'] = ta.ADX(dataframe)
         # RSI
        dataframe['rsi'] = ta.RSI(dataframe)

        heikinashi = qtpylib.heikinashi(dataframe)
        dataframe['ha_open'] = heikinashi['open']
        dataframe['ha_close'] = heikinashi['close']

         # Calculate the ATR
        #dataframe['atr'] = ta.ATR(dataframe, timeperiod=self.buy_params['atr_period'])
       # dataframe['upper_band'] = dataframe['ema9'] + (self.buy_params['atr_multiplier'] * dataframe['atr'])
        #dataframe['lower_band'] = dataframe['ema9'] - (self.buy_params['atr_multiplier'] * dataframe['atr'])

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Based on TA indicators, populates the buy signal for the given dataframe
        :param dataframe: DataFrame
        :return: DataFrame with buy column
        """
        dataframe.loc[
            (
               # (dataframe['rsi'] > self.rsi_buy.value) &
               # (dataframe['volume'] > dataframe['volume'].rolling(self.buy_volumeAVG.value).mean() * 4) &
                (dataframe['ha_close'] > dataframe['ema9']) &
                # (dataframe['ha_close'] > dataframe['ema21']) &
                (dataframe['ha_open'] < dataframe['ha_close']) 
                #(dataframe['adx'] > self.buy_adx.value) # green bar
            ),           
            
            'buy'] = 1


        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Based on TA indicators, populates the sell signal for the given dataframe
        :param dataframe: DataFrame
        :return: DataFrame with buy column
        """
        dataframe.loc[
            (
            
               # (dataframe['rsi'] < self.rsi_sell.value) &
                (dataframe['ha_close'] < dataframe['ema9']) &
                #(dataframe['ha_close'] < dataframe['ema9']) &
                (dataframe['ha_open'] > dataframe['ha_close'])   # red bar
            ),
            'sell'] = 1
        
        return dataframe
