import random
from datamodel import Order, TradingState
from typing import List
from collections import defaultdict, OrderedDict

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
        traderData = "RandomTrading"

        assets = ["AMETHYSTS", "STARFRUIT"]
        limits = {"AMETHYSTS": 20, "STARFRUIT": 30}
        levels = {"AMETHYSTS": 10000, "STARFRUIT": 4900}
        
        for product in state.order_depths:
            orders = []
            order_depth = state.order_depths[product]
            max_quantities = self.tradable_quantity(state.position.get(product, 0), limits.get(product))
            quantity_buy = min(10,max_quantities.get("buy"))
            quantity_sell = min(10,max_quantities.get("sell"))


            if quantity_buy != 0: # Will trade if we can take a position
                orders += self.limit_order(order_depth, product, levels[product] - 1, quantity_buy, "buy")
            elif quantity_sell != 0:
                orders += self.limit_order(order_depth, product, levels[product] + 1, quantity_sell, "sell")

            result[product] = orders

        return result, conversions, traderData

    def limit_order(self, order_depth, product, price, quantity, side):
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