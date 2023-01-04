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
conn = sqlite3.connect("/home/ec2-user/latency-test/subs_plan_creation/Charging.db")
accdata = conn.cursor()
accdata.execute("SELECT Account  FROM charging_account where plan is not null and del_flag is null")
result_full=accdata.fetchall()
hrnow = now.strftime("%H")
hrdata = conn.cursor()
hrdata.execute("SELECT  new_customer FROM call_stats  where HOUR=?",[hrnow])
call_cnt1=hrdata.fetchone()
call_cnt=call_cnt1[0]
randnum = random.randint(100,150)
call_cnt=int(call_cnt1[0])+randnum
results = random.sample(result_full,call_cnt)
conn.close()

for i in results:
    account_id = i[0]
    plan_version_list=["9f26d548-1e2a-4dcd-afe1-c31df80cd420","c9c440ab-9fa2-41a2-836d-adf3a2c70fb6","aae61a97-9629-4b93-a1b6-7983569fb018","2610e651-c798-4f05-8798-70c646821fdb","a36b583d-2851-4a8a-b9db-f40c7ced04fb","1961be66-036c-4795-bfcd-f962354f057e"]
    version_id=random.choice(plan_version_list)
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
    f = open('/home/ec2-user/latency-test/customer_onboarding/customeraddon.log', 'a')
    f.write(str(account_id) +"," + str(version_id) +  "\n")
    f.close()
