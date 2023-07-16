import pandas as pd
import numpy as np
import itertools as it
import matplotlib.pyplot as plt



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
            (to limit the state space size for tractability). Position = number of
            stocks owned. Negative position means shares are shorted.
        position_increment (int):
            when stocks are longed/shorted, it must be at this increment.
        states (list[tuple]):
            all observable states
        transactions (list):
            the action space of the trader; how many shares to long/short
            at each time step. transactions = 0 means 'hold' current position.
            If current position is -1 (one stock shorted), a transaction of 1
            would close out the short position instead of creating a new long position
            (i.e. no hedging with complicated positions).
        transaction_cost (float):
            cost of trading per share.
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
         index=indicator_values, columns=indicator_values)

    price_bounds = [30, 70]
    position_bounds = [-5, 5]
    position_increment = 1

    states = list(it.product(indicator_values, 
                        range(price_bounds[0], price_bounds[1]+1, 1),
                        range(position_bounds[0], position_bounds[1]+1, position_increment)))
    
    transactions = list(range(-position_bounds[1], position_bounds[1]+1, position_increment))

    transaction_cost = 0
    
    
    def __init__(self, initial_indicator=0, initial_price=50, initial_position=0):
        """
        """
        self.indicator_history = [initial_indicator]
        self.growth_history = []
        self.price = initial_price
        self.price_history = [self.price]
        self.position = initial_position
        self.position_history = [initial_position]
        self.transaction_history = []
        self.reward_history = []
    

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
            
    
    def reward_calculator(self, transaction):
        """Calculates reward for the trader for making a transaction
        given a current state of the stock. Buying incurs a cost
        (negative reward) of number of shares bought x current share price.
        transaction (int): number of stocks longed/shorted
        """
        reward = 0

        # net long position
        if transaction > 0 and self.position >= 0:
            reward -= transaction * (self.price + self.transaction_cost)
        # net short position
        elif transaction < 0 and self.position < 0:
            capital_gains = abs(transaction) * (self.price - self.last_buyin_price)
            payoff -= transaction * self.price
            
            # apply capital gains tax
            taxes = (capital_gains > 0) * self.capital_gains_tax * capital_gains
            payoff -= taxes
                
        # if holding
        else:
            payoff += self.position * (self.price - self.price_history[-1])
                
        return payoff
    
    
    def is_valid_transaction(self, transaction):
        """Allows selling iff a share is already owned.
        Allows buying iff ownership limit is not reached.
        """
        if self.position + transaction > self.position_bounds[1]:
#             print(f"Cannot own more than {self.position_bounds[1]} stocks.")
            return False
        elif self.position + transaction < self.position_bounds[0]:
#             print(f"Cannot own less than {self.position_bounds[0]} stocks.")
            return False
        else:
            return True
    

    def close_out(self):
        """Terminates all future trading and close out on current position.
        """
        pass

    
    def simulate_trading_day(self, Ndays=1):
        """Simulate a number of trading days passing.
        Ndays (int): number of trading days (>= 1)
        """
        pass

    
    def calculate_financial_gains(self):
        """Calculate net financial gains (capital gains minus transaction costs).
        """
        pass

    
    def investment_decision(self, transaction):
        """
        """
        # ========== CALCULATE PAYOFFS ==========
        if not self.is_valid_transaction(transaction):
            # if action is not valid, 'do nothing'
            transaction = 0
        self.transaction_history.append(transaction)
        
        # records most recent buy-in price
        if transaction > 0:
            self.last_buyin_price = self.price
            
        payoff = self.payoff_calculator(transaction)
        self.payoff_history.append(payoff)
        self.total_payoff += payoff
        
        # ========== STATE TRANSITION ==========
        self.position += transaction
        
        # select next-period price growth based on current performance
        probs = self.growth_probabilities.loc[self.performance, :].values
        self.growth = np.random.choice(self.stock_growths, p=probs)
        # calculate next-period price
        self.price_history.append(self.price)
        self.price = self.price + int(self.growth)
        
        # select next-period performance
        self.performance_history.append(self.performance)
        probs = self.performance_transition_matrix.loc[self.performance, :].values
        self.performance = np.random.choice(self.firm_performance, p=probs)
        
        state = (self.performance, self.price, self.position)
        
        return state, payoff
    