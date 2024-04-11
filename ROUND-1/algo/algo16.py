import random
from datamodel import Order, TradingState
from typing import List
import collections 
import jsonpickle
import numpy as np

# Quantities are always positive. Only when the order is placed we look at their sign which tells us if it's a long/short position
# Bid/Ask are terms used for orders we get from the market
# Buy/Sell are terms used for OUR actions (Market making)
#   Buy is associated with the market's ask
#   Sell is associated with the market's bid
#   Exception: order_depth.sell_orders // order_depth.buy_orders
#                   ask orders        //         buy orders

# Order dynamics:
#   So when we place a buy order Order(AMETHYSTS, 9998, 5). Essentially we would match with 5 qty (if it exits) of AMETHYSTS UNTIL the price of 9998
#   For example: if we have {9996:1,9997:2,9998:7,10000:22} we would fill {9996:1,9997:2,9998:2}.
#   If the depth looked like this {9996:1,9997:2,10000:22} we would fill {9996:1,9997:2}

class Trader:

    def run(self, state: TradingState):
        result = {}
        conversions = 0

        if state.traderData:
            trader_data = jsonpickle.decode(state.traderData)
        else:
            trader_data = self.data_init()

        assets = ["AMETHYSTS", "STARFRUIT"]
        limits = {"AMETHYSTS": 20, "STARFRUIT": 20}
        levels = {"AMETHYSTS": 10000, "STARFRUIT": 5050}
        
        
        for product in state.order_depths:
            orders = []
            order_depth = state.order_depths[product]
            asks = self.convert_dict_to_float(collections.OrderedDict(sorted(order_depth.sell_orders.items())))
            bids = self.convert_dict_to_float(collections.OrderedDict(sorted(order_depth.buy_orders.items(), reverse=True)))

            max_quantities = self.tradable_quantity(state.position.get(product, 0), limits.get(product))

            
            if product == "AMETHYSTS":
                orders = self.trade_amethysts(product, max_quantities, trader_data)
    
            result[product] = orders



            # Collect Data
            if trader_data[product]["window"] < 120:
                trader_data[product]["window"]+=1
            else:
                trader_data[product]['depth'].pop(0)
                trader_data[product]['mid_prices'].pop(0)

            
            mid_price = self.calculate_mid_price(bids, asks)

            window_sizes = [30, 60]
            for window_size in window_sizes:
                mean_key = f"mean_{window_size}"
                sd_key = f"sd_{window_size}"
                if trader_data[product]["window"] >= window_size:
                    window_prices = trader_data[product]['mid_prices'][-window_size:] 
                    if np.isnan(trader_data[product][mean_key]):
                        trader_data[product][mean_key] = np.mean(window_prices)
                        trader_data[product][sd_key] = np.std(window_prices, ddof=1)
                    else:
                        adjustment_factor = float(mid_price / window_size) - float(trader_data[product]['mid_prices'][-window_size] / window_size)
                        trader_data[product][mean_key] += adjustment_factor
                        trader_data[product][sd_key] = np.std(window_prices, ddof=1)

            trader_data[product]['mid_prices'].append(mid_price)
            trader_data[product]['depth'].append([{"timestamp": state.timestamp,
                                                       "bids": bids,
                                                       "asks": asks,
                                                       "midprice": mid_price}])

        traderData = jsonpickle.encode(trader_data)
        return result, conversions, traderData

    def limit_order(self, product, price, quantity, side):
        return [Order(product, price, quantity if side == "buy" else -quantity)]

    def tradable_quantity(self, current_position: int, position_limit: int) -> dict:
        position_limit = abs(position_limit)
        if current_position >= 0:
            max_buy = position_limit - current_position
            max_sell = current_position + position_limit
        else:
            max_buy = abs(current_position) + position_limit
            max_sell = position_limit - abs(current_position)
        return {"buy": max_buy, "sell": max_sell}
    
    def data_init(self):
        trader_data = {}
        trader_data['AMETHYSTS'] = {"depth": [], "window": 0, "mid_prices":[],"mean_30": np.nan, "mean_60": np.nan, "kill": False}
        trader_data['STARFRUIT'] = {"depth": [], "window": 0, "mid_prices":[],"mean_30": np.nan, "mean_60": np.nan, "kill": False}
        return trader_data

    def convert_dict_to_float(self, input_dict):
        return {float(key): float(value) for key, value in input_dict.items()}
    
    def calculate_mid_price(self, bids, asks):
        if not bids or not asks:
            return np.nan
        return (list(bids.keys())[0] + list(asks.keys())[0]) / 2
    
    def trade_amethysts(self, product, max_quantities, trader_data):
        orders = []
        quantity_buy = max_quantities.get("buy")
        quantity_sell = max_quantities.get("sell")

        if trader_data[product]['window'] <= 60:
            if quantity_buy != 0:
                orders = self.limit_order(product, 10000 - 1, quantity_buy, "buy")
            elif quantity_sell != 0:
                orders = self.limit_order(product, 10000 + 1, quantity_sell, "sell")
            return orders

        if quantity_buy != 0:
            orders += self.limit_order(product, int(trader_data[product]["mean_60"] - 1 * trader_data[product]["sd_30"]), quantity_buy, "buy")
        if quantity_sell != 0:
            orders += self.limit_order(product, int(trader_data[product]["mean_60"] + 1 * trader_data[product]["sd_30"]), quantity_sell, "sell")
        return orders
