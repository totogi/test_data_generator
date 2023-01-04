import multiprocessing
import getpass # for prompting for password to use to connect to Totogi
import requests # used by gql GraphQL library
import httpx # for making REST over HTTP/2 requests to the N40 interface
#from gql import Client, gql # for making GraphQL requests to Totogi Charging API
#from gql.transport.requests import RequestsHTTPTransport

#from IPython.display import JSON
import json
from datetime import datetime
import asyncio
from os import access, environ
import sqlite3
import random
import time
import json
import logging
from datetime import datetime
import numpy as np
import csv

class VoiceISDGeneratorClass:
    def __init__(self):
	    self.now = datetime.now()
	    self.s = httpx.AsyncClient(http2=True, verify=False)
	    self.base_url = "https://5g.produseast1.api.totogi.com"
	    self.provider_id="e8becf15-7921-34db-802e-820716f1230f"
	    self.mcc = 214 #470 #234
	    self.mnc = "03"

    async def get_token(self):
        url = "https://cognito-idp.us-east-1.amazonaws.com/us-east-1_us-east-1_bYrFO4DaR/"

        payload = {
        "AuthParameters": {
        "USERNAME": "jana.reddy+data@totogi.com",
        "PASSWORD": "Kingkong1!"
        },
        "AuthFlow": "USER_PASSWORD_AUTH",
        "ClientId": "3bsr3p2j5ffn1cf05knuqc03v2"
        }
        headers = {
        "Content-Type": "application/x-amz-json-1.1",
        "X-Amz-Target": "AWSCognitoIdentityProviderService.InitiateAuth"
        }

        #print('Getting access token')
        response = await self.s.request("POST", url, json=payload, headers=headers)
        token_json = response.json()
        #print(token_json)
        access_token = token_json['AuthenticationResult']['AccessToken']
        #print('Retrieved access token')
        return access_token


    async def init(self,token, device_id,init_requ_units,called_number):
        url = f"{self.base_url}/nchf-convergedcharging/v3/chargingData"
        print(url)
        request_time = f"{datetime.now().isoformat()[:-3]}Z"
        payload = {
        "invocationSequenceNumber": 1,
        "tenantIdentifier": self.provider_id,
        "subscriberIdentifier": device_id,
        "multipleUnitUsage": [
        {
        "requestedUnit": {"time": init_requ_units},
        "ratingGroup": 100
        }
        ],
        "iMSChargingInformation": {
        "calledPartyAddress": called_number
        },
        "locationReportingChargingInformation": {"pSCellInformation": {"nrcgi": {
        "nrCellId": "11",
        "nid": "12",
        "plmnId": {
        "mcc": self.mcc,
        "mnc": self.mnc
        }
        }}},
        "nfConsumerIdentification": {"nodeFunctionality": "SMF"},
        "invocationTimeStamp": request_time
        }
        headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
        }
        print('init payload %s', str(json.dumps(payload)))
        response = await self.s.request("POST", url, json=payload, headers=headers)
        headers = response.headers
        return_location = None
        if 'location' in headers:
            return_location = headers['location']
        if response.status_code >= 300:
            print(f'{response.status_code}: {response.text}. Request payload:')
            print(str(json.dumps(payload)))
        else:
            print(f'{response.status_code}: {response.text}')
        return (return_location, response.status_code)

    async def update(self,token, location_header, seq_num, device_id,update_requ_units,up_consumed_units,called_number):
        url = f"{self.base_url}/nchf-convergedcharging/v3/chargingData/{location_header}/update"
        request_time = f"{datetime.now().isoformat()[:-3]}Z"
        payload = {
        "invocationSequenceNumber": seq_num,
        "tenantIdentifier": self.provider_id,
        "subscriberIdentifier": device_id,
        "multipleUnitUsage": [
        {
        "requestedUnit": {"time": update_requ_units},
        "usedUnitContainer": [
        {
        "localSequenceNumber": 1,
        "time": up_consumed_units
        }
        ],
        "ratingGroup": 100
        }
        ],
        "iMSChargingInformation": {
        "calledPartyAddress": called_number
        },
        "locationReportingChargingInformation": {"pSCellInformation": {"nrcgi": {
        "nrCellId": "11",
        "nid": "12",
        "plmnId": {
        "mcc": self.mcc,
        "mnc": self.mnc
        }
        }}},
        "nfConsumerIdentification": {"nodeFunctionality": "SMF"},
        "invocationTimeStamp": request_time
        }
        headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
        }
        print('update payload %s', str(json.dumps(payload)))
        response = await self.s.request("POST", url, json=payload, headers=headers)
        return_location = None
        if 'location' in response.headers:
            return_location = response.headers['location']
        if response.status_code >= 300:
            print(f'{response.status_code}: {response.text}')
        else:
            print(f'{response.status_code}: {response.text}')
        return (return_location, response.status_code)

    async def terminate(self,token, location_header, seq_num, device_id,tr_consumed_units,called_number):
        url = f"{self.base_url}/nchf-convergedcharging/v3/chargingData/{location_header}/release"
        request_time = f"{datetime.now().isoformat()[:-3]}Z"
        payload = {
        "invocationSequenceNumber": seq_num,
        "tenantIdentifier": self.provider_id,
        "subscriberIdentifier": device_id,
        "multipleUnitUsage": [
        {
        "usedUnitContainer": [
        {
        "localSequenceNumber": 2,
        "time": tr_consumed_units
        }
        ],
        "ratingGroup": 100
        }
        ],
        "iMSChargingInformation": {
        "calledPartyAddress": called_number
        },
        "locationReportingChargingInformation": {"pSCellInformation": {"nrcgi": {
        "nrCellId": "11",
        "nid": "12",
        "plmnId": {
        "mcc": self.mcc,
        "mnc": self.mnc
        }
        }}},
        "nfConsumerIdentification": {"nodeFunctionality": "SMF"},
        "invocationTimeStamp": request_time
        }
        headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
        }
        print('terminate payload %s', str(json.dumps(payload)))
        response = await self.s.request("POST", url, json=payload, headers=headers)
        if response.status_code >= 300:
            print(f'{response.status_code}: {response.text}')
        else:
            print(f'{response.status_code}: {response.text}')
        return response.status_code


    async def consume_voiceisd(self,device_id,access_token):
        init_requ_units=random.randrange(100, 1000,2)
        print("init_requ_units " + str(init_requ_units))
        up_consumed_units=random.randrange(100, 1000,2)
        print("up_consumed_units " + str(up_consumed_units))
        if up_consumed_units >= init_requ_units:
            up_consumed_units = init_requ_units
        else:
            up_consumed_units = up_consumed_units
        print("up_consumed_units " + str(up_consumed_units))
        update_requ_units=random.randrange(100, 1000,2)
        print("Up requ units " + str(update_requ_units))
        tr_consumed_units=random.randrange(100, 1000,2)
        print("Used units " + str(tr_consumed_units))
        if tr_consumed_units >= update_requ_units:
            tr_consumed_units = update_requ_units
        else:
            tr_consumed_units = tr_consumed_units
        print("updated cu " + str(tr_consumed_units))
        with open('/home/ec2-user/latency-test/FINAL_SCRIPTS/countrycode.csv', 'r') as ccode:
            reader = csv.reader(ccode)
            data = list(reader)
        isd = random.choice(data)
        isdprefix = isd[0]
        called_number = str(isdprefix) + str(random.randint(11111111, 99999999))
        init_count = 0
        init_error_count = 0
        (location, status_code) = await self.init(access_token, device_id, init_requ_units,called_number)
        init_count += 1
        f = open('/home/ec2-user/latency-test/FINAL_SCRIPTS/voiceisd.log', 'a')
        f.write(device_id + " , " + datetime.now().strftime("%d/%m/%Y %H:%M:%S") +" ,init, " + str(status_code) + " , " + str(init_requ_units) + " ," +"\n")
        f.close()
        if status_code >= 400:
            init_error_count += 1
            print(f"Error calling init: {status_code}")
        updates_per_session = random.randint(1, 5)
        upda_count = 0
        upda_error_count = 0
        for j in range(0, updates_per_session):
            (location, status_code) = await self.update(access_token, location, seq_num=j+2,
            device_id=device_id,update_requ_units=update_requ_units,up_consumed_units=up_consumed_units,called_number=called_number)
            upda_count += 1
            time.sleep(1)
            f = open('/home/ec2-user/latency-test/FINAL_SCRIPTS/voiceisd.log', 'a')
            f.write(device_id + " , " + datetime.now().strftime("%d/%m/%Y %H:%M:%S")+" ,upda, " + str(status_code) + " , " + str(update_requ_units) + "," + str(up_consumed_units) + "\n")
            f.close()
        if status_code >= 400:
            upda_error_count += 1
            print(f"Error calling update: {status_code}")
        term_count = 0
        term_error_count = 0
        status_code = await self.terminate(access_token, location, seq_num=2+updates_per_session
        , device_id=device_id,tr_consumed_units=tr_consumed_units,called_number=called_number)
        term_count += 1
        f = open('/home/ec2-user/latency-test/FINAL_SCRIPTS/voiceisd.log', 'a')
        f.write(device_id + " , " + datetime.now().strftime("%d/%m/%Y %H:%M:%S")+", term, " + str(status_code) +","+ str(tr_consumed_units) +","+  "\n")
        f.close()
        if status_code >= 400:
            term_error_count += 1
            print(f"Error calling terminate: {status_code}")
        return init_count,init_error_count,upda_count,upda_error_count,term_count,term_error_count

