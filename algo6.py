import random
from datamodel import Order, TradingState
from typing import List

class Trader:

    def run(self, state: TradingState):
        result = {}
        conversions = 0
        traderData = "RandomTrading"  # Maintain state if necessary

        for product in state.order_depths:
            order_depth = state.order_depths[product]  # Get order depth for product
            orders: List[Order] = []

            # Decide randomly to buy or sell (p=0.5 for each)

                # Attempt to buy at the best and second best sell price if available
            if len(order_depth.sell_orders) > 1:  # Check there are at least 2 sell orders
                sorted_asks = sorted(order_depth.sell_orders.keys())
                best_ask = sorted_asks[0]
                second_best_ask = sorted_asks[1]
                quantity = 1  # Example quantity for buying
                orders.append(Order(product, 11000, quantity))
                # orders.append(Order(product, second_best_ask, quantity))

            # Attempt to sell at the best and second best buy price if available
            if len(order_depth.buy_orders) > 1:  # Check there are at least 2 buy orders
                sorted_bids = sorted(order_depth.buy_orders.keys(), reverse=True)
                best_bid = sorted_bids[0]
                second_best_bid = sorted_bids[1]
                quantity = -1  # Example quantity for selling, negative to indicate sell
                orders.append(Order(product, 9000, quantity))
                # orders.append(Order(product, second_best_bid, quantity))

            result[product] = orders

        return result, conversions, traderData
