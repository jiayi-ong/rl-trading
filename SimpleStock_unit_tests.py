import unittest
from StockSimulator import SimpleStock


class Tests(unittest.TestCase):

    def test_transaction_hold_1(self):
        """Holding with net long position.
        """
        pass


    def test_transaction_hold_2(self):
        """Holding with net short position.
        """
        pass


    def test_transaction_long_1(self):
        """Long with net long position.
        """
        stock = SimpleStock(initial_price=50)
        stock.portfolio.extend([(1,30), (1,40)])
        stock._compute_net_position()

        act_trans, reward, cashflow = stock._process_transaction(2)
        self.assertEqual(act_trans, 2)
        self.assertEqual(stock.position, 4)
        self.assertEqual(reward, 0)
        self.assertEqual(cashflow, -2*50)


    def test_transaction_long_2(self):
        """Long with net short position.
        """
        stock = SimpleStock(initial_price=50)
        stock.portfolio.extend([(-1,40),(-1,70)])
        stock._compute_net_position()
        
        act_trans, reward, cashflow = stock._process_transaction(5)
        self.assertEqual(act_trans, 5)
        self.assertEqual(stock.position, 3)
        self.assertEqual(reward, 20-10)
        self.assertEqual(cashflow, -5*50)


    def test_transaction_long_3(self):
        """Order of closing out on short positions.
        """
        stock = SimpleStock(initial_price=35)
        stock.portfolio.extend([(-1,45), (-1,70), (-1,20)])
        stock._compute_net_position()
        
        truths = [(1,-2,35,-35), (1,-1,10,-35), (1,0,-15,-35)]
        for i in range(3):
            act_trans, reward, cashflow = stock._process_transaction(1)
            self.assertEqual(act_trans, truths[i][0])
            self.assertEqual(stock.position, truths[i][1])
            self.assertEqual(reward, truths[i][2])
            self.assertEqual(cashflow, truths[i][3])


    def test_transaction_short_1(self):
        """Short with net short position.
        """
        stock = SimpleStock(initial_price=40)
        stock.portfolio.append((-1,40))
        stock._compute_net_position()
        
        act_trans, reward, cashflow = stock._process_transaction(-3)
        self.assertEqual(act_trans, -3)
        self.assertEqual(stock.position, -4)
        self.assertEqual(reward, 0)
        self.assertEqual(cashflow, 3*40)


    def test_transaction_short_1(self):
        """Short with net long position.
        """
        stock = SimpleStock(initial_price=30)
        stock.portfolio.append((1, 60))
        stock._compute_net_position()
        
        act_trans, reward, cashflow = stock._process_transaction(-2)
        self.assertEqual(act_trans, -2)
        self.assertEqual(stock.position, -1)
        self.assertEqual(reward, -30)
        self.assertEqual(cashflow, 2*30)


    def test_transaction_short_3(self):
        """Order of closing out on long positions.
        """
        stock = SimpleStock(initial_price=50)
        stock.portfolio.extend([(1,40), (1,63), (1,35)])
        stock._compute_net_position()
        
        truths = [(-1,2,15,50), (-1,1,10,50), (-1,0,-13,50)]
        for i in range(3):
            act_trans, reward, cashflow = stock._process_transaction(-1)
            self.assertEqual(act_trans, truths[i][0])
            self.assertEqual(stock.position, truths[i][1])
            self.assertEqual(reward, truths[i][2])
            self.assertEqual(cashflow, truths[i][3])


    def test_invalid_transaction_1(self):
        """Shorting beyond limit.
        """
        stock = SimpleStock(initial_price=40)
        stock.price_history.append(60)
        # transaction price don't matter on reward while holding
        stock.portfolio.extend([(-1,50),(-1,50),(-1,50),(-1,50),(-1,50)])
        stock._compute_net_position()

        act_trans, reward, cashflow = stock._process_transaction(-3)
        self.assertEqual(act_trans, 0)
        self.assertEqual(stock.position, -5)
        self.assertEqual(reward, 5*20)
        self.assertEqual(cashflow, 0)


    def test_invalid_transaction_2(self):
        """Longing beyond limit.
        """
        stock = SimpleStock(initial_price=50)
        stock.price_history.append(40)
        # transaction price don't matter on reward while holding
        stock.portfolio.extend([(1,50),(1,50),(1,50),(1,50),(1,50)])
        stock._compute_net_position()

        act_trans, reward, cashflow = stock._process_transaction(3)
        self.assertEqual(act_trans, 0)
        self.assertEqual(stock.position, 5)
        self.assertEqual(reward, 5*10)
        self.assertEqual(cashflow, 0)


    def test_price_1(self):
        """Price bounds reached.
        """
        stock1 = SimpleStock(initial_price=100)
        stock2 = SimpleStock(initial_price=10)

        self.assertEqual(stock1.price, 70)
        self.assertEqual(stock2.price, 30)




if __name__ == "__main__":
    unittest.main()