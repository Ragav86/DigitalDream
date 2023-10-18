from langchain import OpenAI
from langchain.chat_models import AzureChatOpenAI
from langchain.agents import create_pandas_dataframe_agent
import pandas as pd
from langchain.agents import create_sql_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.sql_database import SQLDatabase
from langchain.agents.agent_types import AgentType
import pandas as pd
# Setting up the api key
import os
from dotenv import load_dotenv

load_dotenv()




def create_agent(db: str):
    """
    Create an agent that can access and use a large language model (LLM).

    Args:
        filename: The path to the CSV file that contains the data.

    Returns:
        An agent that can access and use the LLM.
    """
    llm = model = AzureChatOpenAI(model=os.getenv("OPENAI_CHAT_MODEL"),
                                  deployment_name=os.getenv("OPENAI_CHAT_MODEL"),
                                  temperature=0)
    # Create an OpenAI object.
    llm = llm

    db = SQLDatabase.from_uri(db)
    toolkit = SQLDatabaseToolkit(db=db, llm=OpenAI(temperature=0))

    # Create a SQL agent.
    return create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=True,
    agent_type=AgentType.OPENAI_FUNCTIONS
    )


def query_agent(agent, query):
    """
    Query an agent and return the response as a string.

    Args:
        agent: The agent to query.
        query: The query to ask the agent.

    Returns:
        The response from the agent as a string.
    """

    prompt = (
            """
                For the following query, if it requires drawing a table, reply as follows:
                {"table": {"columns": ["column1", "column2", ...], "data": [[value1, value2, ...], [value1, value2, ...], ...]}}
    
                If the query requires creating a bar chart, reply as follows:
                {"bar": {"columns": ["A", "B", "C", ...], "data": [25, 24, 10, ...]}}
    
                If the query requires creating a line chart, reply as follows:
                {"line": {"columns": ["A", "B", "C", ...], "data": [25, 24, 10, ...]}}
    
                There can only be two types of chart, "bar" and "line".
    
                If it is just asking a question that requires neither, reply as follows:
                {"answer": "answer"}
                Example:
                {"answer": "The title with the highest rating is 'Gilead'"}
    
                If you do not know the answer, reply as follows:
                {"answer": "I do not know."}
    
                Return all output as a json only.
    
                All strings in "columns" list and data list, should be in double quotes,
    
                For example: {"columns": ["title", "ratings_count"], "data": [["Gilead", 361], ["Spider's Web", 5164]]}
    
                Lets think step by step.
    
                Below is the query.
                Query: 
                """
            + query
    )

    # Run the prompt through the agent.
    response = agent.run(prompt)
    print(pd.json_normalize(response))
    # Convert the response to a string.
    return response.__str__()