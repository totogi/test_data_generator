import config
import os
import getpass # for prompting for password to use to connect to Totogi
import requests # used by gql GraphQL library
import httpx # for making REST over HTTP/2 requests to the N40 interface
from gql import Client, gql # for making GraphQL requests to Totogi Charging API
from gql.transport.requests import RequestsHTTPTransport
from graphql import DocumentNode
import random
import json
from datetime import datetime
import asyncio
from os import access, environ
import sqlite3
import time
import logging
from logging.handlers import RotatingFileHandler
import numpy as np
from services.parallel_task_processor_service import ParallelTaskProcessorService
from services.async_gql_client_service import AsyncGqlClientService


#Configuration parameters
username =  config.username
password = config.password
provider_id= config.provider_id
cognito_url = config.cognito_url
gql_url = config.gql_url
min_account = config.min_account
max_account = config.max_account
plan_version_list= config.plan_version_list
account_prefix = config.account_prefix
device_series = config.device_series
min_credit = config.min_credit
max_credit = config.max_credit
edr_gen_mode = config.edr_gen_mode
edr_cnt = config.edr_cnt

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

# Parallel Processing
max_parallel_tasks = config.max_parallel_tasks
parallel_tasks_enabled = config.parallel_tasks_enabled
parallel_task_processor = ParallelTaskProcessorService(parallel_tasks_enabled, max_parallel_tasks)

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
async_client = AsyncGqlClientService(gql_url, access_token)

#create account

createaccquery = gql(
    """
    mutation createAccount($input: CreateAccountInput!) {
      createAccount(input: $input) {
        ... on InvalidField {
          errorMessage
          fieldName
          errorCode
        }
        ... on AccountAlreadyExists {
          errorMessage
          errorCode
          accountId
        }
        ... on AccountNotFound {
          errorMessage
          accountId
          errorCode
          providerId
        }
        ... on CreateAccountPayload {
          __typename
          account {
            id
            providerId
          }
        }
      }
    }

    """
)



#credit amount

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



#create device

createdevquery = gql(
    """
    mutation createDevice($input: CreateDeviceInput!) {
      createDevice(input: $input) {
        ... on CreateDevicePayload {
          __typename
          device {
            providerId
            id
            customData
            account {
              id
              providerId
            }
          }
        }
        ... on DeviceAlreadyExists {
          errorMessage
          errorCode
          deviceId
        }
        ... on AccountNotFound {
          errorMessage
          providerId
          errorCode
          accountId
        }
        ... on InvalidField {
          errorMessage
          fieldName
          errorCode
        }
      }
    }

    """
)

######## looping

#Creating account, crediting amount, creating device and subscribing to plan
now = datetime.now()
#get max of the account nuber
conn = sqlite3.connect(db_file_path)
accdata = conn.cursor()
accdata.execute("SELECT COALESCE(max(substr(Account,-7)),0) FROM charging_account")
maxacc1=accdata.fetchone()
maxacc=int(maxacc1[0])+1
#get number of accounts of be activated for the current hour
if edr_gen_mode=="DB":
    hrnow = now.strftime("%H")
    hrdata = conn.cursor()
    hrdata.execute("SELECT new_customer FROM call_stats  where HOUR=?",[hrnow])
    call_cnt1=hrdata.fetchone()
    randnum = random.randint(min_account,max_account)
    call_cnt=int(call_cnt1[0])+randnum
else:
    call_cnt=edr_cnt
acc_cnt = 0
dev_cnt = 0

async def execute_graphql(graphql_doc: DocumentNode, graphql_variables: dict, post_execute_db_query: str, post_execute_db_query_values: tuple, print_result: bool = False) -> None:
    result = await async_client.execute(graphql_doc, variable_values=graphql_variables)
    if print_result:
        print(result)
    
    accdata.execute(post_execute_db_query, post_execute_db_query_values)
    conn.commit()


async def onboard_customer(i: int) -> None:
    account_id = account_prefix+str(i).zfill(7)
    device_id = str(device_series+i)
    credit_amount = random.randint(min_credit, max_credit)
    base_input = {
        "providerId" : provider_id,
        "accountId" : account_id
    }
    createaccparams = {"input": base_input,}
    await execute_graphql(createaccquery, createaccparams, "insert into charging_account (Account) values (?)", (account_id,), True)
    acc_cnt += 1
    
    creditamtparams = {"input": (base_input | {"amount" : credit_amount}),}
    await execute_graphql(creditamtquery, creditamtparams, "update charging_account set Amount=? where account=?", (credit_amount,account_id))
    
    version_id=random.choice(plan_version_list)
    subsplanparams = {
    "input" : (base_input | {
      "planVersionId" : version_id
      #,
      #"overrides"     : [
      #   {"name" : "purchase fee", "value" : 200},
        # {"name" : "TemplateService3", "value" : "{ \"recurring units\" : 100 }" }
      #]
        })
    }
    await execute_graphql(subsplanquery, subsplanparams, "update charging_account set plan=? where account=?", (version_id,account_id))

    createdevparams = {"input" : (base_input | {"deviceId" : device_id})}
    await execute_graphql(createdevquery, createdevparams, "update charging_account set Device=? where account=?", (device_id,account_id))
    dev_cnt += 1
    
    logger.info(f"customer onboarding,{account_id},{device_id},{credit_amount},{version_id}")


async def main():
    for i in range(maxacc,maxacc+call_cnt):
        parallel_task_processor.process_task(onboard_customer(i))
    parallel_task_processor.process_pending_tasks()
    conn.close()
    stats_logger.info(f"Onboarding_stats, {acc_cnt},{dev_cnt}")


asyncio.run(main())
