import random
from datamodel import Order, TradingState
from typing import List

class Trader:

    def run(self, state: TradingState):
        result = {}
        for product in state.order_depths:
            order_depth = state.order_depths[product]  # Get order depth for product
            orders: List[Order] = []

            # Decide randomly to buy or sell (p=0.5 for each)
            if random.random() < 0.5:
                # Attempt to buy at the second best sell price if available
                asks = order_depth.sell_orders
                if len(asks) > 1:  # Check there are at least 2 sell orders
                    sorted_asks = sorted(asks.keys())
                    best_ask = sorted_asks[0]
                    second_best_ask = sorted_asks[1]
                    quantity = 1  # Example quantity
                    orders.append(Order(product, best_ask, quantity))
                    orders.append(Order(product, second_best_ask, quantity))
            else:
                # Attempt to sell at the second best buy price if available
                if len(order_depth.buy_orders) > 1:  # Check there are at least 2 buy orders
                    sorted_bids = sorted(order_depth.buy_orders.keys(), reverse=True)
                    second_best_bid = sorted_bids[1]  # Get the second highest price
                    quantity = -1  # Negative for selling
                    orders.append(Order(product, second_best_bid, quantity))

            result[product] = orders

        # No conversion for this simple example
        conversions = 0
        traderData = "RandomTrading"  # Maintain state if necessary
        return result, conversions, traderData
