import streamlit as st
import pandas as pd
import json
from PIL import Image
from sqlalchemy import create_engine
from agent import query_agent, create_agent
from pandasai import PandasAI
from pandasai.llm.azure_openai import AzureOpenAI
import os
from dotenv import load_dotenv
import matplotlib
matplotlib.use('TkAgg')

load_dotenv()

def decode_response(response: str) -> dict:
    """This function converts the string response from the model to a dictionary object.

    Args:
        response (str): response from the model

    Returns:
        dict: dictionary with response data
    """
    return json.loads(response)


def write_response(response: str,query: str):
    """
    Write a response from an agent to a Streamlit app.

    Args:
        response_dict: The response from the agent.

    Returns:
        None.
    """
    llm = AzureOpenAI(model=os.getenv("OPENAI_CHAT_MODEL"),
                      deployment_name=os.getenv("OPENAI_CHAT_MODEL"),
                      temperature=0,
                      api_token=os.getenv("OPENAI_API_KEY"),
                      api_base=os.getenv("OPENAI_API_BASE"))
    pandas_ai = PandasAI(llm, conversational=False)

    flag = False

    json_data = ''

    for line in response.split('\n'):
        print(line)
        if line.startswith('{'):
            json_data = line

    print("Json:" + json_data)

    if json_data != '':
        try:
            response_dict = json.loads(json_data)
        except ValueError as e:
            flag = True

    if flag or json_data == '':
        st.write(response)
    else:

        # Check if the response is an answer.
        if "answer" in response_dict:
            st.write(response_dict["answer"])

        # Check if the response is a bar chart.
        if "bar" in response_dict:
            data = response_dict["bar"]
            print(data["data"],data["columns"])
            df = pd.DataFrame(data["data"],columns=data["columns"])
            pandas_ai.run(df,query + "with title and save the chart as chat.png")
            chart = Image.open('chart.png')
            st.image(chart)

        # Check if the response is a line chart.
        if "line" in response_dict:
            data = response_dict["line"]
            print(data["data"],data["columns"])
            df = pd.DataFrame(data["data"],columns=data["columns"])
            pandas_ai.run(df,query + "with title and save the chart as chat.png")
            chart = Image.open('chart.png')
            st.image(chart)

        # Check if the response is a line chart.
        if "pie" in response_dict:
            data = response_dict["pie"]
            print(data["data"],data["columns"])
            df = pd.DataFrame(data["data"],columns=data["columns"])
            pandas_ai.run(df,query + "with title and save the chart as chat.png")
            chart = Image.open('chart.png')
            st.image(chart)

        # Check if the response is a table.
        if "table" in response_dict:
            data = response_dict["table"]
            df = pd.DataFrame(data["data"], columns=data["columns"])
            st.table(df)


st.set_page_config(
        page_title="Digital Dream Dashboard",
        page_icon="Ericsson Logo.png",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

image = Image.open('Banner.png')

st.image(image, width=1000, use_column_width="always")

st.header("Welcome to Digital Dream", divider='blue')

query = st.text_area("Insert your query")

driver = '{ODBC Driver 17 for SQL Server}'
odbc_str = 'mssql+pyodbc:///?odbc_connect=' \
           'Driver=' + driver + \
           ';Server=tcp:digital-dream-sql.database.windows.net;PORT=1433' + \
           ';DATABASE=digital-dream-db' + \
           ';Uid=digidrm' + \
           ';Pwd=8miIRF1@#50Kzb?mU$Ze' + \
           ';Encrypt=yes;TrustServerCertificate=no;Connection Timeout=60;'

db_engine = create_engine(odbc_str)

agent = create_agent(db_engine)

if st.button("Submit Query", type="primary"):


    # Query the agent.
    response = query_agent(agent=agent, query=query)
    print(response)
    # Decode the response.
    #decoded_response = decode_response(response)

    # Write the response to the Streamlit app.
    write_response(response,query)