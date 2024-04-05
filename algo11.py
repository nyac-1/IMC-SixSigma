import random
from datamodel import Order, TradingState
from typing import List

class Trader:

    def run(self, state: TradingState):
        result = {}
        conversions = 0
        traderData = "RandomTrading"

        limits = {"AMETHYSTS": 20, "STARFRUIT": 30}

        for product in state.order_depths:
            order_depth = state.order_depths[product]
            quantities = self.tradable_quantity(state.position.get(product, 0), limits.get(product))
            quantity_buy = quantities.get("buy")
            quantity_sell = quantities.get("sell")

            # Now, use execute_trades to append orders to the result
            orders = self.execute_trades(order_depth, product, quantity_buy, quantity_sell)
            result[product] = orders

        return result, conversions, traderData

    def execute_trades(self, order_depth, product, quantity_buy, quantity_sell):
        orders = []
        quantity = 10
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
