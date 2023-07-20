import unittest
from StockSimulator import SimpleStock


class Tests(unittest.TestCase):

    def test_1(self):
        """Long with net long position.
        """
        stock = SimpleStock(initial_price=50)
        stock.portfolio.append((1, 30))
        stock._compute_net_position()

        reward, cashflow = stock._transact_long(N=3)
        self.assertEqual(reward, -50*3)
        self.assertEqual(cashflow, -50*3)


    def test_2(self):
        """Long with net short position.
        """
        stock = SimpleStock(initial_price=50)
        stock.portfolio.append((-1, 30))
        stock._compute_net_position()
        
        reward, cashflow = stock._transact_long(N=3)
        self.assertEqual(reward, -20-50-50)
        self.assertEqual(cashflow, -50-50-50)




if __name__ == "__main__":
    unittest.main()