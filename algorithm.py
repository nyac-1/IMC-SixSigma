import random
from datamodel import Order, TradingState
from typing import List

class Trader:

    def run(self, state: TradingState):
        result = {}
        for product in state.order_depths:
            order_depth = state.order_depths[product] # Get order depth for product
            orders: List[Order] = []
            
            # Decide randomly to buy or sell (p=0.5 for each)
            if random.random() < 0.5:
                # Attempt to buy at best sell price if available
                if len(order_depth.sell_orders) != 0:
                    best_ask = min(order_depth.sell_orders.keys())
                    quantity = 1  # Example quantity
                    orders.append(Order(product, best_ask, quantity))
            else:
                # Attempt to sell at best buy price if available
                if len(order_depth.buy_orders) != 0:
                    best_bid = max(order_depth.buy_orders.keys())
                    quantity = -1  # Negative for selling
                    orders.append(Order(product, best_bid, quantity))
            
            result[product] = orders
        
        # No conversion for this simple example
        conversions = 0
        traderData = "RandomTrading"  # Maintain state if necessary
        return result, conversions, traderData
