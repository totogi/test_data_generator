import sqlite3

# Connect to the database
conn = sqlite3.connect("Charging.db")

# Create a cursor object
cursor = conn.cursor()

# Define the table schema
table_schema = """
CREATE TABLE charging_account (
    Account TEXT NOT NULL, 
    Device TEXT ,
    Amount INTEGER,
    plan Text,
    del_flag TEXT
);
"""

# Execute the CREATE TABLE statement
cursor.execute(table_schema)

# Commit the transaction
conn.commit()

# Close the connection
conn.close()
