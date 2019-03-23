import psycopg2
from ssc.dbconnection import getDBConnection
from requests_toolbelt.multipart import decoder


def add_audio_key(audio_key, session_id):
    try:

        connection = getDBConnection()
        cursor = connection.cursor()

        add_audio_key_sql = "INSERT INTO audio_keys (audio_key, session_id)" \
                            "VALUES (%s, %s)"

        cursor.execute(add_audio_key_sql, (audio_key, session_id))
        connection.commit()

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
        return False

    finally:
        # closing database connection.
        if (connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")

        return 'Key Added Successfully'
