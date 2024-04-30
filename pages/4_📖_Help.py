import streamlit as st
import requests


DB_INFORMATION = {
    'Redfin': 'Redfin is a real estate brokerage, and the Redfin dataset has information about homes, townhomes, and condos for sale in the United States.',
}
SAMPLE_QUESTIONS = {
    'Redfin': [
        'How many townhomes have been sold in Austin, TX so far in 2023?',
        'compare home prices in los angeles vs austin since 2022',
        'Which county has the highest median rent price overall in Florida?'
    ]
}

def get_all_database_connections():
    api_url = f'{HOST}/api/v1/database-connections'
    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            aliases = {}
            for entry in data:
                aliases[entry["alias"]] = entry["id"]
            return aliases
        else:
            st.warning("Could not get database connections. ")
            return {}
    except requests.exceptions.ConnectionError:
        st.error("Connection failed.")
        return {}

st.set_page_config(
    page_title="Dataherald",
    page_icon="/home/akash/nl-to-sql/streamlit-app/images/logo.png",
    layout="wide")

HOST = st.session_state["HOST"]

with st.container():
    st.title("Golden Records 🌟")
    st.write("In order to improve the performance of NL-to-SQL engines, our system includes a few verified Question SQL samples in the prompts.")
    st.write("As more samples are verified, the performance of the NL-to-SQL engine not only improves in terms of accuracy but also improves in terms of speed.")
    st.write("The verified Question SQL samples are called golden records. These golden records are stored in a vector database for fast retrieval and also in our application storage for easy access and management.")

with st.container():
    st.title("Database scanner 📡")
    st.write("The Database Schema Scanning feature allows you to effortlessly map all tables and columns within your database, aiding the SQL Agent in generating precise answers to your queries.")
    st.write("Whether you want to scan all the tables in your database or specify particular ones, this functionality is designed to streamline the process for you.")

with st.container():
    st.title("Instructions 📜")
    st.write("The Instructions feature allows you to add instructions to the SQL Agent, which will be used to generate answers to your queries.")
    st.write("You can add, delete, and update instructions as you see fit, ensuring that the SQL Agent is always up-to-date with your business needs.")

with st.container():
    st.title("Roadmap 🚀")
    st.write("Our future plans include the following key features:")
    st.write("1. **Custom App Descriptions:** We are working on a feature that will allow you to add custom descriptions for this app, making it more tailored to your needs.")
    st.write("2. **Senate Stock Database:** We plan to add a Senate Stock Database, expanding the range of data sources available for analysis and insights.")
    st.write("3. **Additional Golden Records:** To further enhance the performance of our NL-to-SQL engine, we will continue to add golden records for various databases, ensuring improved accuracy and speed.")

