import random
from datamodel import Order, TradingState  # Ensure these are correctly defined/imported
from typing import List
import collections
import jsonpickle  # Ensure jsonpickle is installed
import numpy as np  # Ensure numpy is installed

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
        
        for product in state.order_depths:
            orders = []
            order_depth = state.order_depths[product]
            asks = self.convert_dict_to_float(collections.OrderedDict(sorted(order_depth.sell_orders.items())))
            bids = self.convert_dict_to_float(collections.OrderedDict(sorted(order_depth.buy_orders.items(), reverse=True)))

            max_quantities = self.tradable_quantity(state.position.get(product, 0), limits.get(product))

            if product == "AMETHYSTS":
                orders = self.trade_amethysts(product, max_quantities, trader_data)
            # elif product == "STARFRUIT":
            #     orders = self.trade_starfruit(product, max_quantities, trader_data, asks, bids)

            result[product] = orders

            # Collect Data
            if trader_data[product]["window"] < 120:
                trader_data[product]["window"] += 1
            else:
                trader_data[product]['depth'].pop(0)
                trader_data[product]['mid_prices'].pop(0)

            mid_price = self.calculate_mid_price(bids, asks)
            trader_data[product]['mid_prices'].append(mid_price)
            trader_data[product]['depth'].append({
                "timestamp": state.timestamp,
                "bids": bids,
                "asks": asks,
                "midprice": mid_price
            })

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
        trader_data['AMETHYSTS'] = {"depth": [], "window": 0, "mid_prices":[], "mean_30": np.nan, "mean_60": np.nan, "kill": False}
        trader_data['STARFRUIT'] = {"depth": [], "window": 0, "mid_prices":[], "mean_30": np.nan, "mean_60": np.nan, "kill": False}
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

    def trade_starfruit(self, product, max_quantities, trader_data, asks, bids):
        orders = []
        # quantity_buy = max_quantities.get("buy")
        # quantity_sell = max_quantities.get("sell")
        # window = trader_data[product]['window']

        # if window <= 60:
        #     return orders  # Don't trade for the first 60 days

        # mean_30 = trader_data[product]['mean_30']
        # mean_60 = trader_data[product]['mean_60']

        # if mean_30 > mean_60 and quantity_buy > 0:
        #     max_ask_qty_price = min(asks, key=asks.get) if asks else None
        #     if max_ask_qty_price is not None:
        #         orders += self.limit_order(product, max_ask_qty_price, quantity_buy, "buy")
        # elif mean_30 < mean_60 and quantity_sell > 0:
        #     max_bid_qty_price = max(bids, key=bids.get) if bids else None
        #     if max_bid_qty_price is not None:
        #         orders += self.limit_order(product, max_bid_qty_price, quantity_sell, "sell")

        return orders
