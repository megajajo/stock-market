# --------------------------------------------------------------------------------------------------------------
# database.py
# Last modified: 5/5/25                        By: Kirsten Else
# Module to test database functions
# Key test info:    Clients - 1. A = Seller, 2. B = Buyer, 3. C, 4. D, 5. F, 8. X
#                   OwnedStock - Seller owns A, C owns 10 C, D owns 10 A and 10 C
#                   Transactions - A bidder C asker once, D bider A asker, E bidder and asker once each - All on market C
# Notes on invalid tests - Cannot create a test to check the below as these are errors from the database
#   ownedStock is successfully inserted, deleted or updated on lines 76, 84, 98, 110
#   balance is successfully updated on lines 131, 138
#   transactions are inserted on lines 145
#   duplicate email or usernames are used in create_client due to database errors at execution
#   duplicate (owner_id, ticker) are used in create_owned_stock due to database errors at execution
#   invalid owner_id in create_owned_stock due to database errors at execution
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

    # stock does not exist
    def test_add_transaction_invalid_1(self):
        result = Database().create_transaction(
            2, 2, 1, 1, 5, "PleaseDoNotUseThisStock", 1
        )
        self.assertEqual(-1, result)

    # asker_id does not exist
    def test_add_transaction_invalid_2(self):
        result = Database().create_transaction(2, 2, 100000, 1, 5, "B", 1)
        self.assertEqual(-1, result)

    # asker_id does not own stock
    def test_add_transaction_invalid_3(self):
        result = Database().create_transaction(2, 2, 8, 1, 5, "B", 1)
        self.assertEqual(-1, result)

    # bidder_id does not exist
    def test_add_transaction_invalid_4(self):
        result = Database().create_transaction(2000000, 2, 1, 1, 5, "B", 1)
        self.assertEqual(-1, result)

    # retrieve_specific_volumn tests

    # Return the specific stock owned by a user when user owns stock in that exchange
    def test_retrieve_specific_stock_valid_1(self):
        result = Database().retrieve_specific_stock(3, "C")
        self.assertEqual(result, 10)

    # Return the specific stock owned by a user when user owns no stock in that exchange
    def test_retrieve_specific_stock_valid_2(self):
        result = Database().retrieve_specific_stock(1, "C")
        self.assertEqual(result, 0)

    # Return the specific stock owned by a user when user does not exist
    def test_retrieve_specific_stock_invalid_1(self):
        result = Database().retrieve_specific_stock(10000000, "C")
        self.assertEqual(result, 0)

    # Return the specific stock owned by a user when specific stock does not exist
    def test_retrieve_specific_stock_invalid_2(self):
        result = Database().retrieve_specific_stock(3, "Z")
        self.assertEqual(result, 0)

    # retrieve_balance tests

    # Return the balance of a user
    def test_retrieve_balance_valid(self):
        result = Database().retrieve_balance(3)
        self.assertEqual(result, 100.0)

    # user does not exist
    def test_retrieve_balance_invalid(self):
        result = Database().retrieve_balance(10000000)
        self.assertEqual(result, 0)

    # is_username_taken tests

    # Test that database returns true for usernames not in the database
    def test_is_username_taken_valid_1(self):
        result = Database().is_username_taken("PleaseNeverUseThisUsername")
        self.assertTrue(result)

    # Test that database returns false for usernames in the database
    def test_is_username_taken_valid_2(self):
        result = Database().is_username_taken("A")
        self.assertFalse(result)

    # is_email_taken tests

    # Test that database returns true for emails not in the database
    def test_is_email_taken_valid_1(self):
        result = Database().is_email_taken("PleaseNeverUseThisEmail")
        self.assertTrue(result)

    # Test that database returns false for usernames in the database
    def test_is_email_taken_valid_2(self):
        result = Database().is_email_taken("a@a.com")
        self.assertFalse(result)

    # create_client tests

    # Test that the database returns the correct client_id when a client is created
    def test_create_client_valid_1(self):
        result = Database().create_client(
            "PleaseNeverUseThisUsername", "PleaseNeverUseThisEmail"
        )
        connection = sqlite3.connect("stock_market_database.db")
        cursor = connection.cursor()
        cursor.execute(
            """SELECT client_id FROM Client WHERE username = ? AND email = ?;""",
            ("PleaseNeverUseThisUsername", "PleaseNeverUseThisEmail"),
        )
        self.assertEqual(result, cursor.fetchall()[0][0])
        cursor.execute("""DELETE FROM Client WHERE client_id = ?;""", (result,))
        connection.commit()
        connection.close()

    # Test that the database returns the correct client_id when a client is created with first names
    def test_create_client_valid_2(self):
        result = Database().create_client(
            "PleaseNeverUseThisUsername", "PleaseNeverUseThisEmail", "First"
        )
        connection = sqlite3.connect("stock_market_database.db")
        cursor = connection.cursor()
        cursor.execute(
            """SELECT client_id FROM Client WHERE username = ? AND email = ? AND first_names = ?;""",
            ("PleaseNeverUseThisUsername", "PleaseNeverUseThisEmail", "First"),
        )
        self.assertEqual(result, cursor.fetchall()[0][0])
        cursor.execute("""DELETE FROM Client WHERE client_id = ?;""", (result,))
        connection.commit()
        connection.close()

    # Test that the database returns the correct client_id when a client is created with last name
    def test_create_client_valid_3(self):
        result = Database().create_client(
            "PleaseNeverUseThisUsername", "PleaseNeverUseThisEmail", last_name="Last"
        )
        connection = sqlite3.connect("stock_market_database.db")
        cursor = connection.cursor()
        cursor.execute(
            """SELECT client_id FROM Client WHERE username = ? AND email = ? AND last_name = ?;""",
            ("PleaseNeverUseThisUsername", "PleaseNeverUseThisEmail", "Last"),
        )
        self.assertEqual(result, cursor.fetchall()[0][0])
        cursor.execute("""DELETE FROM Client WHERE client_id = ?;""", (result,))
        connection.commit()
        connection.close()

    # Test that the database returns the correct client_id when a client is created with first and last names
    def test_create_client_valid_4(self):
        result = Database().create_client(
            "PleaseNeverUseThisUsername", "PleaseNeverUseThisEmail", "First", "Last"
        )
        connection = sqlite3.connect("stock_market_database.db")
        cursor = connection.cursor()
        cursor.execute(
            """SELECT client_id FROM Client WHERE username = ? AND email = ? AND first_names = ? AND last_name = ?;""",
            ("PleaseNeverUseThisUsername", "PleaseNeverUseThisEmail", "First", "Last"),
        )
        self.assertEqual(result, cursor.fetchall()[0][0])
        cursor.execute("""DELETE FROM Client WHERE client_id = ?;""", (result,))
        connection.commit()
        connection.close()

    # account_from_email tests

    # Test that the database returns the client_id and username from a valid email
    def test_account_from_email_valid_1(self):
        result = Database().account_from_email("a@a.com")
        self.assertEqual(result, (1, "A"))

    # Test that the database returns the correct null values for an invalid email
    def test_account_from_email_valid_2(self):
        result = Database().account_from_email("PleaseNeverUseThisEmail")
        self.assertEqual(result, (-1, ""))

    # retrieve_transactions_stock tests

    # Test that the database returns records when the stock has transactions
    def test_retrieve_transactions_stock_valid_1(self):
        result = Database().retrieve_transactions_stock("C")
        self.assertEqual(len(result), 4)

    # Test that the database returns no records when the stock has no transactions
    def test_retrieve_transactions_stock_valid_2(self):
        result = Database().retrieve_transactions_stock("PleaseNeverUseThisTicker")
        self.assertEqual(result, [])

    # retrieve_transactions_user tests

    # Test that the database returns records when the client is the bidder
    def test_retrieve_transactions_user_valid_1(self):
        result = Database().retrieve_transactions_user(4)
        self.assertEqual(
            result,
            [
                (30, 4, 2.0, 1, 1.0, 5, "C", "2025-04-29 11:00:15.364292", 2.0),
            ],
        )

    # Test that the database returns records when the client is the asker
    def test_retrieve_transactions_user_valid_2(self):
        result = Database().retrieve_transactions_user(3)
        self.assertEqual(
            result,
            [
                (29, 1, 2.0, 3, 1.0, 5, "C", "2025-04-29 10:56:15.364292", 2.0),
            ],
        )

    # Test that the database returns records when the clients has been an asker and bidder
    def test_retrieve_transactions_user_valid_3(self):
        result = Database().retrieve_transactions_user(5)
        self.assertEqual(
            result,
            [
                (71, 5, 3.0, 1, 1.0, 1, "C", "2025-04-29 14:46:55.933437", 3.0),
                (72, 1, 3.0, 5, 1.0, 1, "C", "2025-04-29 14:47:55.933437", 3.0),
            ],
        )

    # Test that the database returns no records when the client has performed no transactions
    def test_retrieve_transactions_user_valid_4(self):
        result = Database().retrieve_transactions_user(8)
        self.assertEqual(result, [])

    # No transactions returns for an invalid client
    def test_retrieve_transactions_user_invalid(self):
        result = Database().retrieve_transactions_user(10000000000)
        self.assertEqual(result, [])

    # retrieve_stock tests

    # Tests that the database returns records when the user owns stock in one market
    def test_retrieve_stock_valid_1(self):
        result = Database().retrieve_stock(3)
        self.assertEqual(
            result,
            [
                ("C", 1.0, 10),
            ],
        )

    # Tests that the database returns records when the user owns stock in multiple markets
    def test_retrieve_stock_valid_2(self):
        result = Database().retrieve_stock(4)
        self.assertEqual(result, [("A", 2.0, 10), ("C", 2.0, 10)])

    # Tests that the database returns records when the user owns no stock
    def test_retrieve_stock_valid_3(self):
        result = Database().retrieve_stock(2)
        self.assertEqual(result, [])

    # Tests that the database retuns no records when the user does not exist
    def test_retrieve_stock_invalid(self):
        result = Database().retrieve_stock(10000000000)
        self.assertEqual(result, [])

    # create_owned_stock tests

    # Tests that stock is created
    def test_create_owned_stock_valid(self):
        result = Database().create_owned_stock(1, "B", 10)
        self.assertTrue(result)
        connection = sqlite3.connect("stock_market_database.db")
        cursor = connection.cursor()
        cursor.execute(
            """SELECT * FROM ownedStock WHERE owner_id = 1 AND ticker = 'B' AND total_vol = 10;""",
        )
        self.assertEqual(1, len(cursor.fetchall()))
        cursor.execute(
            """DELETE FROM ownedStock WHERE owner_id = 1 AND ticker = 'B'""",
        )
        connection.commit()
        connection.close()


if __name__ == "__main__":
    unittest.main()
