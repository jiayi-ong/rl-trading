import sys
import pandas as pd
import numpy as np
import itertools as it
import matplotlib.pyplot as plt
from RL_Trading import TraderAgent



class SimpleStock:
    """Simulates a stock (share of a company) that can be traded.
    The single trader is a price taker (his transactions have no effects
    on the stock price). The only exogenous factor that affects the
    stock price is the stock's indicator, whose value in the current period
    predicts the growth of the stock's next-period price. The indicator's value 
    over time is governed by a transition matrix. The stock's observable state comprises 
    the stock's current price, the stock's indicator value, and the trader's
    position in the stock (how many stocks owned).

    Attributes:
        indicator_values (list): 
            discrete values that the stock's indicator can take.
        transition_matrix (pd.DataFrame): contains the probabilities of transitioning
            between one indicator value to another.
        stock_growths (list):
            discrete values that the next-period stock price can change by.
        growth_probabilities (pd.DataFrame):
            each row is the conditional distribution of stock price growth
            given the current indicator value.
        price_bounds (list):
            the lower and upper bounds of the discrete stock price (to limit
            the state space size for tractability).
        position_bounds (list):
            the lower and upper bounds of the trader's position in the stock price 
            (to limit the state space size for tractability). Position = net number of
            stocks longed / shorted. Negative position means more shares are shorted
            than longed.
        states (list[tuple]):
            all observable states, unique combinations of indicator values
            x prices x positions.
        transactions (list):
            the action space of the trader; how many shares to long/short
            at each time step. transactions = 0 means 'hold' current position.
            If current position is -1 (one stock shorted), a transaction of 1
            would close out the short position instead of creating a new long position
            (i.e. no simultaneous short and long positions).
        transaction_cost (float):
            cost of trading per share.
        portfolio (list[tuple]):
            Each tuple tracks all longs or shorts made, and the price they were made at.
            The first value (-1 or +1) indicates a short or long transaction made, 
            and the second value is the price.
    """

    indicator_values = [-2, -1, 0, 1, 2]

    transition_matrix = pd.DataFrame(
        [[0.40, 0.60, 0.00, 0.00, 0.00],
         [0.00, 0.40, 0.60, 0.00, 0.00],
         [0.00, 0.00, 0.10, 0.90, 0.00],
         [0.00, 0.00, 0.00, 0.40, 0.60],
         [0.60, 0.00, 0.00, 0.00, 0.40]], 
        index=indicator_values, columns=indicator_values)
    
    stock_growths = [-2, -1, 0, 1, 2]

    growth_probabilities = pd.DataFrame(
        [[1.00, 0.00, 0.00, 0.00, 0.00],
         [0.00, 0.90, 0.10, 0.00, 0.00],
         [0.00, 0.00, 0.90, 0.10, 0.00],
         [0.00, 0.00, 0.00, 0.90, 0.10],
         [0.00, 0.00, 0.00, 0.00, 1.00]], 
         index=indicator_values, columns=stock_growths)

    price_bounds = [30, 70]
    position_bounds = [-5, 5]

    states = list(it.product(indicator_values, 
                        range(price_bounds[0], price_bounds[1]+1),
                        range(position_bounds[0], position_bounds[1]+1)))
    
    transactions = list(range(-position_bounds[1], position_bounds[1]+1))

    transaction_cost = 0
    
    
    def __init__(self, initial_indicator=0, initial_price=50):
        """Instantiates a SimpleStock.
        Args:
            initial_indicator (int): starting value of the stock's indicator
            initial_price (int): starting value of the stock's price
        """
        self.portfolio = []
        self.position = 0
        self.indicator_history = [initial_indicator]
        self.growth_history = []
        self.price = initial_price
        self.price_history = [self.price]
        self.transaction_history = []
        self.reward_history = []
        self.cashflow_history = []
    


    @property
    def price(self):
        return self.__price
    
    @price.setter
    def price(self, value):
        """Set price to boundary value if exceeded.
        """
        a, b = self.price_bounds
        if value > b:
            self.__price = b
        elif value < a:
            self.__price = a
        else:
            self.__price = value



    def _compute_net_position(self):
        """Computes the net position of the current
        portfolio. E.g. if there are three shorted stocks,
        the net position would be -3.
        """
        position = 0

        for transaction in self.portfolio:
            position += transaction[0]

        self.position = position

    

    def _is_valid_transaction(self, transaction):
        """Checks if position bounds are violated.
        Args:
            transaction (int):
        Returns:
            (bool): whether the transaction is valid
        """
        if self.position + transaction > self.position_bounds[1]:
            return False
        elif self.position + transaction < self.position_bounds[0]:
            return False
        else:
            return True


    
    def _transact_short(self, N):
        """Computes the transaction 'short' N times and
        returns the reward and cashflow given the current state.
        """
        reward, cashflow = 0, 0
        self.portfolio.sort(key=lambda x: (-x[0], x[1]), reverse=True)

        for _ in range(N):

            if self.position <= 0:
                self.portfolio.append((-1, self.price))
                reward += self.price

            # if there is a net long position, longed shares
            # would be sold in ascending order of price bought (sell cheapest first)
            else:
                shorted = self.portfolio.pop()
                reward += self.price - shorted[1]
            
            cashflow += self.price

            # update position
            self._compute_net_position()

        return reward, cashflow

    

    def _transact_long(self, N):
        """Computes the transaction 'long' N times and
        returns the reward and cashflow given the current state.
        """
        reward, cashflow = 0, 0
        self.portfolio.sort(key=lambda x: (-x[0], x[1]))

        for _ in range(N):

            if self.position >= 0:
                self.portfolio.append((1, self.price))
                reward -= self.price

            # if there is a net short position, shorted shares
            # would be closed in descending order of price shorted (close most expensive first)
            else:
                closed = self.portfolio.pop()
                reward += closed[1] - self.price
            
            cashflow -= self.price

            # update position
            self._compute_net_position()

        return reward, cashflow



    def _transact_hold(self):
        """Computes the transaction 'hold' and
        returns the reward given the current state.
        """
        # with a net long position, reward increases if price appreciates
        if self.position > 0:
            return self.price - self.price_history[-1], 0

        # with a net short position, reward increases if price depreciates
        elif self.position < 0:
            return self.price_history[-1] - self.price, 0
        
        # holding an empty portfolio has no reward
        else:
            return 0, 0



    def _process_transaction(self, transaction):
        """Apply changes to portfolio and compute rewards 
        and cashflows resulting from making the transaction 
        given the current state. If a transaction is invalid
        (e.g. violates the position bounds), the a 'hold' is
        transacted.
        Args:
            transaction: the transaction initiated.
        Returns:
            actual_transaction: the actual transaction made.
        """

        if self._is_valid_transaction(transaction):
            actual_transaction = transaction
            if transaction > 0:
                reward, cashflow = self._transact_long(N=abs(transaction))
            elif transaction < 0:
                reward, cashflow = self._transact_short(N=abs(transaction))
            else:
                reward, cashflow = self._transact_hold()

        else:
            # actual transaction is a 'hold'
            actual_transaction = 0
            reward, cashflow = self._transact_hold()

        # record reward, cashflow, and transaction
        self.reward_history.append(reward)
        self.cashflow_history.append(cashflow)
        self.transaction_history.append(actual_transaction)

        return actual_transaction, reward, cashflow



    def _close_out(self):
        """Close out on current position by liquidating portfolio.
        """
        pass

    

    def _transition_states(self):
        """Computes next-period indicator values and stock price.
        """
        current_indicator = self.indicator_history[-1]

        # determine next-period price
        growth_probs = self.growth_probabilities.loc[current_indicator]
        price_growth = np.random.choice(self.stock_growths, p=growth_probs)
        self.growth_history.append(price_growth)
        self.price_history.append(self.price)
        self.price += price_growth

        # determine next-period indicator
        change_probs = self.transition_matrix.loc[current_indicator]
        next_indicator = np.random.choice(self.indicator_values, p=change_probs)
        self.indicator_history.append(next_indicator)

        return (next_indicator, self.price, self.position)

    

    def simulate_trading_day(self, Ndays=1, trader=None, print_out=False):
        """Simulate a number of trading days passing.
        Args:
            Ndays (int): number of trading days.
            trader (TraderAgent): a TraderAgent instance that decides the transaction
                for each trading day.
        """
        if not isinstance(trader, TraderAgent):
            sys.exit("Please provide a valid TraderAgent instance.")
        
        trade_till_position_0 = trader.trade_till_position_0
        day = 0

        while day < Ndays or trade_till_position_0 * (self.position != 0):

            actual_transaction, reward, cashflow = self._process_transaction(strategy[day])

            next_state = self._transition_states()

            if print_out:
                print("==========", "Simulating day", day+1, "==========")
                print("Indicator:", self.indicator_history[-1],
                    "| Price:", self.price,
                    "| Position:", self.position)
                
                print("Transaction:", actual_transaction, "| Reward:", reward, 
                    "| Cashflow:", cashflow)
                print("Portfolio:", self.portfolio)
                print("Growth:", self.growth_history[-1])
            
            day += 1




    def plot_history(self):
        """Visualize historical indicator values, prices, transactions, and cashflows.
        """
        periods = range(len(self.price_history[1:]))
        h = max(self.price_history[1:])

        fig, ax1 = plt.subplots()
        ax1.set_title(f"Net CF: {sum(self.cashflow_history)}")

        # price history
        ax1.plot(self.price_history[1:], c="black", label="Price")

        # transaction history
        for t, (act,cf) in enumerate(zip(self.transaction_history, self.cashflow_history)):
            if act < 0:
                ax1.axvline(x=t, c="red", ls=":")
                ax1.text(x=t+0.1, y=h-0.2, s=f"S: {act}\nCF: {cf}", fontsize=8)
            elif act > 0:
                ax1.axvline(x=t, c="blue", ls=":")
                ax1.text(x=t+0.1, y=h-0.2, s=f"L: {act}\nCF: {cf}", fontsize=8)

        # indicator history
        ax2 = ax1.twinx()
        ax2.bar(x=periods, height=self.indicator_history[1:], alpha=0.6)
        ax2.set_ylim(min(self.indicator_values)-2, h//2)
        ax2.set(ylabel=None)
        ax2.axhline(y=0)

        plt.show()