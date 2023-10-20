from langchain import OpenAI
from langchain.chat_models import AzureChatOpenAI
from langchain.agents import create_pandas_dataframe_agent
import pandas as pd
from langchain.agents import create_sql_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.sql_database import SQLDatabase
from langchain.agents.agent_types import AgentType
import ast
import re
# Setting up the api key
import os
from dotenv import load_dotenv
from langchain.agents.agent_toolkits import create_retriever_tool
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS


load_dotenv()

"""
def run_query_save_results(db_engine):
    query = ("select CONVERT(nvarchar(300),ep.value) as [Description] ," +
             "t.name as [Table/View] 	,c.name as [Column]     from sys.extended_properties as ep  " +
             " LEFT JOIN sys.tables t ON ep.major_id=t.object_id" +
             " INNER JOIN sys.schemas s ON t.schema_id=s.schema_id" +
             " LEFT JOIN sys.columns c ON ep.major_id=c.object_id AND ep.minor_id=c.column_id" +
             " where ep.name='MS_Description' AND t.name = 'DatabaseAudit'")
    df = pd.read_sql(query, db_engine)
    print(df.to_string())
    embeddings = OpenAIEmbeddings(deployment='text-embedding-ada-002')
    vector_db = FAISS.from_texts(df.to_string(), embeddings)
    retriever = vector_db.as_retriever()

    return retriever
"""

def create_agent(db):
    """
    Create an agent that can access and use a large language model (LLM).

    Args:
        filename: The path to the CSV file that contains the data.

    Returns:
        An agent that can access and use the LLM.
    """
    llm = AzureChatOpenAI(model=os.getenv("OPENAI_CHAT_MODEL"),
                                  deployment_name=os.getenv("OPENAI_CHAT_MODEL"),
                                  temperature=0)
    # Create an OpenAI object.
    llm = llm
    """
    retriever = run_query_save_results(db)


    retriever_tool = create_retriever_tool(
        retriever,
        name='metadata_search',
        description='use to learn the table and column description'
    )

    custom_tool_list = [retriever_tool]
    """

    #db = SQLDatabase.from_uri(db)
    db = SQLDatabase(db)

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
                Use the following context to create the SQL Query
                Table/View,Column,Description
                DatabaseAudit,,This table contains the monitoring status of each table in the Ericsson Factory Americas (EFA) Azure SQL Database. The table is updated twice daily in the early morning and early afternoon (U.S. Central Time).
                DatabaseAudit,TableName,This column holds the name of the table in the EFA Azure SQL Database for which the monitoring data is stored.
                DatabaseAudit,LineName,"If the data is associated with a factory SMA line, this column reflects the factory Surface Mount Assembly (SMA) line from which the data was obtained (example: A, B, C, etc). If the value is null, the data is not associated with a factory SMA line."
                DatabaseAudit,Category,"This column reflects the origin of the data (e.g. machine data, application name, system name) within each table being monitored."
                DatabaseAudit,Rows,This column provides a count of the total number of rows in the table at the time when the DatabaseAudit table was last updated.
                DatabaseAudit,LastUpdateTimeUTC,This column stores the UTC timestamp of the last updated record in the EFA database table based on the most recent ingest timestamp. The timestamp is in the ISO 8601 format yyyy-mm-dd hh:mm:ss.
                DatabaseAudit,KPI,"This column indicates how frequently the table is expected to be updated and can have one of four values: Weekly, Daily, RealTime, or Best Effort."
                DatabaseAudit,KPIStatus,This column indicates the status of the table based on the KPI and LastUpdateTimeUTC field values. Possible values are Pass , N/A and Investigate.
                DatabaseAudit,_IngestTime,This column holds the UTC timestamp when the data for this record was added to the DatabaseAudit table. The timestamp is in the ISO 8601 format yyyy-mm-dd hh:mm:ss.
                DatabaseAudit,IsActive,This column indicates whether or not the table is actively monitored for compliance against KPIs.
                
                Let's decode the way to respond to the queries. The responses depend on the type of information requested in the query. 

                1. If the query requires a table, format your answer like this:
                {"table": {"columns": ["column1", "column2", ...], "data": [[value1, value2, ...], [value1, value2, ...], ...]}}

                2. For a bar chart, respond like this:
                {"bar": {"columns": ["A", "B", "C", ...], "data": [25, 24, 10, ...]}}

                3. If a line chart is more appropriate, your reply should look like this:
                {"line": {"columns": ["A", "B", "C", ...], "data": [25, 24, 10, ...]}}
                
                4. If a pie chart is more appropriate, your reply should look like this:
                {"pie": {"columns": ["A", "B", "C", ...], "data": [25, 24, 10, ...]}}

                5. For a plain question that doesn't need a chart or table, your response should be:
                {"answer": "Your answer goes here"}

                For example:
                {"answer": "The Product with the highest Orders is '15143Exfo'"}

                6. If the answer is not known or available, respond with:
                {"answer": "I do not know."}
           
                7. If the answer is sql query, respond with:
                {"answer": "select * from customer"}

                Return all output as a string. Remember to encase all strings in the "columns" list and data list in double quotes. 
                For example: {"columns": ["Products", "Orders"], "data": [["51993Masc", 191], ["49631Foun", 152]]}
                
                Return the query if the result is greater than the max token length
                """
            + query
    )
    try:
    # Run the prompt through the agent.
        response = agent.run(prompt)
    # Convert the response to a string.
    except Exception as e:
        response = "Unable to process your request. Encountered following error\n" + e.__str__()

    return response.__str__()