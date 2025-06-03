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
    TODO

# Rerank and sort search results (top_docs) based on combined score
# - format results from topDocs
# - include all available from index (title, body, comments, authro, etc.)
# - formatting is for display later
# - combine scores using combine_score()
# - return sorted results
def rerank(top_results, searcher):
    TODO

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

