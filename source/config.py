from os import access, environ

username = environ['TOTOGI_USERNAME'] #Depending upon the number of activations, either script to be executed in nohup mode or cron).
password = environ['TOTOGI_PASSWORD'] #Depending upon the number of activations, either script to be executed in nohup mode or cron).
cognito_url = environ['TOTOGI_COGNITO_URL']
gql_url = environ['TOTOGI_GQL_URL']
charging_url = environ['TOTOGI_CHARGING_URL']
provider_id="e8becf15-7921-34db-802e-820716f1230f"
mcc = "214"
mnc = "03"
min_account = 10 #Min random value num to activate/deactivate on hourly basis. Script will take hour wise num from DB and add this random value
max_account = 25 #Max random value num to activate/deactivate on hourly basis. Script will take hour wise num from DB and add this random value
plan_version_list=["7f7ffcd6-4d5f-4f11-a034-fce87014b293","36b473fe-5589-48ce-a3a7-383b9911a386","7881e3d6-31ed-4783-9be1-29b82861bba8","ee7c5d2b-8370-42c5-b462-3d6bb9eedce3","71ce1978-0eb2-43b2-819b-53fd9ce86fbe","b41f30a1-5308-4464-8737-1a1af510f79f","07ea7d16-8d32-451b-8a36-2b143e40b23f","0984d867-d27a-42ed-8013-3cbf4031141b","731ef6b6-c7ae-4a7d-b2ef-43fcda627688","59306757-cbe2-42a7-b4ee-5e3aa2b294cc"] #add plan versions to be considered for activation
addon_plan_version_list=["9f26d548-1e2a-4dcd-afe1-c31df80cd420","c9c440ab-9fa2-41a2-836d-adf3a2c70fb6","aae61a97-9629-4b93-a1b6-7983569fb018","2610e651-c798-4f05-8798-70c646821fdb","a36b583d-2851-4a8a-b9db-f40c7ced04fb","1961be66-036c-4795-bfcd-f962354f057e"] #Add on plan versions IDs for add on activation
account_prefix = 'Account1' #Starting account id prefix
device_series = 690000000  #Starting device id series
min_credit = 1000
max_credit = 5000
min_cnt = 50 #Min random value num to credit on hourly basis.
max_cnt = 100 #Max random value num to credit on hourly basis. Script will take hour wise num from DB and add this random value
data_session_sr = 1048576     #This will be starting range of the data session volume
data_session_er = 104857600   #This will be ending range of the data session volumne
data_session_in = 1048576     #This will be data volume increment units to select the random consumption units
routeinfo = "ORSP"
mnpinfo = "ORSP"
offnet = "ORCP"
voice_session_sr = 100     #This will be starting range of the voice call 
voice_session_er = 1000   #This will be ending range of the voice call
voice_session_in = 2     #This will be voice call units to select the random consumption units
called_num_sr = 695000000 #Called num start range 
called_num_er = 695999999 #Called num end range 
isd_num_sr = 11111111 #ISD calling start series
isd_num_er = 99999999 #ISD calling end series
sms_session_sr = 1     #This will be starting range of the voice call
sms_session_er = 20   #This will be ending range of the voice call
sms_session_in = 2     #This will be voice call units to select the random consumption units


#Configuration parameters
script_path = "/home/ec2-user/latency-test/VERSION3/"
