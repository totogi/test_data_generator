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


#User inputs
username =  config.username
password = config.password
provider_id= config.provider_id
cognito_url = config.cognito_url
gql_url = config.gql_url
min_account = config.min_account
max_account = config.max_account
addon_plan_version_list=config.addon_plan_version_list

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

#Get access token
body = {
        "AuthParameters": {
                "USERNAME": username,
                "PASSWORD": password
        },
        "AuthFlow": "USER_PASSWORD_AUTH",
        "ClientId": "3bsr3p2j5ffn1cf05knuqc03v2"
}
r = requests.post(cognito_url,
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
        access_token = result['AuthenticationResult']['AccessToken']
else:
        pass

transport = RequestsHTTPTransport(
    url=gql_url,
    verify=True,
    retries=3,
    headers={'Authorization':access_token})

# Create a GraphQL client using the defined transport
client = Client(transport=transport, fetch_schema_from_transport=True)


#subscriber to plan_id

subsplanquery = gql(
    """
mutation subscribeToPlan($input: SubscribeToPlanVersionInput!) {
  subscribeToPlan(input: $input) {
    ... on SubscribeToPlanVersionValidationFailed {
      errorMessage
      errorCode
    }
    ... on InvalidField {
      errorMessage
      fieldName
      errorCode
    }
    ... on AccountNotFound {
      errorMessage
      providerId
      errorCode
      accountId
    }
    ... on PlanVersionIsNotAssignable {
      errorMessage
      providerId
      planVersionId
      errorCode
    }
    ... on PlanVersionNotFound {
      errorMessage
      planVersionId
      providerId
      errorCode
    }
    ... on SubscribeToPlanVersionPayload {
      __typename
      subscribedPlanVersion {
        to
        from
        planVersion {
          version
          state
          id
        }
      }
      account {
        customData
        id
        activePlanVersions {
          from
          to
          planVersion {
            version
            state
            id
          }
        }
        archivedPlanVersions {
          to
          from
          planVersion {
            version
            state
            id
          }
        }
        balance {
          version
          value
          customData
        }
        inactivePlanVersions {
          to
          planVersion {
            state
            version
            id
          }
          from
        }
      }
    }
  }
}

    """
)


# Addon activation 
now = datetime.now()
conn = sqlite3.connect(db_file_path)
#get max of the account number
accdata = conn.cursor()
accdata.execute("SELECT Account  FROM charging_account where plan is not null and del_flag is null")
result_full=accdata.fetchall()
#get number of accounts tddon o be activated for the current hour
hrnow = now.strftime("%H")
hrdata = conn.cursor()
hrdata.execute("SELECT  new_customer FROM call_stats  where HOUR=?",[hrnow])
call_cnt1=hrdata.fetchone()
call_cnt=call_cnt1[0]
randnum = random.randint(min_account,max_account)
call_cnt=int(call_cnt1[0])+randnum
results = random.sample(result_full,call_cnt)
conn.close()
pl_cnt = 0
for i in results:
    account_id = i[0]
    version_id=random.choice(addon_plan_version_list)
    subsplanparams = {
    "input" : {
      "providerId"    : provider_id,
      "accountId"     : account_id,
      "planVersionId" : version_id
      #,
      #"overrides"     : [
       #   {"name" : "purchase fee", "value" : 200},
         # {"name" : "TemplateService3", "value" : "{ \"recurring units\" : 100 }" }
      #]
        }
    }
    result = client.execute(subsplanquery, variable_values=subsplanparams)
    pl_cnt += 1
    logger.info('Addon activation,{},{}'.format(account_id,version_id))
stats_logger.info('Addon_stats, {}'.format(pl_cnt))
