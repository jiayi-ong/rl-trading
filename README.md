# Trading Stocks with Reinforcement-Learning

Examines the feasibility of automating stock trading decisions using RL in a simulated setting.

## Simulation

Simulates a stock (share of a company) that can be traded. 

The single trader is a price taker (his transactions have no effects on the stock price). 

The only exogenous factor that affects the stock price is the stock's indicator, whose value in the current period
predicts the growth of the stock's next-period price. The indicator's value over time is governed by a transition matrix. 

The stock's observable state comprises the stock's current price, the stock's indicator value, and the trader's
position in the stock (how many stocks owned). 

No hedging positions are allowed, i.e. no concurrent long and short positions.

## RL Trader

Discrete state-action reward table for the Q-Learning algorithm.