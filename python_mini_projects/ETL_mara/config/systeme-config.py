import mara_db.config

mara_db.config.databases["postgres"] = mara_db.dbs.PostgreSQLDB(
    host="localhost", user="user", password="password", database="mydb"
)
