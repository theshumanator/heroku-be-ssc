import psycopg2
import asyncio
# from ssc.dbconfig import user, password, database
from ssc.Invites.invites import get_user_id
from passlib.hash import pbkdf2_sha256
from ssc.dbconnection import getDBConnection


def add_user(username, password):
    # connection = None
    user_added = False
    res={}
    try:
        connection = getDBConnection()
        cursor = connection.cursor()

        encrypted_pw = pbkdf2_sha256.hash(password)

        cursor.execute("""INSERT INTO users (username, password)
                       VALUES (%s, %s) RETURNING *;"""
                       , (username, encrypted_pw))
        connection.commit()
        if (cursor.rowcount != 0):
            user_added = True
        else:
            res["error"] = "Invalid username and/or password"
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
        res["error"] = str(error)
    finally:
        if (connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")
        res["user_added"] = user_added
        return res


def fetch_users():
    res = {}
    list_of_users = []
    # connection = None
    try:
        connection = getDBConnection()
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM users;")
        user_records = cursor.fetchall()

        for row in user_records:
            list_of_users.append({'username': row[1]})

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
        res["error"] = str(error)
    finally:
        if (connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")
        if ((len(list_of_users) == 0) & ("error" not in res)):
            res["error"] = "There are no users in the system"
        res["users"] = list_of_users
        return res


def fetch_user_workspaces(username):
    res = {}
    list_of_user_workspaces = []
    # connection = None
    try:
        connection = getDBConnection()
        cursor = connection.cursor()

        loop = asyncio.new_event_loop()
        user_id = loop.run_until_complete(get_user_id(username))

        if user_id == -1:
            res["error"] = "User does not exist in the system"
        else:
            user_workspaces_sql = "SELECT w.name, wu.is_admin " \
                                  "FROM workspaces w " \
                                  "JOIN workspace_users wu ON wu.workspace_id = w.workspace_id " \
                                  "WHERE wu.user_id =%s "

            cursor.execute(user_workspaces_sql, (user_id,))
            user_workspaces = cursor.fetchall()

            for row in user_workspaces:
                list_of_user_workspaces.append({'workspace': row[0],
                                                'is_admin': row[1]})

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
        res["error"] = str(error)
    finally:
        # closing database connection.
        if (connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")
        res["workspaces"] = list_of_user_workspaces
        return res
