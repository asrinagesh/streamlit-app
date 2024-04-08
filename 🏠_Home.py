import requests
import re
import pandas as pd
import streamlit as st
import webbrowser
import time

from pathlib import Path
from sqlalchemy import create_engine, text

LOGO_PATH = Path(__file__).parent / "images" / "logo.png"
DEFAULT_DATABASE = "Prod READ-ONLY"
HOST = "http://ec2-52-72-247-170.compute-1.amazonaws.com"
st.session_state["HOST"] = "http://ec2-52-72-247-170.compute-1.amazonaws.com"
final_response = ""

def get_all_database_connections(api_url):
    try:
        response = requests.get(api_url)
        response_data = response.json()
        return {entry["alias"]: entry["id"] for entry in response_data} if response.status_code == 200 else {}  # noqa: E501
    except requests.exceptions.RequestException:
        return {}

def add_database_connection(api_url, connection_data):
    try:
        response = requests.post(api_url, json=connection_data)
        return response.json() if response.status_code == 200 else None
    except requests.exceptions.RequestException:
        return None

def answer_question(api_url, db_connection_id, question):
    request_body = {
        "evaluate": True,
        "llm_config": {
            "llm_name": "gpt-4-turbo-preview"
        },
        "prompt": {
            "text": question,
            "db_connection_id": db_connection_id,
        }        
    }
    try:
        with requests.post(api_url, json=request_body, stream=True) as response:
            response.raise_for_status()
            for chunk in response.iter_content(chunk_size=2048):
                if chunk:
                    response = chunk.decode("utf-8")
                    # print("OG RESPONSE: ")
                    # print(response)
                    # print("\n\n\n")

                    if ("Final Answer:" in response and "```sql" in response):
                        response = response.replace("Final Answer:", "Final Answer:\n")
                        global final_response
                        final_response = response
                    # elif ("Action: SqlDbQuery" in response):
                    #     response = response.replace("Action: SqlDbQuery", "Action: SqlDbQuery\n")
                    #     start_index_sql_query = response.find("Action Input: ")
                    #     start_index_sql_query = start_index_sql_query + len("Action Input: ")
                    #     response = response[:start_index_sql_query] + "\n```sql\n" + response[start_index_sql_query:] + "```"                             
                    elif ("UNSIGNED" in response or "PRIMARY" in response):
                        response = ""

                    # print("Modified RESPONSE: ")
                    # print(response)
                    # print("\n\n\n")
                    yield response + "\n"
                    time.sleep(0.1)                
    except requests.exceptions.RequestException as e:
        st.error(f"Connection failed due to {e}.")

def test_connection(url):
    try:
        response = requests.get(url)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def create_button_link(text, url):
    button_clicked = st.sidebar.button(text)
    if button_clicked:
        webbrowser.open_new_tab(url)

def find_key_by_value(dictionary, target_value):
    for key, value in dictionary.items():
        if value == target_value:
            return key
    return None

def execute_sql(sql):
    engine = create_engine('mysql+pymysql://read_worldnet:brIVcCUQxUPjNOSVbDdh3DHfqRCfG0S@tms-prod.cluster-cakvi1wq42an.us-east-1.rds.amazonaws.com:8421/tms')
    connection = engine.connect()
    data = connection.execute(text(sql))

    if data:
        df = pd.DataFrame(data.fetchall())

    global final_response
    final_response = ""

    csv = df.to_csv(index=False).encode('utf-8')

    return df, csv

WAITING_TIME_TEXTS = [
    ":wave: Hello. Please, give me a few moments and I'll be back with your answer.",  # noqa: E501
]

INTRODUCTION_TEXT = """
This app is a proof of concept using the Dataherald NL-2-SQL engine using a streamlit front-end and a dataset of local production data.
"""  # noqa: E501
INTRO_EXAMPLE = """
A sample question you can ask is: What is the shipment revenue for each branch in the past 6 months?
"""

st.set_page_config(
    page_title="Worldnet SQL Test",
    page_icon="./images/logo.png",
    layout="wide")

# st.sidebar.subheader("Connect to the engine")
# HOST = st.sidebar.text_input("Engine URI", value="http://localhost")
# if st.sidebar.button("Connect"):
#     url = HOST + '/api/v1/heartbeat'
#     if test_connection(url):
#         st.sidebar.success("Connected to engine.")
#     else:
#         st.sidebar.error("Connection failed.")

# Setup main page
st.image("images/whitelogo.svg", width=500)
if not test_connection(HOST + '/api/v1/heartbeat'):
    st.error("Could not connect to engine. Please connect to the engine on the left sidebar.")  # noqa: E501
    st.stop()
else:
    database_connections = get_all_database_connections(HOST + '/api/v1/database-connections')  # noqa: E501
    if st.session_state.get("database_connection_id", None) is None:
        st.session_state["database_connection_id"] = database_connections[DEFAULT_DATABASE]  # noqa: E501
    db_name = find_key_by_value(database_connections, st.session_state["database_connection_id"])  # noqa: E501
    # st.warning(f"Connected to {db_name} database.")
    st.info(INTRODUCTION_TEXT)  # noqa: E501
    st.info(INTRO_EXAMPLE)

output_container = st.empty()
user_input = st.chat_input("Ask your question")
output_container = output_container.container()
if user_input:
    output_container.chat_message("user").write(user_input)
    answer_container = output_container.chat_message("assistant")
    with st.spinner("Agent starts..."):
        st.write_stream(answer_question(HOST + '/api/v1/stream-sql-generation', st.session_state["database_connection_id"], user_input))
        if final_response and "```sql" in final_response:
            st.write("I will execute the SQL Query now: ")

            final_response = final_response.strip()
            start_indx = final_response.index("```sql") + len("```sql")
            end_indx = final_response[start_indx:].index("```") + start_indx
             
            full_query = final_response[start_indx:end_indx]
            df, csv = execute_sql(full_query)
            st.dataframe(df)
            st.download_button("DOWNLOAD DATA", csv, "data.csv", key='download-csv')
    
    st.empty()
        