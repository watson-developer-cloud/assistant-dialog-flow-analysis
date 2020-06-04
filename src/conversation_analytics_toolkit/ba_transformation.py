# (C) Copyright IBM Corp. 2019, 2020.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
import json

def _wa_to_ba_json(row, workspace_name, conversation_id_field):
    row_request = row["request"]
    row_response = row["response"]

    ba_json = {}
    ba_json["event"] = "REQUEST_RESPONSE" 
     
    if len(row.request_timestamp)<23:
        timestring = row.request_timestamp[:19]
        ba_json["timestamp"] = int(datetime.datetime.strptime(timestring, "%Y-%m-%dT%H:%M:%S").timestamp()*1000)
    else:
        timestring = row.request_timestamp[:23]
        ba_json["timestamp"] = int(datetime.datetime.strptime(timestring, "%Y-%m-%dT%H:%M:%S.%f").timestamp()*1000)

    ba_json["log_id"]=row["log_id"]

    ba_json["data"] = {}
    ba_json["data"]["input"] = { "text": row_request["input"]["text"] }
    ba_json["data"]["intents"] = row_response["intents"]
    ba_json["data"]["entities"] = row_response["entities"]
    ba_json["data"]["output"] = {
        "text" : row_response["output"]["text"],
        "nodes_visited": row_response["output"]["nodes_visited"]
    }

    if 'branch_exited' in row_response["context"]["system"]:
        ba_json["data"]["output"]["branch_exited"] = row_response["context"]["system"]["branch_exited"]
        ba_json["data"]["output"]["branch_exited_reason"] = row_response["context"]["system"]["branch_exited_reason"]

    ba_json["data"]["context"] = {}
    ba_json["data"]["context"]["conversation_id"] = row_response["context"][conversation_id_field]
    if "user_id" in row_response["context"]:
        ba_json["data"]["context"]["user_id"] = row_response["context"]["user_id"]
    if "workspace_name" in row_response["context"]:
        ba_json["data"]["context"]["workspace_name"] = row_response["context"]["workspace_name"]
    elif workspace_name != None:
        ba_json["data"]["context"]["workspace_name"] = workspace_name
    if "not_handled" in row_response["context"]:
        # optional. Boolean. Default value is false.
        ba_json["data"]["context"]["not_handled"] = row_response["context"]["not_handled"]

    ba_json["data"]["context"]["input_type"] = "text"
    return ba_json

# create row for sql table
def _wa_to_ba_transformer(row, tenant_id, workspace_name, conversation_id_field):
    ba_row=[]

    ba_row.append(row["log_id"])
    event_json = _wa_to_ba_json(row, workspace_name, conversation_id_field)
    ba_row.append(json.dumps(event_json))
    ba_row.append(int(event_json["timestamp"]))
    ba_row.append(tenant_id)

    return ba_row

def transform_wa_to_ba(df_logs, tenant_id, workspace_name=None, conversation_id_field="conversation_id"):
    """
    Transforms WA log dataframe format to BA array format
    """
    # iterate to get list of rows for sql table
    ba_array = []
    for index, row in df_logs.iterrows():
        ba_array.append(_wa_to_ba_transformer(row, tenant_id, workspace_name, conversation_id_field))
    return ba_array

# store ba_array to the database
def store_ba_to_mysql(ba_array, db_credentials, tenant_id, raw_data_table='analyticsRecords'):
    """
    Persist ba array to MySQL
    """
    import pymysql
    # establish a connection
    db_connection = pymysql.connect(
        host=db_credentials["host"],
        port=db_credentials["port"],
        user=db_credentials["user"],
        password=db_credentials["password"],
        db=db_credentials["database"],
        charset="utf8")

    # insert data to sql table
    try:
        with db_connection.cursor() as db_cursor:
            field_list="(id, event_json, epoch, tenant_id)"
            insert_stmt = "INSERT INTO "+raw_data_table+" "+field_list+" VALUES (%s,%s,%s,%s)"
            db_cursor.executemany(insert_stmt,ba_array)
    except Exception as e:
            print(e)
            print("Failure in database connection")

    db_connection.commit()
    db_connection.close()


def store_ba_to_postgres(ba_array, db_credentials, tenant_id, raw_data_table='analyticsRecords'):
    """
    Persist ba array to MySQL
    """

    import psycopg2
    # establish a connection
    #db_credentials['dbname'] = db_credentials["database"]
    #del db_credentials["database"]
    if db_credentials.setdefault('ssl', False): # setdefault() - Returns the value of the specified key. If the key does not exist: insert the key, with the specified value
        db_credentials['sslmode']='require'
    del db_credentials['ssl']

    db_connection = psycopg2.connect(**db_credentials)

    # insert data to sql table
    try:
        with db_connection.cursor() as db_cursor:
            field_list="(id, event_json, epoch, tenant_id)"
            insert_stmt = "INSERT INTO "+raw_data_table+" "+field_list+" VALUES (%s,%s,%s,%s)"
            #db_cursor.executemany(insert_stmt,ba_array)
            psycopg2.extras.execute_batch(db_cursor, insert_stmt, ba_array, page_size=1000)

    except Exception as e:
            print(e)
            print("Failure in database connection")

    db_connection.commit()
    db_connection.close()
