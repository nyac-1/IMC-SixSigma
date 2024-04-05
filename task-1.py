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
                # Attempt to buy at best and second-best sell price if available
                if len(order_depth.sell_orders) >= 2:
                    sell_prices = sorted(order_depth.sell_orders.keys())
                    best_ask = sell_prices[0]
                    second_best_ask = sell_prices[1]
                    quantity = 1  # Example quantity

                    # Place orders at best and second-best ask prices
                    orders.append(Order(product, best_ask, quantity))
                    # orders.append(Order(product, second_best_ask, quantity))
                elif len(order_depth.sell_orders) == 1:
                    best_ask = min(order_depth.sell_orders.keys())
                    orders.append(Order(product, best_ask, quantity))
            else:
                # Attempt to sell at best and second-best buy price if available
                if len(order_depth.buy_orders) >= 2:
                    buy_prices = sorted(order_depth.buy_orders.keys(), reverse=True)
                    best_bid = buy_prices[0]
                    second_best_bid = buy_prices[1]
                    quantity = -1  # Negative for selling

                    # Place orders at best and second-best bid prices
                    # orders.append(Order(product, best_bid, quantity))
                    # orders.append(Order(product, second_best_bid, quantity))
                elif len(order_depth.buy_orders) == 1:
                    best_bid = max(order_depth.buy_orders.keys())
                    orders.append(Order(product, best_bid, quantity))

            result[product] = orders

        # No conversion for this simple example
        conversions = 0
        traderData = "RandomTradingAdvanced"  # Maintain state if necessary
        return result, conversions, traderData
