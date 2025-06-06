from flask import Flask, render_template, request
import logging
import sys
import os
import time
import json
import markdown
import lucene
from datetime import datetime

from config import DEFAULT_INDEX_DIR

# Importing PyLucene search functionality
try:
    from search_utils import search_index, combine_score, rerank
    print("Successfully imported PyLucene search functionality")
    USE_MOCK = False
except ImportError as e:
    print(f"Warning: Could not import PyLucene: {e}")
    print("Using mock search functionality for development")
    USE_MOCK = True
    
    # Mock search function for development without PyLucene
    def mock_search(query, index_dir=DEFAULT_INDEX_DIR, top_k=10):
        """Mock implementation of search_index that simulates PyLucene search
        This function creates realistic mock data that follows the same format
        as what would be returned by the actual PyLucene search_index function.
        It implements the same ranking logic as described in the project requirements.
        """
        subreddits = ["technology", "science", "programming", "news", "AskReddit"]
        current_time = time.time()
        
        mock_results = []
        for i in range(min(20, top_k * 2)):  # Generate extra results for ranking
            days_old = i % 10  # 0-9 days old
            created_utc = current_time - (days_old * 86400)
            
            reddit_score = max(5, 100 - (i * 5))
            
            relevance = max(0.1, 1.0 - (i * 0.04))
            
            w_relevance = 0.6
            w_recency = 0.2
            w_score = 0.2
            
            # Normalize reddit score
            norm_score = max(0, reddit_score) / 100
            
            # Normalize recency
            time_diff = max(0, current_time - created_utc)
            norm_recency = 1.0 / (1.0 + (time_diff / (60 * 60 * 24 * 7)))
            
            # Calculate combined score
            combined_score = (w_relevance * relevance) + (w_recency * norm_recency) + (w_score * norm_score)
            
            # Create a mock result
            result = {
                "title": f"[{subreddits[i % len(subreddits)]}] {query.title()} discussion thread {i+1}",
                "selftext": f"This is a detailed post about {query} with various perspectives and information. It contains multiple paragraphs of content and links to external resources. The discussion covers both technical aspects and practical applications of {query}.",
                "author": f"redditor_{i+1}",
                "created_utc": created_utc,
                "score": reddit_score,
                "url": f"https://www.reddit.com/r/{subreddits[i % len(subreddits)]}/comments/{hash(query + str(i)) % 1000000}/discussion",
                "relevance": relevance,
                "combined_score": combined_score
            }
            mock_results.append(result)
        
        # Sort by combined score (highest first)
        sorted_results = sorted(mock_results, key=lambda x: x["combined_score"], reverse=True)
        return sorted_results[:top_k]


def generate_snippet(text, query_terms, max_len=300):
    """
    Generate a snippet by finding the first match of any query term and showing its surrounding context.
    If no match is found, return the first max_len characters.
    """
    text_lower = text.lower()
    for term in query_terms:
        idx = text_lower.find(term.lower())
        if idx != -1:
            start = max(0, idx - 50)
            end = min(len(text), idx + 250)
            snippet = text[start:end]
            if start > 0:
                snippet = "..." + snippet
            if end < len(text):
                snippet = snippet + "..."
            return snippet
    return text[:max_len] + "..." if len(text) > max_len else text


app = Flask(__name__)

logging.disable(sys.maxsize)

@app.route('/')
def index():
    """Render the search page"""
    return render_template('index.html')

@app.route('/search')
def search():
    """Handle search requests"""
    lucene.getVMEnv().attachCurrentThread()
    query = request.args.get('q', '')
    if not query:
        return render_template('index.html', error='Please enter a search query')
    
    try:
        # Get number of results to display
        top_k = int(request.args.get('top_k', 10))
        
        # Perform search using PyLucene if available, otherwise use mock
        start_time = time.time()
        if USE_MOCK:
            results = mock_search(query, DEFAULT_INDEX_DIR, top_k)
        else:
            # Use the actual PyLucene search_index function
            results = search_index(query, DEFAULT_INDEX_DIR, top_k)
            if not results:
                return render_template('index.html', error='No results found for your query')
        search_time = time.time() - start_time
        
        # Format results for display
        formatted_results = []
        for result in results:
            # Convert timestamp to readable date
            created_date = datetime.fromtimestamp(result['created_utc']) if result['created_utc'] else None
            
            # Convert markdown to HTML for body content (handle missing body field)
            # body = result.get('body', result.get('selftext', ''))
            # body_html = markdown.markdown(body[:500] + '...' if len(body) > 500 else body)
            body = result.get('body', result.get('selftext', ''))
            query_terms = query.split()  # split query into terms
            snippet = generate_snippet(body, query_terms)
            body_html = markdown.markdown(snippet)

            
            # Format the result
            formatted_result = {
                'title': result['title'],
                'body_html': body_html,
                'author': result['author'],
                'score': result['score'],
                'url': result['url'],
                'created_date': created_date.strftime('%Y-%m-%d %H:%M:%S') if created_date else 'Unknown',
                'relevance': round(result['relevance'], 3),
                'combined_score': round(result['combined_score'], 3)
            }
            formatted_results.append(formatted_result)
        
        return render_template('results.html', 
                              query=query, 
                              results=formatted_results, 
                              count=len(formatted_results),
                              time=round(search_time, 3))
    
    except Exception as e:
        return render_template('index.html', error=f'Search error: {str(e)}')

@app.route('/about')
def about():
    """About page with information about the search engine"""
    return render_template('about.html')

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    print("Starting Flask server at http://127.0.0.1:3000")
    print("Open your browser and navigate to http://127.0.0.1:3000")
    app.run(debug=True, host='127.0.0.1', port=3000)