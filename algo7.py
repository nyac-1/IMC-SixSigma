# Code to remmber the order depth history for each product and to buy or sell randomly

import random
from datamodel import Order, TradingState  # Assuming datamodel is provided elsewhere as per your documentation
from typing import List
import jsonpickle  # For encoding and decoding complex Python objects

class Trader:

    def run(self, state: TradingState):
        result = {}
        conversions = 0
        # Attempt to deserialize traderData if it exists, else initialize
        try:
            traderData = jsonpickle.decode(state.traderData)
        except Exception as e:
            traderData = {"order_depth_history": {}}

        for product in state.order_depths:
            order_depth = state.order_depths[product]  # Get order depth for product
            orders: List[Order] = []

            # Decide randomly to buy or sell (p=0.5 for each)
            if random.random() < 0.5:
                # Attempt to buy at the best and second best sell price if available
                if len(order_depth.sell_orders) > 1:  # Check there are at least 2 sell orders
                    sorted_asks = sorted(order_depth.sell_orders.keys())
                    best_ask = sorted_asks[0]
                    second_best_ask = sorted_asks[1]
                    quantity = 1  # Example quantity for buying
                    orders.append(Order(product, best_ask, quantity))
                    orders.append(Order(product, second_best_ask, quantity))
            else:
                # Attempt to sell at the best and second best buy price if available
                if len(order_depth.buy_orders) > 1:  # Check there are at least 2 buy orders
                    sorted_bids = sorted(order_depth.buy_orders.keys(), reverse=True)
                    best_bid = sorted_bids[0]
                    second_best_bid = sorted_bids[1]
                    quantity = -1  # Example quantity for selling, negative to indicate sell
                    orders.append(Order(product, best_bid, quantity))
                    orders.append(Order(product, second_best_bid, quantity))

            # Save current order depth for the product
            current_order_depth = {
                "buy_orders": dict(order_depth.buy_orders),
                "sell_orders": dict(order_depth.sell_orders)
            }

            # Append current order depth to the history in traderData
            traderData["order_depth_history"].setdefault(product, []).append(current_order_depth)

            result[product] = orders

        # Serialize traderData using jsonpickle to maintain state
        traderData_encoded = jsonpickle.encode(traderData)

        return result, conversions, traderData_encoded
