# SmartSQL

SmartSQL is a modern, minimal, and production-ready Natural Language to SQL system. It enables users to query structured databases using plain English, powered by LLMs and semantic search.

---

## Features
- **Natural Language Interface:** Query your database using plain English.
- **LLM-Driven Text-to-SQL:** Uses large language models (LLMs) to generate SQL from user queries.
- **Semantic Search with FAISS:** Finds relevant schema context for more accurate SQL generation.
- **Schema Awareness & Query Correction:** Dynamically analyzes schema and corrects queries based on feedback.
- **Conversational Query Engine:** Supports follow-up questions and query refinement.
- **Modern UI:** Minimal, responsive, and accessible React frontend.
- **Downloadable Results:** Export query results as CSV.
- **Query History:** View and re-run previous queries in your session.

---

## Tech Stack
- **Frontend:** React (TypeScript), Material-UI
- **Backend:** Flask (Python), LangChain, SQLAlchemy
- **AI/NLP:** Groq LLM, LangChain, FAISS
- **Database:** SQLite (default), pluggable for PostgreSQL/MySQL

---

## Quick Start

### 1. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env  # Add your Groq API key
python app.py
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm start
```

- Frontend: [http://localhost:3000](http://localhost:3000)
- Backend: [http://localhost:5000](http://localhost:5000)

---

## Example Queries
- List all students in section B
- Show average marks for the CS class
- Which teachers teach Algorithms?
- Show names and marks for Algorithms course
- List teachers in Computer Science department

---

## Project Structure
```
SmartSQL/
├── backend/
│   ├── app.py
│   ├── requirements.txt
│   ├── semantic_search.py
│   └── ...
├── frontend/
│   ├── src/
│   ├── package.json
│   └── ...
└── README.md
```

---

## Configuration
- **API Keys:** Set your Groq API key in `backend/.env`.
- **Database:** Default is SQLite (`student.db`). You can configure PostgreSQL/MySQL in the `.env` file.

---

## Contributing
Pull requests and issues are welcome. Please open an issue to discuss your ideas or report bugs.

---

## License
MIT License
