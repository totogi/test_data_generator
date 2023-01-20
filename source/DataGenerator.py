import config
import os
import getpass # for prompting for password to use to connect to Totogi
import requests # used by gql GraphQL library
import httpx # for making REST over HTTP/2 requests to the N40 interface
from gql import Client, gql # for making GraphQL requests to Totogi Charging API
from gql.transport.requests import RequestsHTTPTransport
import random
from datetime import datetime
import asyncio
from os import access, environ
import sqlite3
import time
import json
import logging
from logging.handlers import RotatingFileHandler
import numpy as np
now=datetime.now()


#User inputs
charging_url = config.charging_url
provider_id = config.provider_id
mcc = config.mcc
mnc = config.mnc
cognito_url = config.cognito_url
data_session_sr = config.data_session_sr
data_session_er = config.data_session_er
data_session_in = config.data_session_in
username = config.username
password = config.password
#Configuration parameters
script_path = config.script_path
log_file_name = os.path.basename(__file__).replace('.py','')
log_file_path = script_path+"logs/"+log_file_name+".log"
stats_file_path = script_path+"logs/"+"Stats_"+log_file_name+".log"
db_file_path = script_path+"dbfile"+"/Charging.db"

#Logger definition for log files
logger = logging.getLogger(log_file_name)
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(log_file_path, maxBytes=10485760, backupCount=50)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
#Logger for stats file
stats_logger = logging.getLogger("Stats_"+log_file_name)
stats_logger.setLevel(logging.INFO)
stats_handler = RotatingFileHandler(stats_file_path, maxBytes=10485760, backupCount=50)
stats_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stats_handler.setFormatter(stats_formatter)
stats_logger.addHandler(stats_handler)


class EventGeneratorClass:
        def __init__(self):
                self.access_token = None
                self.now = datetime.now()
                self.s = httpx.AsyncClient(http2=True, verify=False)

        #Function to get JWT token
        async def get_token(self):
                payload = {
                        "AuthParameters": {
                                "USERNAME": username,
                                "PASSWORD": password
                        },
                        "AuthFlow": "USER_PASSWORD_AUTH",
                        "ClientId": "3bsr3p2j5ffn1cf05knuqc03v2"
                }
                headers = {
                        "Content-Type": "application/x-amz-json-1.1",
                        "X-Amz-Target": "AWSCognitoIdentityProviderService.InitiateAuth"
                }
                response = await self.s.request("POST", cognito_url, json=payload, headers=headers)
                #print(response)
                token_json = response.json()
                access_token = token_json['AuthenticationResult']['AccessToken']
                return access_token

        #Creating charging initial request
        async def init(self,token, device_id,init_requ_units):
                url = f"{charging_url}/nchf-convergedcharging/v3/chargingData"
                request_time = f"{datetime.now().isoformat()[:-3]}Z"
                payload = {
                        "invocationSequenceNumber": 1,
                        "tenantIdentifier": provider_id,
                        "subscriberIdentifier": device_id,
                        "multipleUnitUsage": [
                                {
                                        "requestedUnit": {"totalVolume": init_requ_units},
                                        "ratingGroup": 300
                                }
                        ],
                        "locationReportingChargingInformation": {"pSCellInformation": {"nrcgi": {
                                                "nrCellId": "11",
                                                "nid": "12",
                                                "plmnId": {
                                                        "mcc": mcc,
                                                        "mnc": mnc
                                                }
                                        }}},
                        "nfConsumerIdentification": {"nodeFunctionality": "SMF"},
                        "invocationTimeStamp": request_time
                }
                headers = {
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {token}"
                }
                #print('init payload %s', str(json.dumps(payload)))

                response = await self.s.request("POST", url, json=payload, headers=headers)
                headers = response.headers
                return_location = None
                if 'location' in headers:
                        return_location = headers['location']

                if response.status_code >= 300:
                        print(f'{response.status_code}: {response.text}. Request payload:')
                        #print(str(json.dumps(payload)))
                else:
                        print(f'{response.status_code}: {response.text}')
                return (return_location, response.status_code)

        #Charging update request
        async def update(self,token, location_header, seq_num, device_id,update_requ_units,up_consumed_units):
                url = f"{charging_url}/nchf-convergedcharging/v3/chargingData/{location_header}/update"
                request_time = f"{datetime.now().isoformat()[:-3]}Z"
                payload = {
                        "invocationSequenceNumber": seq_num,
                        "tenantIdentifier": provider_id,
                        "subscriberIdentifier": device_id,
                        "multipleUnitUsage": [
                                {
                                        "requestedUnit": {"totalVolume": update_requ_units},
                                        "usedUnitContainer": [
                                                {
                                                        "localSequenceNumber": 1,
                                                        "totalVolume": up_consumed_units
                                                }
                                        ],
                                        "ratingGroup": 300
                                }
                        ],
                        "locationReportingChargingInformation": {"pSCellInformation": {"nrcgi": {
                                                "nrCellId": "11",
                                                "nid": "12",
                                                "plmnId": {
                                                        "mcc": mcc,
                                                        "mnc": mnc
                                                }
                                        }}},
                        "nfConsumerIdentification": {"nodeFunctionality": "SMF"},
                        "invocationTimeStamp": request_time
                }
                headers = {
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {token}"
                }
                #print('update payload %s', str(json.dumps(payload)))

                response = await self.s.request("POST", url, json=payload, headers=headers)
                return_location = None
                if 'location' in response.headers:
                        return_location = response.headers['location']

                if response.status_code >= 300:
                        print(f'{response.status_code}: {response.text}')
                else:
                        print(f'{response.status_code}: {response.text}')
                return (return_location, response.status_code)

        #Charging terminate request
        async def terminate(self,token, location_header, seq_num, device_id,tr_consumed_units):
                url = f"{charging_url}/nchf-convergedcharging/v3/chargingData/{location_header}/release"
                request_time = f"{datetime.now().isoformat()[:-3]}Z"
                payload = {
                        "invocationSequenceNumber": seq_num,
                        "tenantIdentifier": provider_id,
                        "subscriberIdentifier": device_id,
                        "multipleUnitUsage": [
                                {
                                        "usedUnitContainer": [
                                                {
                                                        "localSequenceNumber": 2,
                                                        "totalVolume": tr_consumed_units
                                                }
                                        ],
                                        "ratingGroup": 300
                                }
                        ],
                        "locationReportingChargingInformation": {"pSCellInformation": {"nrcgi": {
                                                "nrCellId": "11",
                                                "nid": "12",
                                                "plmnId": {
                                                        "mcc": mcc,
                                                        "mnc": mnc
                                                }
                                        }}},
                        "nfConsumerIdentification": {"nodeFunctionality": "SMF"},
                        "invocationTimeStamp": request_time
                }
                headers = {
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {token}"
                }
                #print('terminate payload %s', str(json.dumps(payload)))

                response = await self.s.request("POST", url, json=payload, headers=headers)

                if response.status_code >= 300:
                        print(f'{response.status_code}: {response.text}')
                else:
                        print(f'{response.status_code}: {response.text}')
                return response.status_code

        #Charging request function called by the main script
        async def consume_data(self,device_id):
                for i in range(1):
                        #This for loop used for continue and break statement below. 
                        #Select random units for initial, update and terminate also validate consumption unit is less the requested units
                        init_requ_units=random.randrange(data_session_sr,data_session_er,data_session_in)
                        #print("init_requ_units " + str(init_requ_units))
                        up_consumed_units=random.randrange(data_session_sr,data_session_er,data_session_in)
                        #print("up_consumed_units " + str(up_consumed_units))
                        if up_consumed_units >= init_requ_units:
                                up_consumed_units = init_requ_units
                        else:
                                up_consumed_units = up_consumed_units
                        #print("up_consumed_units " + str(up_consumed_units))
                        update_requ_units=random.randrange(data_session_sr,data_session_er,data_session_in)
                        #print("Up requ units " + str(update_requ_units))
                        tr_consumed_units=random.randrange(data_session_sr,data_session_er,data_session_in)
                        #print("Used units " + str(tr_consumed_units))
                        if tr_consumed_units >= update_requ_units:
                                tr_consumed_units = update_requ_units
                        else:
                                tr_consumed_units = tr_consumed_units
                        #print("updated cu " + str(tr_consumed_units))
                        #Assign variables to log statistics
                        init_count = 0
                        init_error_count = 0
                        upda_count = 0
                        upda_error_count = 0
                        term_count = 0
                        term_error_count = 0
                        #Get access token and set the variable
                        if self.access_token is None:
                                self.access_token=await self.get_token()
                        (location, status_code) = await self.init(self.access_token, device_id, init_requ_units)
                        init_count += 1
                        logger.info('{},init,{},{}'.format(device_id,status_code,init_requ_units))
                        #Check if token is expired and renew token
                        if status_code == 401:
                                init_error_count += 1
                                print(f"Error calling init: {status_code}")
                                self.access_token=self.get_token()
                        #Exit current loop incase of rating failed error
                        elif status_code >= 400:
                                init_error_count += 1
                                print(f"Error calling init: {status_code}")
                                continue
                        updates_per_session = random.randint(1, 5)
                        for j in range(0, updates_per_session):
                                (location, status_code) = await self.update(self.access_token, location, seq_num=j+2,
                                                                                                device_id=device_id,update_requ_units=update_requ_units,up_consumed_units=up_consumed_units)
                                upda_count += 1
                                time.sleep(1)
                                logger.info('{},upda,{},{},{}'.format(device_id,status_code,update_requ_units,up_consumed_units))
                        #Check if token is expired and renew token
                        if status_code == 401:
                                upda_error_count += 1
                                print(f"Error calling update: {status_code}")
                                self.access_token=await self.get_token()
                        #Break to exit update loop incase of rating failed error 
                        elif status_code >= 400:
                                upda_error_count += 1
                                print(f"Error calling update: {status_code}")
                                break
                        status_code = await self.terminate(self.access_token, location, seq_num=2+updates_per_session
                                                                                                , device_id=device_id,tr_consumed_units=tr_consumed_units)
                        term_count += 1
                        logger.info('{},term,{},{}'.format(device_id,status_code,tr_consumed_units))
                        #Check if token is expired and renew token
                        if status_code == 401:
                                term_error_count += 1
                                print(f"Error calling terminate: {status_code}")
                                self.access_token=await self.get_token()
                        elif status_code >= 400:
                                term_error_count += 1
                                print(f"Error calling tetminate: {status_code}")
                return init_count,init_error_count,upda_count,upda_error_count,term_count,term_error_count

my_object =  EventGeneratorClass()
#Main function to generate the events
async def main():
    conn = sqlite3.connect(db_file_path)
    accdata = conn.cursor()
    #Fetch device details from database a
    accdata.execute("SELECT device FROM charging_account  where plan is not null and del_flag is null ")
    result_full=accdata.fetchall()
    #Fetch hour wise number of calls to be generated
    hrnow = now.strftime("%H")
    hrdata = conn.cursor()
    hrdata.execute("SELECT data FROM call_stats  where HOUR=?",[hrnow])
    call_cnt1=hrdata.fetchone()
    call_cnt=call_cnt1[0]
    #Check if call count is less than devices
    if int(call_cnt) > len(result_full):
        call_cnt = len(result_full)
    #Fetch random samples from the device output
    results = random.sample(result_full,call_cnt)
    all_results = [0,0,0,0,0,0]
    #Loop and generating the events
    for row in results:
        device_id = row[0]
        #print(device_id)
        result = await my_object.consume_data(device_id)
        sums = [all_results[i] + result[i] for i in range(len(all_results))]
        all_results=sums
    #print(all_results)
    stats_logger.info('Data, %s',str(all_results))

if __name__ == "__main__":
    asyncio.run(main())
