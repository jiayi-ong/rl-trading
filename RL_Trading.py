import numpy as np



class TraderAgent:
    """
    """

    def __init__(self, stock):
        """
        Args:
            stock (SimpleStock):
                the class name SimpleStock
        """
        self.stock = stock
        self.trade_till_position_0 = False
    

    def make_transaction(self):
        """
        """
        raise NotImplementedError()
    

    def learn_from_reward(self):
        """
        """
        raise NotImplementedError()
    



class TraderAgent_Random(TraderAgent):
    """
    """

    def make_transaction(self):
        """
        """
        return np.random.choice(self.stock.transactions)
    

    def learn_from_reward(self, reward, next_state):
        """
        """
        pass




class TraderAgent_QLearning(TraderAgent):
    """
    """

    def __init__(self):
        """
        """
        self.Q_HAT = np.zeros(shape=(len(self.stock.states), len(self.stock.transactions)))

    
    @staticmethod
    def stable_softmax(x, axis=1):
        """ Numerically stable softmax:
        softmax(x) = e^x /(sum(e^x))
                = e^x / (e^max(x) * sum(e^x/e^max(x)))
        Args:
            x: A 1-dimensional array of floats
        Returns:
            output: softmax(x)
        """
        z = np.exp(x - np.max(x))
        output = z / np.sum(z)

        return output
