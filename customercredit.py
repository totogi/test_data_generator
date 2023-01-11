import requests # used by gql GraphQL library
import httpx # for making REST over HTTP/2 requests to the N40 interface
from gql import Client, gql # for making GraphQL requests to Totogi Charging API
from gql.transport.requests import RequestsHTTPTransport
import random

#from IPython.print import JSON
import asyncio
import os
from os import access, environ
import sqlite3
import time
import json
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
import numpy as np


log_file_path = "/home/ec2-user/latency-test/NEW_SCRIPTS/logs/Customercredit.log"
stats_file_path = "/home/ec2-user/latency-test/NEW_SCRIPTS/logs/Stats_Customercredit.log"
db_file_path = "/home/ec2-user/latency-test/NEW_SCRIPTS/Charging.db"
username = 'Totogiusername'
password = 'Totogipassword'
provider_id="e8becf15-7921-34db-802e-820716f1230f"
min_credit = 50 #Min random value amount to credit on hourly basis.
max_credit = 100 #Max random value amount to credit on hourly basis.
min_cnt = 50 #Min random value num to credit on hourly basis.
max_cnt = 100 #Max random value num to credit on hourly basis. Script will take hour wise num from DB and add this random value

#Logger definition for log files
logger = logging.getLogger("Customercredit")
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(log_file_path, maxBytes=10485760, backupCount=50)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
#Logger for stats file
stats_logger = logging.getLogger("Stats_Customercredit")
stats_logger.setLevel(logging.INFO)
stats_handler = RotatingFileHandler(stats_file_path, maxBytes=10485760, backupCount=50)
stats_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stats_handler.setFormatter(stats_formatter)
stats_logger.addHandler(stats_handler)

#Get token
r = requests.post('https://cognito-idp.us-east-1.amazonaws.com/us-east-1_us-east-1_bYrFO4DaR/', 
  json={
    "AuthParameters": {
		"USERNAME": username,
		"PASSWORD": password
	},
	"AuthFlow": "USER_PASSWORD_AUTH",
	"ClientId": "3bsr3p2j5ffn1cf05knuqc03v2"
  }, headers={
    "X-Amz-Target" : "AWSCognitoIdentityProviderService.InitiateAuth",
    "Content-Type" : "application/x-amz-json-1.1"
  })

result = r.json()
if 'AuthenticationResult' in result:
	access_token = r.json()['AuthenticationResult']['AccessToken']
else:
	print(result)
	
	
transport = RequestsHTTPTransport(
    url="https://api.produseast1.totogi.app/graphql", 
    verify=True,
    retries=3,
    headers={'Authorization':access_token})

# Create a GraphQL client using the defined transport
client = Client(transport=transport, fetch_schema_from_transport=True)

#credit account

creditamtquery = gql(
    """
      mutation creditAccount($input: CreditAccountInput!) {
        creditAccount(input: $input) {
        ... on CreditAccountPayload {
          __typename
          account {
            balance {
              customData
              value
              version
            }
            customData
            id
          }
        }
        ... on AccountNotFound {
          errorMessage
          accountId
          errorCode
          providerId
        }
        ... on InvalidField {
          errorMessage
          errorCode
          fieldName
        }
      }
    }

    """
)



#credit amount
now = datetime.now()
conn = sqlite3.connect(db_file_path)
accdata = conn.cursor()
#Select accounts for credit operations
accdata.execute("SELECT Account  FROM charging_account where plan is not null and del_flag is null")
result_full=accdata.fetchall()
#Select count of accounts for credit operation for current hour
hrnow = now.strftime("%H")
hrdata = conn.cursor()
hrdata.execute("SELECT  new_customer FROM call_stats  where HOUR=?",[hrnow])
call_cnt1=hrdata.fetchone()
call_cnt=call_cnt1[0]
randnum = random.randint(min_cnt,max_cnt)
call_cnt=int(call_cnt1[0])+randnum
results = random.sample(result_full,call_cnt)
acc_cnt = 0

for i in results:
    account_id = i[0]
    credit_amount = random.randint(min_credit,max_credit)
    creditamtparams = {
    "input": {
        "providerId" : provider_id,
        "accountId"  : account_id,
        "amount"     : credit_amount
        },
    }
    result = client.execute(creditamtquery, variable_values=creditamtparams)
    acc_cnt += 1
    logger.info('Account credit,{},{}'.format(account_id,credit_amount))
conn.close()
stats_logger.info('Account credit_stats, {}'.format(acc_cnt))
