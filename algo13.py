import jsonpickle
from datamodel import Order, TradingState

class Trader:
    def run(self, state: TradingState):
        # Deserialize traderData or initialize it
        if state.traderData and state.traderData != "RandomTrading":
            trader_state = jsonpickle.decode(state.traderData)
        else:
            # Initializes with empty positions and average_prices if not present
            trader_state = {"positions": {}, "average_prices": {}}

        result = {}
        conversions = 0
        assets = ["AMETHYSTS", "STARFRUIT"]
        limits = {"AMETHYSTS": 20, "STARFRUIT": 30}
        levels = {"AMETHYSTS": 10000, "STARFRUIT": 4960}

        # Intend to place orders based on predefined strategy
        for product in assets:
            order_depth = state.order_depths.get(product, {})
            current_position = trader_state["positions"].get(product, 0)
            max_quantities = self.tradable_quantity(current_position, limits.get(product))
            quantity_buy = min(10, max_quantities.get("buy"))
            quantity_sell = min(10, max_quantities.get("sell"))

            if quantity_buy > 0:
                result[product] = [self.limit_order(product, levels[product] - 1, quantity_buy, "buy")]
            elif quantity_sell > 0:
                result[product] = [self.limit_order(product, levels[product] + 1, quantity_sell, "sell")]

        # Update trader_state based on filled trades from state.own_trades
        for product, trades in state.own_trades.items():
            for trade in trades:
                # Adjust the quantity for buy/sell direction based on trade details
                quantity = trade.quantity if trade.buyer == "SUBMISSION" else -trade.quantity
                # Update positions and average prices based on the trades
                new_position, new_avg_price = self.update_position_and_price(
                    trader_state["positions"].get(product, 0),
                    trader_state["average_prices"].get(product, 0),
                    quantity, 
                    trade.price
                )
                # Apply the updates to trader_state
                trader_state["positions"][product] = new_position
                trader_state["average_prices"][product] = new_avg_price

        # Serialize the updated trader_state for persistence
        print(trader_state)
        traderData = jsonpickle.encode(trader_state)

        return result, conversions, traderData

    def limit_order(self, product, price, quantity, side):
        # Generates an order based on the provided details
        return Order(product, price, quantity if side == "buy" else -quantity)

    def tradable_quantity(self, current_position: int, position_limit: int):
        # Calculate the maximum buy/sell quantity based on current position and position limits
        max_buy = position_limit - max(current_position, 0)
        max_sell = max(0, current_position)  # Can sell up to the amount in position
        return {"buy": max_buy, "sell": max_sell}

    def update_position_and_price(self, old_position, old_avg_price, quantity, price):
        # Update the position size and average price incorporating the new trade
        if quantity > 0:  # Buy transaction
            total_cost = old_avg_price * old_position + price * quantity
            new_position = old_position + quantity
            new_avg_price = total_cost / new_position if new_position else 0
        else:  # Sell transaction, reduce position
            new_position = old_position + quantity
            # For sell transactions, the average price doesn't change
            new_avg_price = old_avg_price

        return new_position, new_avg_price
