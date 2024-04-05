import random
from datamodel import Order, TradingState
from typing import List

class Trader:

    def run(self, state: TradingState):
        result = {}
        conversions = 0
        traderData = "RandomTrading"  # Maintain state if necessary

        limits = {"AMETHYSTS": 20, "STARFRUIT": 30}
        levels = {"AMETHYSTS": 10000, "STARFRUIT": 4900}

        product_name = "AMETHYSTS"

        
        if product_name in state.order_depths.keys():
            order_depth = state.order_depths[product_name]  # Get order depth for product_name

            orders = []
            quantity_buy = self.tradable_quantity(state.position.get(product_name, 0), limits.get(product_name)).get("buy")  # Example quantity for buying
            quantity_sell = self.tradable_quantity(state.position.get(product_name, 0), limits.get(product_name)).get("sell")  # Example quantity for buying

            # Decide randomly to buy or sell (p=0.5 for each)
            if random.random() < 0.5:
                # Attempt to buy at the best and second best sell price if available
                if len(order_depth.sell_orders) > 1:  # Check there are at least 2 sell orders
                    sorted_asks = sorted(order_depth.sell_orders.keys())
                    best_ask = sorted_asks[0]
                    second_best_ask = sorted_asks[1]
                    orders.append(Order(product, best_ask, quantity_buy))
                    orders.append(Order(product, second_best_ask, quantity_buy))
            else:
                # Attempt to sell at the best and second best buy price if available
                if len(order_depth.buy_orders) > 1:  # Check there are at least 2 buy orders
                    sorted_bids = sorted(order_depth.buy_orders.keys(), reverse=True)
                    best_bid = sorted_bids[0]
                    second_best_bid = sorted_bids[1]
                    orders.append(Order(product, best_bid, -1*quantity_sell))
                    orders.append(Order(product, second_best_bid, -1*quantity_sell))

            result[product_name] = orders

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
    

