from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import os
import logging
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain.agents.agent_types import AgentType
from langchain_groq import ChatGroq
from sqlalchemy import create_engine, inspect, text
import json
from semantic_search import SchemaSemanticSearch, get_schema_embeddings
import numpy as np
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
if not GROQ_API_KEY:
    logger.error("GROQ_API_KEY not found in environment variables")
    raise ValueError("GROQ_API_KEY environment variable is required")

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///student.db')
SCHEMA_INDEX_PATH = os.getenv('SCHEMA_INDEX_PATH', 'schema_index')

# Initialize database connection
def get_db():
    try:
        engine = create_engine(DATABASE_URL)
        # Test the connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connection successful")
        db = SQLDatabase(engine)
        return db, engine
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        return None, None

# Initialize LLM
def get_llm():
    try:
        llm = ChatGroq(
            groq_api_key=GROQ_API_KEY,
            model_name="Llama3-8b-8192",
            temperature=0.2
        )
        logger.info("LLM initialization successful")
        return llm
    except Exception as e:
        logger.error(f"LLM initialization error: {e}")
        return None

# Initialize semantic search
def get_semantic_search(schema_info):
    try:
        # Try to load existing index
        if os.path.exists(SCHEMA_INDEX_PATH):
            return SchemaSemanticSearch.load(SCHEMA_INDEX_PATH)
        
        # Create new index
        semantic_search = SchemaSemanticSearch()
        embeddings = get_schema_embeddings(schema_info)
        
        for table_name, column_name, data_type, vector in embeddings:
            semantic_search.add_schema_item(table_name, column_name, data_type, vector)
        
        # Save the index
        semantic_search.save(SCHEMA_INDEX_PATH)
        return semantic_search
    except Exception as e:
        logger.error(f"Semantic search initialization error: {e}")
        return None

@app.route('/', methods=['GET'])
def root():
    return jsonify({
        "message": "Welcome to SmartSQL API",
        "endpoints": {
            "/api/health": "Health check endpoint",
            "/api/schema": "Get database schema",
            "/api/query": "Process natural language queries",
            "/api/semantic-search": "Search schema semantically"
        }
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    db_status = "healthy" if get_db()[0] else "unhealthy"
    llm_status = "healthy" if get_llm() else "unhealthy"
    
    return jsonify({
        "status": "healthy" if db_status == "healthy" and llm_status == "healthy" else "degraded",
        "components": {
            "database": db_status,
            "llm": llm_status
        }
    })

@app.route('/api/schema', methods=['GET'])
def get_schema():
    db, engine = get_db()
    if not db or not engine:
        return jsonify({"error": "Database connection failed"}), 500
    try:
        schema_info = {}
        inspector = inspect(engine)
        # Get all tables and views
        tables = inspector.get_table_names()
        views = inspector.get_view_names()
        for name in tables + views:
            is_view = name in views
            columns = inspector.get_columns(name)
            schema_info[name] = {
                "columns": [col["name"] for col in columns],
                "types": {col["name"]: str(col["type"]) for col in columns},
                "is_view": is_view
            }
            if not is_view:
                try:
                    foreign_keys = inspector.get_foreign_keys(name)
                    if foreign_keys:
                        schema_info[name]["foreign_keys"] = foreign_keys
                except Exception as e:
                    logger.warning(f"Could not get foreign keys for {name}: {e}")
        return jsonify(schema_info)
    except Exception as e:
        logger.error(f"Schema retrieval error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/semantic-search', methods=['POST'])
def semantic_search():
    data = request.json
    if not data or 'query' not in data:
        return jsonify({"error": "No query provided"}), 400
    
    try:
        # Get schema info
        schema_info = get_schema().get_json()
        
        # Initialize semantic search
        semantic_search = get_semantic_search(schema_info)
        if not semantic_search:
            return jsonify({"error": "Failed to initialize semantic search"}), 500
        
        # Generate query vector (placeholder - replace with actual embedding)
        query_vector = np.random.randn(768).astype(np.float32)
        query_vector = query_vector / np.linalg.norm(query_vector)
        
        # Search
        results = semantic_search.search(query_vector)
        return jsonify({"results": results})
    except Exception as e:
        logger.error(f"Semantic search error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/query', methods=['POST'])
def process_query():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    data = request.json
    if not data or 'query' not in data:
        return jsonify({"error": "No query provided"}), 400
    db, engine = get_db()
    llm = get_llm()
    if not db or not llm:
        return jsonify({"error": "Failed to initialize database or LLM"}), 500
    try:
        # Get schema info for semantic search
        inspector = inspect(engine)
        schema_info = {}
        tables = inspector.get_table_names()
        views = inspector.get_view_names()
        for name in tables + views:
            is_view = name in views
            columns = inspector.get_columns(name)
            schema_info[name] = {
                "columns": [col["name"] for col in columns],
                "types": {col["name"]: str(col["type"]) for col in columns},
                "is_view": is_view
            }
            if not is_view:
                try:
                    foreign_keys = inspector.get_foreign_keys(name)
                    if foreign_keys:
                        schema_info[name]["foreign_keys"] = foreign_keys
                except Exception as e:
                    logger.warning(f"Could not get foreign keys for {name}: {e}")
        semantic_search = get_semantic_search(schema_info)
        query_vector = np.random.randn(768).astype(np.float32)
        query_vector = query_vector / np.linalg.norm(query_vector)
        relevant_items = semantic_search.search(query_vector) if semantic_search else []
        context = "\n".join([
            f"Table: {item['table_name']}, Column: {item['column_name']}, Type: {item['data_type']}"
            for item in relevant_items
        ])
        enhanced_query = f"{data['query']}\n\nRelevant schema information:\n{context}"
        toolkit = SQLDatabaseToolkit(db=db, llm=llm)
        agent = create_sql_agent(
            llm=llm,
            toolkit=toolkit,
            verbose=True,
            agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        )
        try:
            response = agent.invoke({"input": enhanced_query})
            output = response.get("output", "") or response.get("final_answer", "")
            sql = ""
            result = ""

            # Try to extract SQL using regex (looks for lines starting with SELECT/UPDATE/INSERT/DELETE)
            sql_match = re.search(r"(SELECT|UPDATE|INSERT|DELETE)[^;\\n]*", output, re.IGNORECASE)
            if sql_match:
                sql = sql_match.group(0).strip()

            # Try to extract result (if present)
            if "Final Answer:" in output:
                result = output.split("Final Answer:")[-1].strip()
            elif "Answer:" in output:
                result = output.split("Answer:")[-1].strip()
            else:
                result = output.strip()

            return jsonify({
                "sql": sql,
                "result": result,
                "raw_output": output,
                "error": response.get("error", None),
                "relevant_schema": relevant_items
            })
        except Exception as e:
            # Handle output parsing error and extract final answer from the error message
            error_msg = str(e)
            print("Agent Exception:", error_msg)
            sql = ""
            result = ""
            sql_match = re.search(r"(SELECT|UPDATE|INSERT|DELETE)[^;\\n]*", error_msg, re.IGNORECASE)
            if sql_match:
                sql = sql_match.group(0).strip()
            if "Final Answer:" in error_msg:
                result = error_msg.split("Final Answer:")[-1].strip().split("\n")[0]
            elif "Answer:" in error_msg:
                result = error_msg.split("Answer:")[-1].strip().split("\n")[0]
            else:
                result = error_msg
            return jsonify({
                "sql": sql,
                "result": result,
                "raw_output": error_msg,
                "error": "Output parsing error (handled)",
                "relevant_schema": relevant_items
            })
    except Exception as e:
        logger.error(f"Query processing error: {e}")
        return jsonify({"error": str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    # Verify environment setup
    if not GROQ_API_KEY:
        logger.error("GROQ_API_KEY not found in environment variables")
        raise ValueError("GROQ_API_KEY environment variable is required")
    
    # Test database connection
    if not get_db()[0]:
        logger.error("Failed to connect to database")
        raise ConnectionError("Database connection failed")
    
    # Test LLM connection
    if not get_llm():
        logger.error("Failed to initialize LLM")
        raise ConnectionError("LLM initialization failed")
    
    app.run(debug=True, port=5000) 