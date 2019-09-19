host = "127.0.0.1"
dbname = "dbname"
setname = "setname"
username = "username"
password = "password"
ip_db_path = "./data/埃文科技IP数据库.dat"

DB_URL = "mongodb://{}:{}@{}:27017/{}?authMechanism=SCRAM-SHA-1".format(username, password, host, dbname)
