import logging, sys
logging.disable(sys.maxsize)
import lucene
import os
from org.apache.lucene.store import MMapDirectory, SimpleFSDirectory, NIOFSDirectory
from java.nio.file import Paths
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, Field, FieldType, StoredField, IntPoint, LongPoint
from org.apache.lucene.index import FieldInfo, IndexWriter, IndexWriterConfig, IndexOptions, DirectoryReader
from urllib.parse import urlparse

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
            with open(filepath, 'r', encoding='utf-8') as f:
                for i, line in enumerate(f,1):
                    try:
                        post = json.loads(line.strip())
                        title = post.get('title', '')
                        body = post.get('selftext', post.get('body',''))
                        author = post.get('author', 'Unknown')
                        subreddit = post.get('subreddit', 'Unknown')
                        url = post.get('url', '')
                        score = post.get('score', 0)

                        comments = post.get('comments', [])
                        extracted_comments = [
                            {
                                "author": str(c.get('author', 'Unknown')),
                                "body": c.get('body', ''),
                                "score": int(c.get('score', 0) or 0),
                                "created_utc": int(c.get('created_utc', 0) or 0),
                            }
                            for c in comments if isinstance(c, dict)
                        ]
                        created_utc = (
                            min((c['created_utc'] for c in extracted_comments if c['created_utc'] > 0), default=None)
                        )
                        external_url = list({u for u in post.get('external_url', []) + post.get('external_url_comments', []) if isinstance(u, str)})

                        doc = Document()
                        doc.add(Field('Title', str(title), contextType))
                        doc.add(Field('Body', str(body), contextType))
                        doc.add(Field('Author', str(author), metaType))
                        doc.add(Field('Subreddit', str(subreddit), metaType))
                        doc.add(Field('URL', str(url), metaType))

                        doc.add(IntPoint('Score', int(score)))
                        doc.add(StoredField('Score', int(score)))

                        if created_utc is not None:
                            doc.add(LongPoint('CreatedUTC', created_utc))
                            doc.add(StoredField('CreatedUTC', created_utc))

                        for comment in extracted_comments:
                            doc.add(Field('CommentAuthor', str(comment['author']), metaType))
                            doc.add(Field('CommentBody', str(comment['body']), contextType))
                            doc.add(IntPoint('CommentScore', int(comment['score'])))
                            doc.add(StoredField('CommentScore', int(comment['score'])))
                            doc.add(LongPoint('CommentCreatedUTC', comment['created_utc']))
                            doc.add(StoredField('CommentCreatedUTC', comment['created_utc']))

                        for url in external_url:
                            if isinstance(url, str) and url.startswith('http'):
                                doc.add(Field('ExternalURL', str(url), metaType))
                                domain = urlparse(url).netloc
                                if domain:
                                    doc.add(Field('ExternalURLDomain', str(domain), metaType))
                        
                        writer.addDocument(doc)

                        total_docs += 1

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
