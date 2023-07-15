import pandas as pd
import numpy as np
import itertools as it
import matplotlib.pyplot as plt



class SimpleStock:
    """Simulates a simple stock that can be traded.
    The single trader is a price taker (his transactions have no effects
    on the stock price). The only exogenous factor that affects the
    stock price is the firm's performance, which can take 3 levels.
    Firm performance in the current period affects next-period prices.
    The firm's performance over time is governed by a transition
    matrix. The stock's observable state comprises the trader's position
    in the stock, the firm performance, and price, which is indirectly 
    defined by the last-period price and growth rates.
    """
    # ========== STATES ==========
    firm_performance = [-2,-1,0,1,2]
    performance_transition_matrix = pd.DataFrame(
        [[0.40, 0.60, 0.00, 0.00, 0.00],
         [0.00, 0.40, 0.60, 0.00, 0.00],
         [0.00, 0.00, 0.10, 0.90, 0.00],
         [0.00, 0.00, 0.00, 0.40, 0.60],
         [0.60, 0.00, 0.00, 0.00, 0.40]], 
        index=firm_performance, columns=firm_performance)
    
    # stock prices can change by +/- 1 or 0 per period
    # probabilities of change are conditional on current firm performance
    # e.g. next period prices will very likely be lower if firm under-performed this period
    stock_growths = [-2, -1, 0, 1, 2]
    growth_probabilities = pd.DataFrame(
        [[1.00, 0.00, 0.00, 0.00, 0.00],
         [0.00, 0.90, 0.10, 0.00, 0.00],
         [0.00, 0.00, 0.90, 0.10, 0.00],
         [0.00, 0.00, 0.00, 0.90, 0.10],
         [0.00, 0.00, 0.00, 0.00, 1.00]], index=firm_performance, columns=stock_growths)
    
    # prices are discrete
    # controls the number of states by limiting prices
    price_bounds = [40, 60]
    
    # position = how many shares owned by the trader
    # trader cannot own negative shares and cannot own more than 10 shares
    position_bounds = [0, 10]
    # tracks the most recent purchase price (for capital gains tax calculation)
    last_buyin_price = None
    
    # unit of change in position allowed 
    # i.e. if stocks are bought or sold, must be at increments of x shares
    increment = 2
    
    # generate all observable states: performance x price x position
    states = list(it.product(firm_performance, 
                        range(price_bounds[0], price_bounds[1]+1),
                        range(position_bounds[0], position_bounds[1]+1, increment)))
    
    # ========== ACTIONS ==========
    # investor can buy or sell x shares at a time, or hold (buy 0)
    # action space = [-x, -(x-1), ..., 0, ..., x-1, x]
    # e.g. if transactions = -x, then sell x shares
    transactions = list(range(-position_bounds[1], position_bounds[1]+1, increment))
    
    # fixed transaction cost per share
    transaction_cost = 0
    
    # capital gains tax: fixed percentage of capital gain deducted
    capital_gains_tax = 0.2
    
    
    def __init__(self, initial_performance=0, initial_price=50, initial_position=0):
        """
        """
        self.performance = initial_performance
        self.price = initial_price
        self.position = initial_position
        self.growth = None
        # tracks transaction and price histories
        self.performance_history = []
        self.transaction_history = []
        self.payoff_history = []
        self.price_history = [initial_price]
        self.total_payoff = 0
    
    @property
    def price(self):
        return self.__price
    
    @price.setter
    def price(self, value):
        a, b = self.price_bounds
        if value > b:
            self.__price = b
        elif value < a:
            self.__price = a
        else:
            self.__price = value
            
    
    def payoff_calculator(self, transaction):
        """Payoffs are based on change in value of total assets.
        Buying has a payoff of 0 - transaction costs, since cash is
        converted to the value of stock minus fees. Holding while stock
        appreciates/depreciates has a payoff of the change in stock value
        between two consecutive periods. Selling has a payoff of the final
        stock value minus transaction fees and taxes.
        """
        payoff = 0
        
        # if buying
        if transaction > 0:
            payoff -= transaction * (self.price + self.transaction_cost)
        # if selling
        elif transaction < 0:
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
    