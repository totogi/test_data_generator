import config
import sqlite3

script_path = config.script_path
db_path = script_path+"dbfile/Charging.db"
# Connect to the database
conn = sqlite3.connect(db_path)

# Create a cursor object
cursor = conn.cursor()

# Define the table schema
table_schema = """
CREATE TABLE call_stats(
    HOUR TEXT NOT NULL, 
    voice_onnet INTEGER ,
    voice_offnet INTEGER,
    voice_isd INTEGER,
    SMS_onnet INTEGER,
    SMS_Offnet INTEGER,
    SMS_ISD INTEGER,
    data INTEGER,
    new_customer INTEGER,
    remove_customer INTEGER
);
"""

# Execute the CREATE TABLE statement
cursor.execute(table_schema)

# Commit the transaction
conn.commit()

# Close the connection
conn.close()
