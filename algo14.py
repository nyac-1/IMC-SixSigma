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

        assets = ["AMETHYSTS", "STARFRUIT"]

        if state.traderData and state.traderData != "Init":
            trader_data = jsonpickle.decode(state.traderData)
        else:
            trader_data = {}
            for asset in assets:
                trader_data[asset] = {"depth":[], "n":0}


        result = {}
        conversions = 0
        traderData = "Init"

        
        limits = {"AMETHYSTS": 20, "STARFRUIT": 30}
        levels = {"AMETHYSTS": 10000, "STARFRUIT": 4980}
        
        for product in state.order_depths:
            order_depth = state.order_depths[product]
            max_quantities = self.tradable_quantity(state.position.get(product, 0), limits.get(product))
            quantity_buy = min(10,max_quantities.get("buy"))
            quantity_sell = min(10,max_quantities.get("sell"))

            if quantity_buy != 0: # Will trade if we can take a position
                orders = self.limit_order(product, levels[product] - 1, quantity_buy, "buy")
            elif quantity_sell != 0:
                orders = self.limit_order(product, levels[product] + 1, quantity_sell, "sell")

            result[product] = orders
            # Example for how the trader state would look like
            # {'AMETHYSTS': {'depth': [[{'timestamp': 80500, 'bids': {'9996': 1, '9995': 21}, 'asks': {'9998': -1, '10004': -1, '10005': -21}}], [{'timestamp': 80600, 'bids': {'9996': 1, '9995': 30}, 'asks': {'10004': -1, '10005': -30}}], [{'timestamp': 80700, 'bids': {9998: 3, 9996: 2, 9995: 22}, 'asks': {10004: -2, 10005: -22}}]], 'n': 3}, 'STARFRUIT': {'depth': [[{'timestamp': 80500, 'bids': {'5046': 22}, 'asks': {'5047': -2, '5052': -1, '5053': -21}}], [{'timestamp': 80600, 'bids': {'5046': 31}, 'asks': {'5051': -2, '5053': -31}}], [{'timestamp': 80700, 'bids': {5046: 24}, 'asks': {5052: -2, 5053: -22}}]], 'n': 3}}
            if trader_data[product]["n"] < 30:
                trader_data[product]["n"]+=1
            else:
                trader_data[product]['depth'].pop(0)


            asks = self.convert_dict_to_float(collections.OrderedDict(sorted(order_depth.sell_orders.items())))
            bids = self.convert_dict_to_float(collections.OrderedDict(sorted(order_depth.buy_orders.items(), reverse=True)))

            mid_price = self.calculate_mid_price(bids, asks)

            vwap_asks = self.volume_weighted_average(asks)
            vwap_bids = self.volume_weighted_average(bids)
                
            trader_data[product]['depth'].append([{"timestamp": state.timestamp,
                                                       "bids": bids,
                                                       "asks": asks,
                                                       "midprice": mid_price,
                                                       "vwap_asks": vwap_asks,
                                                       "vwap_bids": vwap_bids}])
            
        print(trader_data)
        traderData = jsonpickle.encode(trader_data)

        return result, conversions, traderData

    def limit_order(self, product, price, quantity, side):
        orders = []
        if side == "buy":
            orders += [Order(product, price, quantity)]
        elif side == "sell":
            orders += [Order(product, price, -1*quantity)]
        return orders

    def tradable_quantity(self, current_position: int, position_limit: int) -> dict:
        position_limit = abs(position_limit)
        if current_position >= 0:
            max_buy = position_limit - current_position
            max_sell = current_position + position_limit
        else:
            max_buy = abs(current_position) + position_limit
            max_sell = position_limit - abs(current_position)
        return {"buy": max_buy, "sell": max_sell}
    
    def calculate_mid_price(self, bids, asks):
        if not bids or not asks:
            return np.nan
        return (list(bids.keys())[0] + list(asks.keys())[0]) / 2
    
    def volume_weighted_average(self, data):
        total_volume = sum(data.values())
        weighted_sum = sum(float(price) * volume for price, volume in data.items())
        if total_volume == 0:
            return np.nan
        return weighted_sum / total_volume
    
    def convert_dict_to_float(self, input_dict):
        return {float(key): float(value) for key, value in input_dict.items()}