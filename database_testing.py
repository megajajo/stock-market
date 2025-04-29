# --------------------------------------------------------------------------------------------------------------
# database.py
# Last modified: 20/3/25                        By: Kirsten Else
# Module to test database functions
# Key test info:    Clients - 1. Seller, 2. Buyer, 3. C
#                   Stocks - 1. A, 2. B, 3.C
#                   OwnedStock - Seller owns A, C owns 10 C
# --------------------------------------------------------------------------------------------------------------
import unittest, sqlite3
from database import Database


class TestDatabase(unittest.TestCase):

    # create_transaction tests

    # Add a transaction where bidder has no previous stock and asker has more stock than stock sold
    # Path: UPDATE, INSERT, UPDATEx2, INSERT
    def test_add_transaction_valid_1(self):
        result = Database().create_transaction(2, 2, 1, 1, 6, "A", 1)
        self.assertNotEqual(result, -1)
        connection = sqlite3.connect("stock_market_database.db")
        cursor = connection.cursor()
        # 1 record for bidder
        cursor.execute("""SELECT * FROM OwnedStock WHERE owner_id = 2""")
        self.assertEqual(cursor.fetchall(), [(2, "A", 1, 6)])
        # 1 record for asker
        cursor.execute("""SELECT * FROM OwnedStock WHERE owner_id = 1""")
        self.assertEqual(len(cursor.fetchall()), 1)
        # 1 transaction added
        cursor.execute(
            """SELECT bidder_id, bid_price, asker_id, ask_price, vol, ticker, transaction_price FROM Transactions WHERE transaction_id = ?""",
            (result,),
        )
        self.assertEqual(cursor.fetchall(), [(2, 2, 1, 1, 6, "A", 1)])
        # Reset database
        cursor.execute("""DELETE FROM OwnedStock WHERE owner_id = 2""")
        connection.commit()
        connection.close()

    # Add a transaction where bidder has previous stock and asker has more stock than stock sold
    # Path: UPDATE, UPDATE, UPDATEx2, INSERT
    def test_add_transaction_valid_2(self):
        # Initilise database
        connection = sqlite3.connect("stock_market_database.db")
        cursor = connection.cursor()
        cursor.execute(
            """INSERT INTO OwnedStock(owner_id, ticker, average_price, total_vol) VALUES(2, "A", 2, 10)"""
        )
        connection.commit()
        connection.close()
        result = Database().create_transaction(2, 2, 1, 1, 5, "A", 1)
        self.assertNotEqual(result, -1)
        connection = sqlite3.connect("stock_market_database.db")
        cursor = connection.cursor()
        # 1 record for bidder
        cursor.execute("""SELECT * FROM OwnedStock WHERE owner_id = 2""")
        self.assertEqual(cursor.fetchall(), [(2, "A", 1.67, 15)])
        # 1 record for asker
        cursor.execute("""SELECT * FROM OwnedStock WHERE owner_id = 1""")
        self.assertEqual(len(cursor.fetchall()), 1)
        # 1 transaction added
        cursor.execute(
            """SELECT bidder_id, bid_price, asker_id, ask_price, vol, ticker, transaction_price FROM Transactions WHERE transaction_id = ?""",
            (result,),
        )
        self.assertEqual(cursor.fetchall(), [(2, 2, 1, 1, 5, "A", 1)])
        # Reset database
        cursor.execute("""DELETE FROM OwnedStock WHERE owner_id = 2""")
        connection.commit()
        connection.close()

    # Add a transaction where bidder has no previous stock and asker has exactly the amount of stock
    # Path: DELETE, INSERT, UPDATEx2, INSERT
    def test_add_transaction_valid_3(self):
        # Initilise database
        connection = sqlite3.connect("stock_market_database.db")
        cursor = connection.cursor()
        cursor.execute(
            """INSERT INTO OwnedStock(owner_id, ticker, average_price, total_vol) VALUES(1, "B", 2, 5)"""
        )
        connection.commit()
        connection.close()
        result = Database().create_transaction(2, 2, 1, 1, 5, "B", 1)
        self.assertNotEqual(result, -1)
        connection = sqlite3.connect("stock_market_database.db")
        cursor = connection.cursor()
        # 1 record for bidder
        cursor.execute("""SELECT * FROM OwnedStock WHERE owner_id = 2""")
        self.assertEqual(cursor.fetchall(), [(2, "B", 1, 5)])
        # No records for asker
        cursor.execute(
            '''SELECT * FROM OwnedStock WHERE owner_id = 1 AND ticker = "B"'''
        )
        self.assertEqual(len(cursor.fetchall()), 0)
        # 1 transaction added
        cursor.execute(
            """SELECT bidder_id, bid_price, asker_id, ask_price, vol, ticker, transaction_price FROM Transactions WHERE transaction_id = ?""",
            (result,),
        )
        self.assertEqual(cursor.fetchall(), [(2, 2, 1, 1, 5, "B", 1)])
        # Reset database
        cursor.execute('''DELETE FROM OwnedStock WHERE ticker = "B"''')
        connection.commit()
        connection.close()

    # Add a transaction where bidder has previous stock and asker has exactly the amount of stock
    # Path: DELETE, UPDATE, UPDATEx2, INSERT
    def test_add_transaction_valid_4(self):
        # Initilise database
        connection = sqlite3.connect("stock_market_database.db")
        cursor = connection.cursor()
        cursor.execute(
            """INSERT INTO OwnedStock(owner_id, ticker, average_price, total_vol) VALUES(1, "B", 2, 5)"""
        )
        cursor.execute(
            """INSERT INTO OwnedStock(owner_id, ticker, average_price, total_vol) VALUES(2, "B", 2, 10)"""
        )
        connection.commit()
        connection.close()
        result = Database().create_transaction(2, 2, 1, 1, 5, "B", 1)
        self.assertNotEqual(result, -1)
        connection = sqlite3.connect("stock_market_database.db")
        cursor = connection.cursor()
        # 1 record for bidder
        cursor.execute("""SELECT * FROM OwnedStock WHERE owner_id = 2""")
        self.assertEqual(cursor.fetchall(), [(2, "B", 1.67, 15)])
        # No records for asker
        cursor.execute(
            '''SELECT * FROM OwnedStock WHERE owner_id = 1 AND ticker = "B"'''
        )
        self.assertEqual(len(cursor.fetchall()), 0)
        # 1 transaction added
        cursor.execute(
            """SELECT bidder_id, bid_price, asker_id, ask_price, vol, ticker, transaction_price FROM Transactions WHERE transaction_id = ?""",
            (result,),
        )
        self.assertEqual(cursor.fetchall(), [(2, 2, 1, 1, 5, "B", 1)])
        # Reset database
        cursor.execute('''DELETE FROM OwnedStock WHERE ticker = "B"''')
        connection.commit()
        connection.close()

    # retrieve_specific_volumn tests

    # Return the specific stock owned by a user when user owns stock in that exchange
    def test_retrieve_specific_stock_valid_1(self):
        result = Database().retrieve_specific_volumn(3, "C")
        self.assertEqual(result, 10)

    # Return the specific stock owned by a user when user owns no stock in that exchange
    def test_retrieve_specific_stock_valid_2(self):
        result = Database().retrieve_specific_volumn(1, "C")
        self.assertEqual(result, 0)

    # Return the specific stock owned by a user when user does not exist
    def test_retrieve_specific_stock_edge_1(self):
        result = Database().retrieve_specific_volumn(10000000, "C")
        self.assertEqual(result, 0)

    # Return the specific stock owned by a user when specific stock does not exist
    def test_retrieve_specific_stock_edge_2(self):
        result = Database().retrieve_specific_volumn(3, "Z")
        self.assertEqual(result, 0)

    # retrieve_balance tests

    # Return the balance of a user
    def test_retrieve_balance_valid(self):
        result = Database().retrieve_balance(3)
        self.assertEqual(result, 100.0)


if __name__ == "__main__":
    unittest.main()
