import unittest
from StockSimulator import SimpleStock


class Tests(unittest.TestCase):

    def test_transaction_1(self):
        """Long with net long position.
        """
        stock = SimpleStock(initial_price=50)
        stock.portfolio.extend([(1,30), (1,40)])
        stock._compute_net_position()

        reward, cashflow = stock._transact_long(N=2)
        self.assertEqual(stock.position, 4)
        self.assertEqual(reward, 0)
        self.assertEqual(cashflow, -2*50)


    def test_transaction_2(self):
        """Long with net short position.
        """
        stock = SimpleStock(initial_price=50)
        stock.portfolio.extend([(-1,40),(-1,70)])
        stock._compute_net_position()
        
        reward, cashflow = stock._transact_long(N=5)
        self.assertEqual(stock.position, 3)
        self.assertEqual(reward, 20-10)
        self.assertEqual(cashflow, -5*50)


    def test_transaction_3(self):
        """Short with net short position.
        """
        stock = SimpleStock(initial_price=40)
        stock.portfolio.extend([(-1,40)])
        stock._compute_net_position()
        
        reward, cashflow = stock._transact_short(N=3)
        self.assertEqual(stock.position, -4)
        self.assertEqual(reward, 0)
        self.assertEqual(cashflow, 3*40)


    def test_transaction_4(self):
        """Short with net long position.
        """
        stock = SimpleStock(initial_price=30)
        stock.portfolio.append((1, 60))
        stock._compute_net_position()
        
        reward, cashflow = stock._transact_short(N=2)
        self.assertEqual(stock.position, -1)
        self.assertEqual(reward, -30)
        self.assertEqual(cashflow, 2*30)


    def test_transaction_5(self):
        """Order of closing out on long positions.
        """
        pass


    def test_transaction_6(self):
        """Order of closing out on short positions.
        """
        pass


    def test_invalid_transaction_1(self):
        """Shorting beyond limit.
        """
        pass


    def test_invalid_transaction_2(self):
        """Longing beyond limit.
        """
        pass


    def test_misc_1(self):
        """Price bounds reached.
        """
        stock1 = SimpleStock(initial_price=100)
        stock2 = SimpleStock(initial_price=10)

        self.assertEqual(stock1.price, 70)
        self.assertEqual(stock2.price, 30)




if __name__ == "__main__":
    unittest.main()