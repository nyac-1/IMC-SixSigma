import random
from datamodel import Order, TradingState
from typing import List
from collections import defaultdict, OrderedDict

class Trader:

    def run(self, state: TradingState):
        result = {}
        conversions = 0
        traderData = "RandomTrading"

        limits = {"AMETHYSTS": 20, "STARFRUIT": 30}
        levels = {"AMETHYSTS": 10000, "STARFRUIT": 4900}
        

        for product in state.order_depths:
            orders = []
            order_depth = state.order_depths[product]
            max_quantities = self.tradable_quantity(state.position.get(product, 0), limits.get(product))
            quantity_buy = min(10,max_quantities.get("buy"))
            quantity_sell = min(10,max_quantities.get("sell"))


            if quantity_buy != 0:
                orders += self.limit_order(order_depth, product, 9999, quantity_buy, "buy")
            elif quantity_sell != 0:
                orders += self.limit_order(order_depth, product, 10001, quantity_sell, "sell")

            result[product] = orders

        return result, conversions, traderData

    def limit_order(self, order_depth, product, price, quantity, side):
        orders = []

        if side == "buy":
            levels = len(order_depth.sell_orders.keys())
            orders = OrderedDict(sorted(order_depth.sell_orders.items()))
            if levels > 0 and len(orders) > 0:
                orders = [Order(product, orders[0], quantity)]



            pass
        elif side == "sell":
            levels = len(order_depth.buy_orders.keys())
            orders = OrderedDict(sorted(order_depth.buy_orders.items(), reverse = True))

            pass

        # Decide randomly to buy or sell (p=0.5 for each)
        if random.random() < 0.5:
            # Attempt to buy
            if len(order_depth.sell_orders) > 1:
                sorted_asks = sorted(order_depth.sell_orders.keys())
                orders += [Order(product, sorted_asks[0], quantity),
                           Order(product, sorted_asks[1], quantity)]
        else:
            # Attempt to sell
            if len(order_depth.buy_orders) > 1:
                sorted_bids = sorted(order_depth.buy_orders.keys(), reverse=True)
                orders += [Order(product, sorted_bids[0], -quantity),
                           Order(product, sorted_bids[1], -quantity)]
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
