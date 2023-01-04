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





#print account

def print_account(provider_id, account_id):
  query = gql(
      """
  query getAccount(
    $providerId: ID!,
    $accountId: ID!
  ) {
    getAccount(
      providerId: $providerId,
      accountId: $accountId
    ) {
      ... on AccountNotFound {
        errorMessage
        providerId
        errorCode
        accountId
      }
      ... on Account {
        id
        customData
        providerId
        balance {
          customData
          value
          version
        }
        activePlanVersions{
          from
          to
          planVersion{
            id
            version
            planServices{
              balanceName
            }
          }
        }
        archivedPlanVersions{
          from
          to
          planVersion{
            id
            version
            planServices{
              balanceName
            }
          }
        },
              inactivePlanVersions{
                  from
                  to
                  planVersion{
                      id
                      version
            planServices{
                          balanceName
                      }
                  }
              }
      }
    }
  }      
      """
  )
  params = {
    "providerId"    : provider_id,
    "accountId"     : account_id
  }
  
######## looping

#Creating account, crediting amount, creating device and subscribing to plan
now = datetime.now()
conn = sqlite3.connect("/home/ec2-user/latency-test/subs_plan_creation/Charging.db")
accdata = conn.cursor()
accdata.execute("SELECT max(substr(Account,-7)) FROM charging_account")
maxacc1=accdata.fetchone()
maxacc=int(maxacc1[0])+1
hrnow = now.strftime("%H")
hrdata = conn.cursor()
hrdata.execute("SELECT new_customer FROM call_stats  where HOUR=?",[hrnow])
call_cnt1=hrdata.fetchone()
randnum = random.randint(10,25)
call_cnt=int(call_cnt1[0])+randnum


for i in range(maxacc,maxacc+call_cnt):
    account_id = "Account"+str(i).zfill(7)
    device_id = str(695100000+i)
    credit_amount = random.randint(1000, 5000)
    createaccparams = {
    "input": {
        "providerId" : provider_id,
        "accountId" : account_id
        },
    }
    result = client.execute(createaccquery, variable_values=createaccparams)
    print(result)
    accdata.execute("insert into charging_account (Account) values (?)",(account_id,))
    conn.commit()
    creditamtparams = {
    "input": {
        "providerId" : provider_id,
        "accountId"  : account_id,
        "amount"     : credit_amount
        },
    }
    result = client.execute(creditamtquery, variable_values=creditamtparams)
    accdata.execute("update charging_account set Amount=? where account=?",(credit_amount,account_id))
    conn.commit()
    plan_version_list=["7f7ffcd6-4d5f-4f11-a034-fce87014b293","36b473fe-5589-48ce-a3a7-383b9911a386","7881e3d6-31ed-4783-9be1-29b82861bba8","ee7c5d2b-8370-42c5-b462-3d6bb9eedce3","71ce1978-0eb2-43b2-819b-53fd9ce86fbe","b41f30a1-5308-4464-8737-1a1af510f79f","07ea7d16-8d32-451b-8a36-2b143e40b23f","0984d867-d27a-42ed-8013-3cbf4031141b","731ef6b6-c7ae-4a7d-b2ef-43fcda627688","59306757-cbe2-42a7-b4ee-5e3aa2b294cc"]
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
    accdata.execute("update charging_account set plan=? where account=?",(version_id,account_id))
    conn.commit()

    createdevparams = {
    "input" : {
      "providerId"    : provider_id,
      "accountId"     : account_id,
      "deviceId"      : device_id
        }
    }
    result = client.execute(createdevquery, variable_values=createdevparams)
    accdata.execute("update charging_account set Device=? where account=?",(device_id,account_id))
    conn.commit()
    f = open('/home/ec2-user/latency-test/customer_onboarding/customeronboarding.log', 'a')
    f.write(account_id +"," + device_id + "," + str(credit_amount) +"," + version_id + "\n")
    f.close()
conn.close()
