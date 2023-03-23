# Tether Gateway

This project allows you to use the cryptocurrency payment gateway in your applications

This project works as an independent service you can easily add this payment service to your applications.

You can also easily make the changes you need in it

To use, just set your own environment variables
The following is the tutorial on how to use this project:
## Setting up

### 1. FastApi Service

In **_.env_** file change the values of the following variables as needed \
for example :

```bash
OAUTH2_ACCESS_IDENTIFY_TOKEN_EXPIRE_MINUTES=432000
OAUTH2_ACCESS_AUTH_TOKEN_EXPIRE_MINUTES=2
OAUTH2_ALGORITHM ="HS256"
OAUTH2_SECRET_KEY="6c7d438d2ea66bc11ee215516bda6f45336930cc2b40eaa96ec009524c20aa49"
SHA_SALT="dd211c31dd2abe6875c25bb570ca71e9523386757d255a4f2155c"
SQLALCHEMY_DATABASE_URL="mysql+pymysql://root:<root_password>@mysql/tether_gateway"
CACHE_URL="redis://redis:6379"

DEPOSIT_ADDRESS= "0x86Ef335A4E07a8A7b9663000c761Ed5836b25958"
WITHDRAW_ADDRESS= "0x86Ef335A4E07a8A7b9663000c761Ed5836b25958"
ENCODED_WITHDRAW_PRIVATE_KEY= "gAAAAABkG1MtzrsWZohPOPtlae7PWv-Lm24qt2DQx7uFxi_fw4RKInDGQaMj8DanbW_X8p8MT_puxypKmWUU7bMUi1sehxfNdj3-iAQ0hZcyKdRteMP5D7W63aO8AxDmXuyc6ossN4Lk0OASZW_rj0cz7S0B7Cawwzi_98fnUHQlnPXLvvGqao0="
```

for create **_ENCODED_WITHDRAW_PRIVATE_KEY_** you can use of pk_security.py file in celery_withdraw directory 
```python
>>> from pk_security import encrypt_private_key
>>> encoded_withdraw_private_key = encrypt_private_key("raw_withdraw_private_key", "<example_password>", "<example_salt>")
>>> print(encoded_withdraw_private_key)
```
### 2. Withdraw Service
In _**celery_withdraw/.env**_ file change the values of the following variables as needed \
for example :

```bash
PROVIDER_1="https://data-seed-prebsc-1-s1.binance.org:8545"
ABI="[]"
CONTRACT="0xa881Fb34dA0e62A84678138590CF792510143D6B"
OAUTH2_ACCESS_IDENTIFY_TOKEN_EXPIRE_MINUTES=432000
OAUTH2_ACCESS_AUTH_TOKEN_EXPIRE_MINUTES=2
SQLALCHEMY_DATABASE_URL="mysql+pymysql://root:<root_password>@mysql/tether_gateway"
CACHE_URL="redis://redis:6379"
PRIVATE_KEY_SALT="<example_salt>"
PASSWORD_PRIVATE_KEY="<example_password>"
```
**_PRIVATE_KEY_SALT_** and **_PASSWORD_PRIVATE_KEY_** variables are the same values in the **_ENCODED_WITHDRAW_PRIVATE_KEY_** generation section (**<example_password>** , **<example_salt>**).


### 3. Deposit Service
In _**celery_deposit/.env**_ file change the values of the following variables as needed \
for example :
```bash
PROVIDER_1="https://data-seed-prebsc-1-s1.binance.org:8545"
ABI= "[]"
TRANSFER_HASH="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
CONTRACT="0xa881Fb34dA0e62A84678138590CF792510143D6B"
TX_EXPIRE_TIME=1440 # minutes
REQUEST_EXPIRE_TIME= 60 # minute
SQLALCHEMY_DATABASE_URL="mysql+pymysql://root:<root_password>@mysql/tether_gateway"
CACHE_URL="redis://redis:6379"
OAUTH2_ACCESS_IDENTIFY_TOKEN_EXPIRE_MINUTES=432000
OAUTH2_ACCESS_AUTH_TOKEN_EXPIRE_MINUTES=2
```

### 4. Transfer Service
In **_celery_transfer/.env_** file change the values of the following variables as needed \
for example :
```bash
SQLALCHEMY_DATABASE_URL="mysql+pymysql://root:<root_password>@mysql/tether_gateway"
CACHE_URL="redis://redis:6379"
OAUTH2_ACCESS_IDENTIFY_TOKEN_EXPIRE_MINUTES=432000
OAUTH2_ACCESS_AUTH_TOKEN_EXPIRE_MINUTES=2
```

### 5. Docker Compose
In **_docker-compose.yml_** file change the values of the following variables as needed \
for example :

`MYSQL_ROOT_PASSWORD`
`MYSQL_USER`
`MYSQL_PASSWORD`
`SQLALCHEMY_DATABASE_URL`

\
for example:
```bash
MYSQL_ROOT_PASSWORD: <root_password>
MYSQL_USER: john
MYSQL_PASSWORD: john_password

SQLALCHEMY_DATABASE_URL: mysql+pymysql://root:<root_password>@mysql/tether_gateway

```
_**Note**: The value of variable **MYSQL_ROOT_PASSWORD** is the same value used in variable **SQLALCHEMY_DATABASE_URL** ( **<root_password>** ) ._ 

## Run

In finally to Run this project:

```bash
  docker compose up
```
## Usage

_After ready docker services, now open this page for API docs:_ \
_http://0.0.0.0/docs  or  http://your-server-ip/docs_


## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## Support

For support, email amirhosein_wyvern@yahoo.com or @xwyvern in telegram .


## License

[MIT](https://choosealicense.com/licenses/mit/)