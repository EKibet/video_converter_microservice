import datetime,jwt,os
from flask import Flask,request

from flask_mysqldb import MySql


server = Flask()
mysql = MySql(server)

server.config["MYSQL_HOST"]=os.environ.get("MYSQL_HOST")
server.config["MYSQL_USER"]=os.environ.get("MYSQL_USER")
server.config["MYSQL_PASSWORD"]=os.environ.get("MYSQL_PASSWORD")
server.config["MYSQL_DB"]=os.environ.get("MYSQL_DB")
server.config["MYSQL_PORT"]=os.environ.get("MYSQL_PORT")

@server.route("/login",methods = ["POST"])
def login():
    auth = request.authorization
    if not auth:
        return "missing credentials",401 
    cur = mysql.connection.cursor()
    res= cur.execute(
        "SELECT email,password FROM user WHERE  email =%S",(auth.username,auth.password)
    )
    if res>0:
        user_row = cur.fetchone()
        email = user_row[0]
        password= user_row[1]
        if auth.username !=email or auth.password !=password:
            return "invalid creds",401
        else:
            return createJWT(auth.username,os.environ.get("JWT_SECRET"),True)
    return "invalid creds",401

def createJWT(username,secret,authz):
    return jwt.encode(
        {
            "username":username,
            "exp": datetime.datetime.now(tz=datetime.timezone.utc)+datetime.timedelta(days=1),
            "iat": datetime.datetime.utcnow(),
            "admin":authz
        },
        secret,
        algorithm="HS256"
    )
@server.route('/validate',method=["POST"])
def validate_jwt(jwt):
    encoded_jwt = request.headers['Authorization']
    if not encoded_jwt:
        return "missign creds",401
    encoded_jwt = encoded_jwt.split(" ")[1]
    try:
        decoded = jwt.decode(
            encoded_jwt,os.environ.get("JWT_SECRET",algorithm=["HS256"])
        
        )
    except:
        return "not authorized",403
    return decoded,200




if __name__ == "__main__":
    server.run(host="0.0.0.0", port=5000)