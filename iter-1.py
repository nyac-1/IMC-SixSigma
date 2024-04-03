from datamodel import Order, TradingState
from typing import List

class Trader:
    def run(self, state: TradingState) -> tuple:
        result = {}
        conversions = 0  # Assuming no conversions are planned in this strategy
        trader_data = "MeanReversionStrategy"  # Identifier for the trader's strategy state

        product_name = "AMETHYSTS"
        mean_price = 10000  # Preset mean price for AMETHYSTS as a basis for the strategy

        # Execute trading strategy for AMETHYSTS
        if product_name in state.order_depths:
            orders = self.evaluate_orders(state, mean_price, product_name)
            if orders:
                result[product_name] = orders
        return result, conversions, trader_data

    def evaluate_orders(self, state: TradingState, mean_price: int, product_name: str) -> List[Order]:
        order_depth = state.order_depths[product_name]
        orders = []

        if order_depth.sell_orders and order_depth.buy_orders:
            best_ask = min(order_depth.sell_orders.keys())
            best_bid = max(order_depth.buy_orders.keys())

            current_position = state.position.get(product_name, 0)
            position_limit = 20  # Maximum allowed position per product

            # If current price is below mean price and we have a short position, square off and go long
            if best_ask < mean_price:
                # Calculate quantity to square off the short position and take an additional long position
                if current_position < 0:  # Check if we have a short position
                    square_off_quantity = abs(current_position)  # Quantity to square off the short position
                    additional_quantity = position_limit  # Additional quantity to go long
                    total_quantity = square_off_quantity + additional_quantity
                    if total_quantity <= position_limit:  # Ensure not exceeding position limit
                        orders.append(Order(product_name, best_ask, total_quantity))
                    else:
                        orders.append(Order(product_name, best_ask, square_off_quantity))  # Only square off if exceeding limit
                else:
                    # If we don't have a short position, just take a normal long position within position limits
                    quantity = min(5, position_limit - current_position)
                    orders.append(Order(product_name, best_ask, quantity))

            # If current price is above mean price and we have a long position, square off and go short
            elif best_bid > mean_price:
                # Calculate quantity to square off the long position and take an additional short position
                if current_position > 0:  # Check if we have a long position
                    square_off_quantity = current_position  # Quantity to square off the long position
                    additional_quantity = position_limit  # Additional quantity to go short
                    total_quantity = square_off_quantity + additional_quantity
                    if total_quantity <= position_limit:  # Ensure not exceeding position limit
                        orders.append(Order(product_name, best_bid, -total_quantity))
                    else:
                        orders.append(Order(product_name, best_bid, -square_off_quantity))  # Only square off if exceeding limit
                else:
                    # If we don't have a long position, just take a normal short position within position limits
                    quantity = min(5, position_limit + current_position)  # Adjust for negative current_position
                    orders.append(Order(product_name, best_bid, -quantity))

        return orders
