# AURA – AI-Powered Journaling Application

AURA is a Python-based command line application that allows users to record journal entries, analyze their sentiment using the Hugging Face Inference API, and store results in MongoDB Atlas. The application supports basic CRUD operations, mood reporting, and keyword/sentiment search.

## Features

- Add a journal entry  
- Automatic sentiment analysis (positive, neutral, negative)  
- Confidence scoring  
- Automatic mood tagging based on sentiment score  
- Store and retrieve entries from MongoDB Atlas  
- Search by sentiment or keyword  
- Delete entries  
- Generate a summary report (counts, averages, tag distribution)

## Installation and Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Create a `.env` file with the following variables

```env
MONGODB_URL=<your MongoDB Atlas connection string>
DB_NAME=aura
COLLECTION=entries
HF_TOKEN=<your Hugging Face token>
```

### 3. Run the application

```bash
python main.py
```

## Architecture Overview

The application is structured around several software design patterns:

- **Strategy** – Defines how sentiment analysis is performed (`HuggingFaceSentimentStrategy`).  
- **Proxy** – Adds caching to reduce repetitive API calls (`CachingSentimentProxy`).  
- **Decorator** – Adds a mood tag to each entry without changing the core entry structure (`TaggingDecorator`).  
- **Factory** – Creates consistent journal entry objects (`EntryFactory`).  
- **Layered structure** – CLI (presentation), controller logic (`main.py`), API adapter (`sentiment.py`), and database adapter (`db.py`).

## Project Structure

```
AURA/
│
├── main.py
├── sentiment.py
├── decorators.py
├── factory.py
├── db.py
├── demo_db.py
├── demo_api.py
├── requirements.txt
└── README.md
```

## Usage Example

After running `main.py`, the CLI displays:

```
1) Add new entry
2) View all entries
3) Search entries by sentiment
4) Search entries by phrase
5) Delete an entry
6) Mood report
7) Quit
```
