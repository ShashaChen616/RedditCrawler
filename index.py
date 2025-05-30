import logging, sys
logging.disable(sys.maxsize)
import lucene
import os
from org.apache.lucene.store import MMapDirectory, SimpleFSDirectory, NIOFSDirectory
from java.nio.file import Paths
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, Field, FieldType
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.index import FieldInfo, IndexWriter, IndexWriterConfig, IndexOptions, DirectoryReader
from org.apache.lucene.search import IndexSearcher, BoostQuery, Query
from org.apache.lucene.search.similarities import BM25Similarity

from config import *
import json

# Use log file to track already indexed files
def load_indexed_files(log_file):
    if not os.path.exists(log_file):
        return set()
    with open(log_file, 'r') as f:
        return set(line.strip() for line in f.readlines())

# When a file is indexed, save it to the log file
def save_indexed_files(log_file, filename):
    with open(log_file, 'a') as f:
        f.write(filename + '\n')
        

def create_index(data_dir=DEFAULT_OUTPUT_DIR, index_dir=DEFAULT_INDEX_DIR, log_file=DEFAULT_LOG_FILE):
    lucene.initVM()

    if not os.path.exists(index_dir):
        os.mkdir(index_dir)

    indexed_files = load_indexed_files(log_file)

    # setting up Lucene dir, writer and config
    store = SimpleFSDirectory(Paths.get(index_dir))
    analyzer = StandardAnalyzer()
    config = IndexWriterConfig(analyzer)
    config.setOpenMode(IndexWriterConfig.OpenMode.CREATE_OR_APPEND)

    writer = IndexWriter(store, config)

    metaType = FieldType()
    metaType.setStored(True)
    metaType.setTokenized(False)

    contextType = FieldType()
    contextType.setStored(True)
    contextType.setTokenized(True)
    contextType.setIndexOptions(IndexOptions.DOCS_AND_FREQS_AND_POSITIONS)

    total_docs = 0
    
    for filename in os.listdir(data_dir):
        # skip already indexed files and non-JSON files
        if not filename.endswith('.json') or filename in indexed_files:
            continue

        filepath = os.path.join(data_dir, filename)
        try:
            print(f'Starting file: {filename}')
            with open(filepath, 'r', encoding='utf-8') as f:
                for i, line in enumerate(f,1):
                    try:
                        post = json.loads(line.strip())
                        title = post.get('title', '')
                        context = post.get('selftext', post.get('body',''))

                        doc = Document()
                        doc.add(Field('Title', str(title), metaType))
                        doc.add(Field('Context', str(context), contextType))
                        writer.addDocument(doc)

                        total_docs += 1
                        if i%100 == 0 or i == 1:
                            print(f"   -> {i} posts indexed so far from '{filename}'")

                    except Exception as e:
                        print(f"Skipping line in {filename}: {e}")

            print(f'Finished indexing file: {filename} with {i} posts.')
            save_indexed_files(log_file, filename)
        except Exception as e:
            print(f"Error processing file {filename}: {e}")

    writer.close()
    print(f' ---------- [Indexing complete] ---------- ')
    print(f' > Total documents indexed: {total_docs}')
    print(f' > Indexed files are logged in {log_file}')

if __name__ == "__main__":
    create_index()
