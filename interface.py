import streamlit as st
import pandas as pd
import json
from PIL import Image

from agent import query_agent, create_agent





def decode_response(response: str) -> dict:
    """This function converts the string response from the model to a dictionary object.

    Args:
        response (str): response from the model

    Returns:
        dict: dictionary with response data
    """
    return json.loads(response)


def write_response(response_dict: dict):
    """
    Write a response from an agent to a Streamlit app.

    Args:
        response_dict: The response from the agent.

    Returns:
        None.
    """

    # Check if the response is an answer.
    if "answer" in response_dict:
        st.write(response_dict["answer"])

    # Check if the response is a bar chart.
    if "bar" in response_dict:
        data = response_dict["bar"]
        df = pd.DataFrame(data)
        df.set_index("columns", inplace=True)
        st.bar_chart(df)

    # Check if the response is a line chart.
    if "line" in response_dict:
        data = response_dict["line"]
        df = pd.DataFrame(data)
        df.set_index("columns", inplace=True)
        st.line_chart(df)

    # Check if the response is a table.
    if "table" in response_dict:
        data = response_dict["table"]
        df = pd.DataFrame(data["data"], columns=data["columns"])
        st.table(df)


st.set_page_config(
        page_title="Digital Dream",
        page_icon="👋",
    )

image = Image.open('Banner.png')

st.image(image, width=850, use_column_width="auto")

st.header("Welcome to Digital Dream", divider='blue')

query = st.text_area("Insert your query")

if st.button("Submit Query", type="primary"):

    agent = create_agent("sqlite:///C:/Users/eragasr/PycharmProjects/DigitalDream/SQLliteDB/Chinook.db")

    # Query the agent.
    response = query_agent(agent=agent, query=query)
    print(response)
    # Decode the response.
    #decoded_response = decode_response(response)

    # Write the response to the Streamlit app.
    #write_response(response)
    st.write(response)