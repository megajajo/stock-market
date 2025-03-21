# --------------------------------------------------------------------------------------------------------------
# database.py
# Last modified: 20/3/25                        By: Kirsten Else
# Module to allow access to the database
# Create Table Commands:
# CREATE TABLE Client(
#   client_id INTEGER PRIMARY KEY,
#   username TEXT NOT NULL UNIQUE,
#   password TEXT NOT NULL,
#   email TEXT NOT NULL,
#   balance REAL NOT NULL CHECK(balance >= 0.00) DEFAULT 0.00,
#   first_names TEXT,
#   last_name TEXT);

# CREATE TABLE StockMarket(
#   stock_id INTEGER PRIMARY KEY,
#   ticker TEXT NOT NULL);

# CREATE TABLE OwnedStock(
#   owner_id INTEGER,
#   stock_id INTEGER,
#   average_price REAL NOT NULL CHECK(average_price > 0.00),
#   total_vol INTEGER NOT NULL CHECK(total_vol > 0),
#   PRIMARY KEY(owner_id, stock_id),
#   FOREIGN KEY (owner_id)
#       REFERENCES Client (client_id)
#       ON DELETE CASCADE
#       ON UPDATE NO ACTION,
#   FOREIGN KEY (stock_id)
#       REFERENCES StockMarket(stock_id)
#       ON DELETE CASCADE
#       ON UPDATE NO ACTION) WITHOUT ROWID;

# CREATE TABLE Transactions(
#   transaction_id INTEGER PRIMARY KEY,
#   bidder_id INTEGER NOT NULL,
#   bid_price REAL NOT NULL CHECK(bid_price > 0.00),
#   asker_id INTEGER NOT NULL,
#   ask_price REAL NOT NULL CHECK(ask_price > 0.00),
#   vol INTEGER NOT NULL CHECK(vol > 0),
#   stock_id INTEGER NOT NULL,
#   time_stamp TEXT NOT NULL,
#   CHECK(bid_price >= ask_price),
#   FOREIGN KEY (bidder_id)
#       REFERENCES Client (client_id)
#       ON DELETE CASCADE
#       ON UPDATE NO ACTION,
#   FOREIGN KEY (asker_id)
#       REFERENCES Client (client_id)
#       ON DELETE CASCADE
#       ON UPDATE NO ACTION,
#   FOREIGN KEY (stock_id)
#       REFERENCES StockMarket(stock_id)
#       ON DELETE CASCADE
#       ON UPDATE NO ACTION);
# ----------------------------------------------------------------------------------------------------------------------------------------
import sqlite3
from datetime import datetime

# Each query should open a database connection, create a cursor and then close the connection, to prevent stale data
class Database:

    def __init__(self):
        pass


    # create_transaction: Takes information from a bid and ask and store into the database
    # Pre: Data must be validated - asker has the required stock, bidder has the required balance, bid_price >= ask_price, vol > 0
    # Post: transaction_id if successful, -1 if not
    def create_transaction(self, bidder_id, bid_price, asker_id, ask_price, vol, stock_id):
        connection = sqlite3.connect('stock_market_database.db')
        cursor = connection.cursor()
        # Success tracks that all updates are made correctly
        success = True
        # Start 
        cursor.execute('''BEGIN TRANSACTION;''')
        # Update owned_stock for seller
        cursor.execute('''SELECT total_vol FROM OwnedStock WHERE owner_id = ? AND stock_id = ? ;''', (asker_id, stock_id))
        previous_vol = cursor.fetchone()
        # Error in validation
        if previous_vol == None:
            success = False
        # Delete record if no stock remaining
        elif previous_vol[0] == vol:
            cursor.execute('''DELETE FROM OwnedStock WHERE owner_id = ? AND stock_id = ? ;''', (asker_id, stock_id))
            if cursor.rowcount != 1:
                success = False
        # Else update the record
        else:
            cursor.execute('''UPDATE OwnedStock SET total_vol = ? WHERE owner_id = ? AND stock_id = ? ;''', (previous_vol[0] - vol, asker_id, stock_id))
            if cursor.rowcount != 1:
                success = False
        # Update owned_stock for buyer
        cursor.execute('''SELECT total_vol, average_price FROM OwnedStock WHERE owner_id = ? AND stock_id = ? ;''', (bidder_id, stock_id))
        previous_vol_price = cursor.fetchone()
        # Buyer has no previous stock so insert
        if previous_vol_price == None:
            cursor.execute('''INSERT INTO OwnedStock (owner_id, stock_id, average_price, total_vol) VALUES (?, ?, ?, ?); ''', (bidder_id, stock_id, ask_price, vol))
            if cursor.rowcount != 1:
                success = False
        # Buyer has previous stock so update average price
        else:
            new_average_price = ((previous_vol_price[0] * previous_vol_price[1] + ask_price * vol) / (previous_vol_price[0] + vol))
            cursor.execute('''UPDATE OwnedStock SET total_vol = ?, average_price = ? WHERE owner_id = ? AND stock_id = ? ;''', (previous_vol_price[0] + vol, round(new_average_price, 2), bidder_id, stock_id))
            if cursor.rowcount != 1:
                success = False
        # Update balances of buyer and seller
        cursor.execute('''SELECT balance, client_id FROM CLIENT WHERE client_id = ? OR client_id = ? ;''', (bidder_id, asker_id))
        r = cursor.fetchall()
        if len(r) != 2:
                success = False
        else:
            for i in r:
                if i[1] == bidder_id:
                    cursor.execute('''UPDATE Client SET balance = ? WHERE client_id = ? ;''', (i[0] - ask_price * vol, bidder_id))
                    if cursor.rowcount != 1:
                        success = False
                else:
                    cursor.execute('''UPDATE Client SET balance = ? WHERE client_id = ? ;''', (i[0] + ask_price * vol, asker_id))
                    if cursor.rowcount != 1:
                        success = False
        # Create transaction in database
        cursor.execute('''INSERT INTO Transactions (bidder_id, bid_price, asker_id, ask_price, vol, stock_id, time_stamp) VALUES(?, ?, ?, ?, ?, ?, ?);''', (bidder_id, bid_price, asker_id, ask_price, vol, stock_id, str(datetime.now())))
        result = cursor.lastrowid
        if cursor.rowcount == 0 or result == None:
            success = False
            result = -1
        if success:
            cursor.execute('''COMMIT TRANSACTION;''')
        else:
            cursor.execute('''ROLLBACK;''')
        connection.commit()
        connection.close()
        return result

    # retrieve_specific_volumn: Takes a user and a specific stock market and returns the number of owned stock
    # Post: total_vol from record with key (user_id, stock_id)
    def retrieve_specific_volumn(self, owner_id, stock_id):
        connection = sqlite3.connect('stock_market_database.db')
        cursor = connection.cursor()
        cursor.execute('''SELECT total_vol FROM OwnedStock WHERE owner_id = ? AND stock_id = ?''', (owner_id, stock_id))
        result = cursor.fetchall()
        connection.commit()
        connection.close()
        if len(result) == 0:
            return 0
        else:
            return result[0][0]
    
    # retrieve_balance: Takes a user and returns their balance
    # Pre: client_id exists in clients
    # Post: balance from record with key client_id
    def retrieve_balance(self, client_id):
        connection = sqlite3.connect('stock_market_database.db')
        cursor = connection.cursor()
        cursor.execute('''SELECT balance FROM Clients WHERE client_id = ?''', (client_id, ))
        result = cursor.fetchall()
        connection.commit()
        connection.close()
        return result[0][0]

