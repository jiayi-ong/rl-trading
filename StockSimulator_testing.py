from StockSimulator import *
from RL_Trading import TraderAgent_Random, TraderAgent_QLearning


trader = TraderAgent_QLearning(stock=SimpleStock, gamma=1, alpha=1)
N_trials = 3
trials = []

for _ in range(N_trials):
    stock = SimpleStock(random_init=True)
    stock.simulate_trading_day(Ndays=14, trader=trader, print_out=False)
    trials.append(stock)


i = 0
print("Prices:", trials[i].price_history)
print("Transactions:", trials[i].transaction_history)
print("Rewards:", trials[i].reward_history)
print("Cashflow:", trials[i].cashflow_history)

trials[i].plot_history()