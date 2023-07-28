from abc import ABC, abstractmethod
import numpy as np



class TraderAgent(ABC):
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
    

    @abstractmethod
    def make_transaction(self, **kwargs):
        """
        """
        raise NotImplementedError()
    

    @abstractmethod
    def learn_from_reward(self, **kwargs):
        """
        """
        raise NotImplementedError()
    



class TraderAgent_Random(TraderAgent):
    """
    """

    def make_transaction(self, **kwargs):
        """
        """
        return np.random.choice(self.stock.transactions)
    

    def learn_from_reward(self, **kwargs):
        """Random trader does not learn from rewards.
        """
        pass




class TraderAgent_QLearning(TraderAgent):
    """
    """

    def __init__(self, stock, gamma, alpha):
        """
        """
        super().__init__(stock)
        self.gamma = gamma
        self.alpha = alpha
        self.trade_till_position_0 = True
        self.Q_HAT = np.zeros(shape=(len(stock.states), len(stock.transactions)))
        self.i_to_state = {i:j for i,j in enumerate(stock.states)}
        self.state_to_i = {j:i for i,j in enumerate(stock.states)}
        self.i_to_action = {i:j for i,j in enumerate(stock.transactions)}
        self.action_to_i = {j:i for i,j in enumerate(stock.transactions)}

    
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
    

    def make_transaction(self, current_state):
        """
        """
        Q_row = self.Q_HAT[self.state_to_i[current_state]]
        
        if all(Q_row == 0):
            transaction = np.random.choice(self.stock.transactions)
        else:
            # choosing action using softmax policy
            probs = self.stable_softmax(Q_row)
            transaction = np.random.choice(self.stock.transactions, p=probs)

        return transaction
    

    def learn_from_reward(self, transaction, reward, current_state, next_state):
        """
        """
        new_value = reward + self.gamma * np.max(self.Q_HAT[self.state_to_i[next_state]])
        j, k = self.state_to_i[current_state], self.action_to_i[transaction]
        self.Q_HAT[j, k] += self.alpha * (new_value - self.Q_HAT[j, k])
