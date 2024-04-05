import random
from datamodel import Order, TradingState
from typing import List

class Trader:

    def run(self, state: TradingState):
        result = {}
        conversions = 0
        traderData = "RandomTrading"  # Maintain state if necessary

        limits = {"AMETHYSTS": 20, "STARFRUIT": 30}

        for product in state.order_depths:
            if product == "STARFRUIT":
                continue
            order_depth = state.order_depths[product]  # Get order depth for product
            orders: List[Order] = []

            quantities = self.tradable_quantity(state.position.get(product, 0),limits.get(product))
            quantity_buy = quantities.get("buy")
            quantity_sell = quantities.get("sell")

            # Decide randomly to buy or sell (p=0.5 for each)

                # Attempt to buy at the best and second best sell price if available
            if len(order_depth.sell_orders) > 1:  # Check there are at least 2 sell orders
                sorted_asks = sorted(order_depth.sell_orders.keys())
                best_ask = sorted_asks[0]
                second_best_ask = sorted_asks[1]
                quantity = 5  # Example quantity for buying
                # orders.append(Order(product, best_ask, quantity))
                orders.append(Order(product, 10000, quantity))

            # Attempt to sell at the best and second best buy price if available
            if len(order_depth.buy_orders) > 1:  # Check there are at least 2 buy orders
                sorted_bids = sorted(order_depth.buy_orders.keys(), reverse=True)
                best_bid = sorted_bids[0]
                second_best_bid = sorted_bids[1]
                quantity = -5  # Example quantity for selling, negative to indicate sell
                # orders.append(Order(product, best_bid, quantity))
                orders.append(Order(product, 10000, quantity))

            result[product] = orders

        return result, conversions, traderData


    def tradable_quantity(self, current_position: int, position_limit: int) -> dict:
        position_limit = abs(position_limit)
        if current_position >= 0:
            max_buy = position_limit - current_position
            max_sell = current_position + position_limit
        else:
            max_buy = abs(current_position) + position_limit
            max_sell = position_limit - abs(current_position)
        return {"buy": max_buy, "sell": max_sell}
