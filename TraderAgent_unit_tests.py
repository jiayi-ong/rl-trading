import unittest
import numpy as np
from StockSimulator import SimpleStock
from RL_Trading import TraderAgent_Random, TraderAgent_QLearning




class DummyStock:
    """Dummy stock with two states for testing purposes.
    """
    states = [0, 1]
    transactions = [0, 1]

    # reward of taking action (col) in state (row)
    reward_matrix = [[-100, 100], 
                     [200, -200]]
    
    # probability of transitioning from current state (row) to next state (col)
    transition_matrix = [[0.2, 0.8],
                         [0.8, 0.2]]
    

    def __init__(self, initial_state=()):
        self.state = initial_state
        self.transaction_history = []


    def traverse_markov_chain(self, trader, iterations, fixed_decision):
        """
        Args:
            iterations (int): number of iterations.
        """
        


    def simulate_trading_day(self, trader, iterations):
        """
        Args:
            iterations (int): number of iterations.
        """
        raise NotImplementedError()



class Tests(unittest.TestCase):

    def test_1(self):
        """
        """
        trader = TraderAgent_QLearning(DummyStock, alpha=1, gamma=0.1)
        stock = DummyStock()
        stock.simulate_trading_day(trader, iterations=200)

        result = np.array_equal()
        self.assertTrue(result)




if __name__ == "__main__":
    unittest.main()