import streamlit as st
from pathlib import Path
from langchain.agents import create_sql_agent
from langchain.sql_database import SQLDatabase
from langchain.agents.agent_types import AgentType
from langchain.callbacks import StreamlitCallbackHandler
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from sqlalchemy import create_engine
import sqlite3
from langchain_groq import ChatGroq

# Streamlit setup
st.set_page_config(page_title="LangChain: Chat with SQL DB", page_icon="🦜")
st.title("🦜 LangChain: Chat with SQL DB")

# Sidebar for database options and API key input
st.sidebar.header("Database Configuration")
radio_opt = ["Use SQLite 3 Database - Student.db", "Connect to your MySQL Database"]
selected_opt = st.sidebar.radio("Choose the DB you want to chat with", options=radio_opt)

# User inputs for database and API Key
if radio_opt.index(selected_opt) == 1:
    db_uri = "USE_MYSQL"
    mysql_host = st.sidebar.text_input("Provide MySQL Host")
    mysql_user = st.sidebar.text_input("MySQL User")
    mysql_password = st.sidebar.text_input("MySQL Password", type="password")
    mysql_db = st.sidebar.text_input("MySQL Database")
else:
    db_uri = "USE_LOCALDB"
    mysql_host = mysql_user = mysql_password = mysql_db = None  # Set to None for LOCALDB case

api_key = st.sidebar.text_input(label="Groq API Key", type="password")

# Validate user input
if not db_uri or not api_key:
    st.warning("Please provide both the database URI and the Groq API key.")
    st.stop()

# LLM model setup
llm = ChatGroq(groq_api_key=api_key, model_name="Llama3-8b-8192", streaming=True)

# Cache database configuration
@st.cache_resource(ttl="2h")
def configure_db(db_uri, mysql_host=None, mysql_user=None, mysql_password=None, mysql_db=None):
    if db_uri == "USE_LOCALDB":
        dbfilepath = (Path(__file__).parent / "student.db").absolute()
        creator = lambda: sqlite3.connect(f"file:{dbfilepath}?mode=ro", uri=True)
        return SQLDatabase(create_engine("sqlite:///", creator=creator))
    elif db_uri == "USE_MYSQL":
        if not (mysql_host and mysql_user and mysql_password and mysql_db):
            st.error("Please provide all MySQL connection details.")
            st.stop()
        return SQLDatabase(create_engine(f"mysql+mysqlconnector://{mysql_user}:{mysql_password}@{mysql_host}/{mysql_db}"))

# Connect to the selected database
db = configure_db(db_uri, mysql_host, mysql_user, mysql_password, mysql_db)

# Setup toolkit
toolkit = SQLDatabaseToolkit(db=db, llm=llm)

# Create SQL agent
agent = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=True,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    handle_parsing_errors=True  # Enable error handling for parsing errors
)

# Manage chat history
if "messages" not in st.session_state or st.sidebar.button("Clear message history"):
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

# Display chat history with a stylish format
st.subheader("Chat History")
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.chat_message(msg["role"]).write(msg["content"], key=f"user_{len(st.session_state.messages)}")
    else:
        st.chat_message(msg["role"]).write(msg["content"], key=f"assistant_{len(st.session_state.messages)}")

# User input for querying the database
user_query = st.chat_input(placeholder="Ask anything from the database...")

# Process user query
if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    st.chat_message("user").write(user_query)

    # Get response from the agent
    with st.chat_message("assistant"):
        streamlit_callback = StreamlitCallbackHandler(st.container())
        response = agent.run(user_query, callbacks=[streamlit_callback])
        
        # Append response to chat history and display it
        if response:
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.write(response)
        else:
            st.error("No valid response from the agent.")
