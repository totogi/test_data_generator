import sqlite3

# Connect to the database
conn = sqlite3.connect("Charging.db")

# Create a cursor object
cursor = conn.cursor()

# Execute an INSERT statement
cursor.execute("INSERT INTO call_stats(  HOUR,voice_onnet,voice_offnet,voice_isd,SMS_onnet,SMS_Offnet,SMS_ISD,data)  VALUES   (?,?,?,?,?,?,?,?)",(1,251,221,22,88,88,88,538))
cursor.execute("INSERT INTO call_stats(  HOUR,voice_onnet,voice_offnet,voice_isd,SMS_onnet,SMS_Offnet,SMS_ISD,data)  VALUES   (?,?,?,?,?,?,?,?)",(2,313,276,28,111,111,111,672))
cursor.execute("INSERT INTO call_stats(  HOUR,voice_onnet,voice_offnet,voice_isd,SMS_onnet,SMS_Offnet,SMS_ISD,data)  VALUES   (?,?,?,?,?,?,?,?)",(3,392,346,35,138,138,138,840))
cursor.execute("INSERT INTO call_stats(  HOUR,voice_onnet,voice_offnet,voice_isd,SMS_onnet,SMS_Offnet,SMS_ISD,data)  VALUES   (?,?,?,?,?,?,?,?)",(4,783,691,69,276,276,276,1680))
cursor.execute("INSERT INTO call_stats(  HOUR,voice_onnet,voice_offnet,voice_isd,SMS_onnet,SMS_Offnet,SMS_ISD,data)  VALUES   (?,?,?,?,?,?,?,?)",(5,1306,1152,115,461,461,461,2800))
cursor.execute("INSERT INTO call_stats(  HOUR,voice_onnet,voice_offnet,voice_isd,SMS_onnet,SMS_Offnet,SMS_ISD,data)  VALUES   (?,?,?,?,?,?,?,?)",(6,3264,2880,288,1152,1152,1152,7000))
cursor.execute("INSERT INTO call_stats(  HOUR,voice_onnet,voice_offnet,voice_isd,SMS_onnet,SMS_Offnet,SMS_ISD,data)  VALUES   (?,?,?,?,?,?,?,?)",(7,6528,5760,576,2304,2304,2304,14000))
cursor.execute("INSERT INTO call_stats(  HOUR,voice_onnet,voice_offnet,voice_isd,SMS_onnet,SMS_Offnet,SMS_ISD,data)  VALUES   (?,?,?,?,?,?,?,?)",(8,8160,7200,720,2880,2880,2880,14400))
cursor.execute("INSERT INTO call_stats(  HOUR,voice_onnet,voice_offnet,voice_isd,SMS_onnet,SMS_Offnet,SMS_ISD,data)  VALUES   (?,?,?,?,?,?,?,?)",(9,8500,7500,750,3000,3000,3000,15000))
cursor.execute("INSERT INTO call_stats(  HOUR,voice_onnet,voice_offnet,voice_isd,SMS_onnet,SMS_Offnet,SMS_ISD,data)  VALUES   (?,?,?,?,?,?,?,?)",(10,8330,7350,735,2940,2940,2940,14700))
cursor.execute("INSERT INTO call_stats(  HOUR,voice_onnet,voice_offnet,voice_isd,SMS_onnet,SMS_Offnet,SMS_ISD,data)  VALUES   (?,?,?,?,?,?,?,?)",(11,7997,7056,706,2822,2822,2822,14112))
cursor.execute("INSERT INTO call_stats(  HOUR,voice_onnet,voice_offnet,voice_isd,SMS_onnet,SMS_Offnet,SMS_ISD,data)  VALUES   (?,?,?,?,?,?,?,?)",(12,5598,4939,494,1976,1976,1976,9878))
cursor.execute("INSERT INTO call_stats(  HOUR,voice_onnet,voice_offnet,voice_isd,SMS_onnet,SMS_Offnet,SMS_ISD,data)  VALUES   (?,?,?,?,?,?,?,?)",(13,5430,4791,479,1916,1916,1916,9582))
cursor.execute("INSERT INTO call_stats(  HOUR,voice_onnet,voice_offnet,voice_isd,SMS_onnet,SMS_Offnet,SMS_ISD,data)  VALUES   (?,?,?,?,?,?,?,?)",(14,4344,3833,383,1533,1533,1533,7666))
cursor.execute("INSERT INTO call_stats(  HOUR,voice_onnet,voice_offnet,voice_isd,SMS_onnet,SMS_Offnet,SMS_ISD,data)  VALUES   (?,?,?,?,?,?,?,?)",(15,3909,3450,345,1380,1380,1380,6899))
cursor.execute("INSERT INTO call_stats(  HOUR,voice_onnet,voice_offnet,voice_isd,SMS_onnet,SMS_Offnet,SMS_ISD,data)  VALUES   (?,?,?,?,?,?,?,?)",(16,4691,4139,414,1656,1656,1656,8279))
cursor.execute("INSERT INTO call_stats(  HOUR,voice_onnet,voice_offnet,voice_isd,SMS_onnet,SMS_Offnet,SMS_ISD,data)  VALUES   (?,?,?,?,?,?,?,?)",(17,5254,4636,464,1854,1854,1854,9272))
cursor.execute("INSERT INTO call_stats(  HOUR,voice_onnet,voice_offnet,voice_isd,SMS_onnet,SMS_Offnet,SMS_ISD,data)  VALUES   (?,?,?,?,?,?,?,?)",(18,5622,4961,496,1984,1984,1984,9921))
cursor.execute("INSERT INTO call_stats(  HOUR,voice_onnet,voice_offnet,voice_isd,SMS_onnet,SMS_Offnet,SMS_ISD,data)  VALUES   (?,?,?,?,?,?,?,?)",(19,4779,4217,422,1687,1687,1687,8433))
cursor.execute("INSERT INTO call_stats(  HOUR,voice_onnet,voice_offnet,voice_isd,SMS_onnet,SMS_Offnet,SMS_ISD,data)  VALUES   (?,?,?,?,?,?,?,?)",(20,4301,3795,379,1518,1518,1518,7590))
cursor.execute("INSERT INTO call_stats(  HOUR,voice_onnet,voice_offnet,voice_isd,SMS_onnet,SMS_Offnet,SMS_ISD,data)  VALUES   (?,?,?,?,?,?,?,?)",(21,2150,1897,190,759,759,759,3795))
cursor.execute("INSERT INTO call_stats(  HOUR,voice_onnet,voice_offnet,voice_isd,SMS_onnet,SMS_Offnet,SMS_ISD,data)  VALUES   (?,?,?,?,?,?,?,?)",(22,1290,1138,114,455,455,455,2277))
cursor.execute("INSERT INTO call_stats(  HOUR,voice_onnet,voice_offnet,voice_isd,SMS_onnet,SMS_Offnet,SMS_ISD,data)  VALUES   (?,?,?,?,?,?,?,?)",(23,774,683,68,273,273,273,1366))
cursor.execute("INSERT INTO call_stats(  HOUR,voice_onnet,voice_offnet,voice_isd,SMS_onnet,SMS_Offnet,SMS_ISD,data)  VALUES   (?,?,?,?,?,?,?,?)",(24,387,342,34,137,137,137,683))
# Commit the transaction
conn.commit()
conn.close()

