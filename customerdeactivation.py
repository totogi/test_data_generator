import getpass # for prompting for password to use to connect to Totogi
import requests # used by gql GraphQL library
import httpx # for making REST over HTTP/2 requests to the N40 interface
from gql import Client, gql # for making GraphQL requests to Totogi Charging API
from gql.transport.requests import RequestsHTTPTransport
import random

#from IPython.print import JSON
import json
from datetime import datetime
import asyncio
from os import access, environ
import sqlite3
import time
import json
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
import numpy as np


log_file_path = "/home/ec2-user/latency-test/NEW_SCRIPTS/logs/Customerdeactivation.log"
stats_file_path = "/home/ec2-user/latency-test/NEW_SCRIPTS/logs/Stats_Customerdeactivation.log"
db_file_path = "/home/ec2-user/latency-test/NEW_SCRIPTS/Charging.db"
username = 'Totogiusername'
password = 'Totogipassword'
provider_id="e8becf15-7921-34db-802e-820716f1230f"
min_account = 10 #Min random value num to activate on hourly basis.
max_account = 25 #Max random value num to activate on hourly basis. Script will take hour wise num from DB and add this random value
#Logger definition for log files
logger = logging.getLogger("Customerdeactivation")
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(log_file_path, maxBytes=10485760, backupCount=50)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
#Logger for stats file
stats_logger = logging.getLogger("Stats_Customerdeactivation")
stats_logger.setLevel(logging.INFO)
stats_handler = RotatingFileHandler(stats_file_path, maxBytes=10485760, backupCount=50)
stats_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stats_handler.setFormatter(stats_formatter)
stats_logger.addHandler(stats_handler)

#Get token
body = {
	"AuthParameters": {
		"USERNAME": username,
		"PASSWORD": password
	},
	"AuthFlow": "USER_PASSWORD_AUTH",
	"ClientId": "3bsr3p2j5ffn1cf05knuqc03v2"
}
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

#Delete account

deleteaccquery = gql(
    """
    mutation DeleteAccount($input: DeleteAccountInput!) {
      deleteAccount(input: $input) {
        ... on AccountHasReferences {
			errorMessage
			providerId
			errorCode
			accountId
		}
        ... on AccountNotFound {
			errorMessage
			providerId
			accountId
			errorCode
		}
        ... on DeleteAccountPayload {
			__typename
			deletedAccountId
			parentAccount {
        providerId
        id
        friendsAndFamily
        customData
            }
		}
      }
    }

    """
)


  
#delete device
  
deletedevquery = gql(
    """
      mutation DeleteDevice($input: DeleteDeviceInput!) {
        deleteDevice(input: $input) {
        ... on DeviceNotFound {
			errorMessage
			providerId
			errorCode
			deviceId
		}
        ... on DeleteDevicePayload {
			__typename
			deletedDeviceId
			account {
				providerId
				id
			}
		}
      }
    }

    """
)





#Delete account and device
now = datetime.now()
#get account and device details for deletion
conn = sqlite3.connect(db_file_path)
accdata = conn.cursor()
accdata.execute("SELECT Account,device  FROM charging_account where plan is not null and del_flag is null")
result_full=accdata.fetchall()
#get number of accounts of be deactivated for the current hour
hrnow = now.strftime("%H")
hrdata = conn.cursor()
hrdata.execute("SELECT  remove_customer FROM call_stats  where HOUR=?",[hrnow])
call_cnt1=hrdata.fetchone()
call_cnt=call_cnt1[0]
randnum = random.randint(min_account,max_account)
call_cnt=int(call_cnt1[0])+randnum
#call_cnt=2
results = random.sample(result_full,call_cnt)
acc_del = 0
dev_del = 0
#Loop and delete
for i in results:
    account_id = i[0]
    device_id = i[1]

    deltedevparams = {
    "input": {
        "providerId" : provider_id,
        "accountId" : account_id,
        "deviceId" : device_id
        },
    }
    result = client.execute(deletedevquery, variable_values=deltedevparams)
    dev_del += 1
    print(result)
    deleteaccparams = {
    "input": {
        "providerId" : provider_id,
        "accountId"  : account_id
        },
    }
    result = client.execute(deleteaccquery, variable_values=deleteaccparams)
    acc_del += 1
    accdata.execute("update charging_account set del_flag=? where account=?",('Y',account_id))
    conn.commit()
    logger.info('customer deactivation,{},{}'.format(account_id,device_id))
conn.close()
stats_logger.info('Deactivation_stats, {},{}'.format(acc_del,dev_del))
