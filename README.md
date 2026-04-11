# 🔍 Reddit Search Engine (PyLucene + Flask) 🔍 

## 📌 Overview 📌
This project is a full-stack Reddit search engine built using PyLucene and Flask. It indexes large-scale Reddit data (~550MB) and enables efficient search using a custom ranking algorithm that combines relevance, recency, and popularity.

---

## 🧠 Key Features 🧠
- Full-text search using BM25
- Custom reranking (relevance + recency + popularity)
- Multi-field query parsing with boosting
- Snippet generation based on query matches
- Sorting options: relevance, recency, Reddit score, combined score
- Incremental indexing with duplicate detection
- Flask-based web interface

---

## 🏗️ System Architecture 🏗️

Data Collection → Indexing → Search + Ranking → Web Interface

### Components
- **Data Collection**
  - Reddit crawler using PRAW API
  - Stores posts as JSON files

- **Indexing**
  - PyLucene inverted index
  - Fields: title, body, author, score, timestamp

- **Web Interface**
  - Flask app for querying and displaying results
  - Communicates with backend via `search_utils.py`

---

## 📊 Dataset & Index 📊 

| Metric | Value |
|------|------|
| Raw Data Size | 550 MB |
| Index Size | 238 MB |
| Total Posts Indexed | 18,664 |
| Document Unit | 1 Reddit Post |

---

## 🧱 Index Design 🧱

### Indexed Fields
- Title (boosted heavily)
- Body
- Author
- Score
- CreatedUTC
- Subreddit
- Comments
- External URLs

### Field Types
- Text fields → tokenized for search
- Numeric fields → stored using IntPoint / LongPoint
- Metadata fields → stored but not tokenized

---

## 🔍 Search Pipeline 🔍 

User Query → parse_query() → BM25 Search → Rerank → Top-K Results

### Steps
1. Query received from Flask (`app.py`)
2. Parsed using MultiFieldQueryParser
3. Field weights:
   - Title: 2.0  
   - Body: 1.0  
   - Author: 0.3  
4. BM25 retrieves candidates
5. Results reranked
6. Top-K results returned

---

## ⚖️ Ranking Algorithm ⚖️

Final score:

Score = 0.5 * Relevance + 0.3 * Popularity + 0.2 * Recency

### Components
- Relevance → BM25 score
- Popularity → log(1 + Reddit score)
- Recency → 1 / (1 + age_in_hours)

---

## 💻 Implementation 💻

### Indexing (`index.py`)
- Processes Reddit data
- Handles duplicate detection
- Supports incremental indexing

### Search (`search_utils.py`)
- Query parsing with boosting
- BM25 retrieval
- Custom reranking

### Backend (`app.py`)
- Flask web app
- Displays title, snippet, author, timestamp, scores
- Includes fallback system if PyLucene is unavailable

---

## 🖼️ Demo 🖼️

### Search Interface
![Search Interface](images/interface.png)

### Results Page
![Results Page](images/results.png)

---

## ⚠️ Limitations ⚠️
- No semantic search (keyword-based only)
- No efficient handling of updated posts
- Limited filtering by fields
- Sensitive to misspellings

---

## 🚀 How to Run 🚀

```
bash
pip3 install -r requirements.txt
python3 app.py
````

Open:
```
http://127.0.0.1:3000
```

---

## 🎥 Demo Video 🎥

[![Reddit Data Pipeline Demo](https://img.youtube.com/vi/qoaP6CcthHY/0.jpg)](https://www.youtube.com/watch?v=qoaP6CcthHY)

---
