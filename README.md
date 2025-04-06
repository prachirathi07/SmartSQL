# SmartSQL

Natural language interface for SQL databases.

## Overview

SmartSQL is a Streamlit application that allows users to query a SQLite database using natural language. The application translates English questions into SQL queries, executes them, and presents the results in a user-friendly format.

## Features

- Natural language to SQL translation
- Interactive web interface
- Database schema visualization
- Query performance tracking
- Support for multiple LLM models via Groq API
- Advanced settings for customization

## Requirements

- Python 3.8+
- Streamlit
- LangChain
- Groq API key
- SQLite3
- Additional dependencies listed in `requirements.txt`

## Setup

1. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

2. Generate the sample database:
   ```
   python sqlite.py
   ```

3. Run the application:
   ```
   streamlit run app.py
   ```

4. Enter your Groq API key in the sidebar configuration panel.

## Usage

1. View the database schema in the expanded section to understand the available tables and columns.
2. Type your question in natural language in the chat input.
3. The application will convert your question to SQL, execute it, and display the results.
4. Track query performance metrics in the expandable section at the bottom.

## Example Queries

- "List students in section B"
- "What courses are taught by teacher ID 3?"
- "Show names and marks for students in the 'Algorithms' course"
- "Find the average marks for the 'CS' class"

## Project Structure

- `app.py`: Main Streamlit application
- `sqlite.py`: Script to generate the sample student database
- `student.db`: SQLite database containing educational data

## Configuration

The sidebar provides several configuration options:
- Model selection
- API key input
- Advanced settings toggle
- Example queries
- Conversation management
