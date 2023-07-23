import numpy as np



class TraderAgent:
    """
    """

    def __init__(self, stock, trader_algorithm):
        """
        Args:
            stock (SimpleStock):

            trader_algorithm (str):
                either 'random' or 'Q-learning'
        """
        pass

    
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