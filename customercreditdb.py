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
from datetime import datetime

import numpy as np


username = 'jana.reddy+data@totogi.com'
password = 'Kingkong1!'

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

# get provider ID

query = gql(
  """
  query getCurrentUser {
    getCurrentUser {
      providerId
      userId
      email
      name
      roleGroupMemberships
      phoneNumber
      jobTitle
      softwareMfaEnabled
    }
  }
  """
)
result = client.execute(query)
if 'getCurrentUser' in result:
  provider_id = result['getCurrentUser']['providerId']
  print(f"Provider ID: {provider_id}")
else:
  print(result)



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



#credite amount
now = datetime.now()
conn = sqlite3.connect("/home/ec2-user/latency-test/subs_plan_creation/Charging.db")
accdata = conn.cursor()
accdata.execute("SELECT Account  FROM charging_account where plan is not null and del_flag is null")
result_full=accdata.fetchall()
hrnow = now.strftime("%H")
hrdata = conn.cursor()
hrdata.execute("SELECT  new_customer FROM call_stats  where HOUR=?",[hrnow])
call_cnt1=hrdata.fetchone()
call_cnt=call_cnt1[0]
randnum = random.randint(50,100)
call_cnt=int(call_cnt1[0])+randnum
results = random.sample(result_full,call_cnt)


for i in results:
    account_id = i[0]
    credit_amount = random.randint(10, 50)
    creditamtparams = {
    "input": {
        "providerId" : provider_id,
        "accountId"  : account_id,
        "amount"     : credit_amount
        },
    }
    result = client.execute(creditamtquery, variable_values=creditamtparams)
    f = open('/home/ec2-user/latency-test/customer_onboarding/customercredit.log', 'a')
    f.write(str(account_id) +"," + str(credit_amount) +  "\n")
    f.close()
conn.close()
