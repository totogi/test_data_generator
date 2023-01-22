# Test Data Generator scripts to create accounts, devices, subscriptions and 5G calls


1. Launch Amazon EC2 instance using "testedrgenerator.yml" Cloudformation template. t2.micro instance will be sufficient for the load upto 100K subscribers
2. Setup python

```shell
sudo yum update -y
sudo yum install git -y
sudo yum install zlib-devel bzip2 bzip2-devel readline-devel sqlite sqlite-devel openssl-devel xz xz-devel libffi-devel gcc
```
3. Install pyenv

```
curl -L https://github.com/pyenv/pyenv-installer/raw/master/bin/pyenv-installer | bash
```

4. Add to your .bashrc in $HOME path (for e.g /home/ec2-user/.bashrc)

```
export PYENV_ROOT="$HOME/.pyenv"
command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
````

5. Install development tools so compiling works
```
sudo yum group install "Development Tools"
```
6. Install Python 3.9.13 and create a virtual environment
```
pyenv install 3.9.13
pyenv virtualenv 3.9.13 testdata
pyenv global testdata
```

7. Clone repo in home directory (/home/ec2-user)
```
git clone https://github.com/totogi/test_data_generator.git
```

8. Create log and dbfile directory

```
mkdir /home/ec2-user/test_data_generator/logs /home/ec2-user/test_data_generator/dbfile
```

9. Set your username & password in the environment
```
export TOTOGI_USERNAME="infra-user@domain.com"
export TOTOGI_PASSWORD="infraPassword"
export TOTOGI_GQL_URL="https://api.produseast1.totogi.app/graphql"
export TOTOGI_CHARGING_URL="https://5g.produseast1.api.totogi.com"
export TOTOGI_COGNITO_URL="https://cognito-idp.us-east-1.amazonaws.com/us-east-1_us-east-1_bYrFO4DaR/"
```

10. Install requirements
```
pip3 install -r test_data_generator/requirements.txt
pip3 install requests gql requests_toolbelt
```

11. Execute below scripts to create the database and tables
```
cd /home/ec2-user/test_data_generator/source/
python createtable_ca.py
python createtable_cs.py
python dbinsertcallstats.py
```
12. Update config.py with below parameters.
```
provider_id
mcc
mnc
routeinfo
mnpinfo
offnet
Update remaining parameters as per your requirement. 
```
13. Execute below script and select appropriate menu options to create the customer, generate the events etc. 

```
python testedrgenerator.py
```



