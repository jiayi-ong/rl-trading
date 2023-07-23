from StockSimulator import *
from RL_Trading import TraderAgent_Random




stock = SimpleStock()
trader = TraderAgent_Random(stock)

stock.simulate_trading_day(Ndays=14, trader=trader, print_out=False)

print("Prices:", stock.price_history)
print("Transactions:", stock.transaction_history)
print("Rewards:", stock.reward_history)
print("Cashflow:", stock.cashflow_history)


stock.plot_history()