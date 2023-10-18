from langchain.agents import create_sql_agent, initialize_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.sql_database import SQLDatabase
from langchain.llms.openai import OpenAI
from langchain.agents import AgentExecutor, Tool
from langchain.agents.agent_types import AgentType
from langchain.chat_models import ChatOpenAI
from langchain.chat_models import AzureChatOpenAI
import os
from dotenv import load_dotenv
from langchain.prompts import MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from langchain_experimental.sql import SQLDatabaseChain
from langchain.tools.render import format_tool_to_openai_function
from langchain.agents.format_scratchpad import format_to_openai_functions
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain.agents import AgentExecutor
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import create_pandas_dataframe_agent

load_dotenv()

llm = model = AzureChatOpenAI(model=os.getenv("OPENAI_CHAT_MODEL"),
                              deployment_name=os.getenv("OPENAI_CHAT_MODEL"),
                              temperature=0)

agent_kwargs = {
    "extra_prompt_messages": [MessagesPlaceholder(variable_name="memory")],
}
memory = ConversationBufferMemory(memory_key="history", input_key='input', return_messages=True)

suffix = """Begin!

Relevant pieces of previous conversation:
{history}
(You do not need to use these pieces of information if not relevant)

Question: {input}
Thought: I should look at the tables in the database to see what I can query.  Then I should query the schema of the most relevant tables.

{agent_scratchpad}
"""

db = SQLDatabase.from_uri("sqlite:///C:/Users/eragasr/PycharmProjects/DigitalDream/SQLliteDB/Chinook.db")
db_chain = SQLDatabaseChain.from_llm(db=db, llm=llm)
tools = [
    Tool(
        name="ChatPlot",
        func=db_chain.run,
        description="Answer all the question based on tables in DB",
    ),
    Tool(
        name="SQLDB",
        func=db_chain.run,
        description="useful to answer the questions about the data in tables in DB",
    )
]

llm_with_tools = llm.bind(
    functions=[format_tool_to_openai_function(t) for t in tools]
)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant"),
    ("user", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

agent = {
            "input": lambda x: x["input"],
            "agent_scratchpad": lambda x: format_to_openai_functions(x['intermediate_steps'])
        } | prompt | llm_with_tools | OpenAIFunctionsAgentOutputParser()

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

agent_executor.invoke({"input": "List top customers along with country by total sales . "})
