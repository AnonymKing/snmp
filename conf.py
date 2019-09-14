host = "127.0.0.1"
db = "dbname"
username = "username"
password = "password"

DB_URL = "mongodb://{}:{}@{}:27017/{}?authMechanism=SCRAM-SHA-1".format(username, password, host, db)
