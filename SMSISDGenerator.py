from SMSISDGeneratorClass import *
import sqlite3
import asyncio
from datetime import datetime
import time
now = datetime.now()
import random
my_object = SMSISDGeneratorClass()

async def main():
    conn = sqlite3.connect("/home/ec2-user/latency-test/subs_plan_creation/Charging.db")
    accdata = conn.cursor()
    accdata.execute("SELECT device FROM charging_account  where plan is not null and del_flag is null ")
    result_full=accdata.fetchall()
    hrnow = now.strftime("%H")
    hrdata = conn.cursor()
    hrdata.execute("SELECT  SMS_ISD FROM call_stats  where HOUR=?",[hrnow])
    call_cnt1=hrdata.fetchone()
    call_cnt=call_cnt1[0]
    if int(call_cnt) > len(result_full):
        call_cnt = len(result_full)
    results = random.sample(result_full,call_cnt)
    access_token = await my_object.get_token()
    #print(results)
    all_results = [0,0,0,0,0,0]
    for row in results:
        device_id = row[0]
        print(device_id)
        result = await my_object.consume_SMSisd(device_id,access_token)
        #print(result)
        time.sleep(2)
        sums = [all_results[i] + result[i] for i in range(len(all_results))]
        all_results=sums
    print(all_results)
    f = open('/home/ec2-user/latency-test/FINAL_SCRIPTS/SMSisdGenerator.log', 'a')
    f.write( 'SMSisd, ' + datetime.now().strftime("%d/%m/%Y %H:%M:%S")+ ' , ' + str(all_results) + "\n")
    f.close()

if __name__ == "__main__":
    asyncio.run(main())
