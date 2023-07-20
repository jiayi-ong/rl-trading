from StockSimulator import *

stock = SimpleStock()
N = 10
rand_strats = np.random.choice([-1,0,1], replace=True, size=N)
stock.simulate_trading_day(Ndays=N, strategy=rand_strats)

print("Prices:", stock.price_history)
print("Transactions:", stock.transaction_history)
print("Rewards:", stock.reward_history)
print("Cashflow:", stock.cashflow_history)


stock.plot_history()