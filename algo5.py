from datamodel import Order, TradingState
from typing import List

class Trader:

    def run(self, state: TradingState):
        result = {}
        conversions = 0
        traderData = "MeanReversionTrading"
        limits = {"AMETHYSTS": 20, "STARFRUIT": 30}

        product_name = "AMETHYSTS"
        mean_price = 10000 

        if product_name in state.order_depths:
            order_depth = state.order_depths[product_name]
            orders = []
            best_ask = min(order_depth.sell_orders.keys())
            best_bid = max(order_depth.buy_orders.keys())

            if best_ask <= mean_price:
                sorted_asks = sorted(order_depth.sell_orders.keys())
                best_ask = sorted_asks[0]
                second_best_ask = sorted_asks[1]

                for price, qty in order_depth.sell_orders.items():
                    if price == best_ask:
                        orders.append(Order(product_name, best_ask, 1))
                    elif price == second_best_ask:
                        orders.append(Order(product_name, second_best_ask, 1))
                        
            elif best_bid >= mean_price:
                sorted_bids = sorted(order_depth.buy_orders.keys(), reverse=True)
                best_bid = sorted_bids[0]
                second_best_bid = sorted_bids[1]

                for price, qty in order_depth.buy_orders.items():
                    if price == best_bid:
                        orders.append(Order(product_name, best_bid, -1))
                    elif price == second_best_bid:
                        orders.append(Order(product_name, second_best_bid, -1))
            
            return orders




