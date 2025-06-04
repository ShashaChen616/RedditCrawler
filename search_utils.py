import logging, sys
logging.disable(sys.maxsize)
import lucene
import os
from org.apache.lucene.store import MMapDirectory, SimpleFSDirectory, NIOFSDirectory
from java.nio.file import Paths
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.queryparser.classic import QueryParser, MultiFieldQueryParser
from org.apache.lucene.search import IndexSearcher, BoostQuery, Query
from org.apache.lucene.search.similarities import BM25Similarity
from urllib.parse import urlparse
import math
import time

from config import *
import json

# Functions for searching the index to use in app.py

lucene.initVM()

# Load index and return reader and searcher
def load_index(index_dir=DEFAULT_INDEX_DIR):
    lucene.initVM()
    index_dir = SimpleFSDirectory(Paths.get(index_dir))
    reader = DirectoryReader.open(index_dir)                # need reader.close() later
    searcher = IndexSearcher(reader)
    searcher.setSimilarity(BM25Similarity())                # Set BM25 similarity as relevance scoring
    return reader, searcher

# Parse query w/ MultiFieldQueryParser and Boosting
def parse_query(query_str, analyzer=StandardAnalyzer(), fields=['Title', 'Body', 'Author']):
    parser = MultiFieldQueryParser(fields, analyzer)

    # set boosts, default 1
    boosts = {
        'Title': 2.0,
        'Body': 1.0,
        'Author': 0.3
    }
    parser.setBoosts(boosts)
    return parser.parse(query_str)

# Return combined score w/ :
# - relevance: BM25 similarity            (relevance score)
# - created_utc: recency                  (time)
# - reddit_score: reddit post score       (upvote - downvote)
# apply weight to each component
def combine_score(relevance, created_utc, reddit_score):
    
    age_hours = (time.time() - created_utc) / 3600
    recency_score = 1 / (1 + age_hours)
    reddit_score_norm = math.log(1+reddit_score) # prevent from overwhelming the ranking with very high vote posts

    w_rel = 0.5
    w_vote =0.3
    w_time = 0.2

    return (w_rel * relevance) + (w_vote * reddit_score_norm) + (w_time * recency_score)


# Rerank and sort search results (top_docs) based on combined score
# - format results from topDocs
# - include all available from index (title, body, comments, authro, etc.)
# - formatting is for display later
# - combine scores using combine_score()
# - return sorted results
def rerank(top_results, searcher):
    ranked_results = []

    for score_doc in top_results.scoreDocs:
        doc = searcher.doc(score_doc.doc)

        # extract fields from document
        title = doc.get("Title")
        body = doc.get("Body")
        author = doc.get("Author")
        subreddit = doc.get("Subreddit")
        url = doc.get("URL")

        # get numeric values with defaults
        try:
            score = int(doc.get("Score"))
        except:
            score = 0
        
        try:
            created_utc = int(doc.get("CreatedUTC"))
        except:
            created_utc = 0
        
        # get relevance score from BM25
        relevance = score_doc.score

        # calculate combined score
        combined = combine_score(relevance, created_utc, score)

        # collect comments if available
        comments = []
        comment_fields = ["CommentAuthor", "CommentBody", "CommentScore", "CommentCreatedUTC"]
        for i in range (len(doc.getFields("CommentAuthor"))):
            comment = {
                "author": doc.getValues("CommentAuthor")[i],
                "body": doc.getValues("CommentBody")[i],
                "score": int(doc.getValues("CommentScore")[i]),
                "created_utc": int(doc.getValues("CommentCreatdUTC")[i])
            }
            comments.append(comment)
        
        # get external URLs if available
        external_urls = []
        if doc.get("ExternalURL"):
            for url in doc.getValues("ExternalURL"):
                external_urls.append(url)
        
        # create result dictionary
        result = {
            "title": title,
            "selftext": body,
            "body": body,
            "author": author,
            "subreddit": subreddit,
            "url": url,
            "score": score,
            "created_utc": created_utc,
            "relevance": relevance,
            "combined_score": combined,
            "comments": comments,
            "external_url": external_urls
        }
        ranked_results.append(result)
        
    # sort by combined score (highest first)
    ranked_results.sort(key=lambda x: x["combined_score"], reverse=True)
    return ranked_results

# Perform search and return ranked results
def search_index(query_str, index_dir=DEFAULT_INDEX_DIR, top_k=10, analyzer=StandardAnalyzer()):
    reader, searcher = load_index(index_dir)
    try:
        query = parse_query(query_str, analyzer)
        top_docs = searcher.search(query, top_k*2)  # top_k*2 for more margin when reranking
        sorted_results = rerank(top_docs, searcher)
        return sorted_results[:top_k]
    finally:
        reader.close()

