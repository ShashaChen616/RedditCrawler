import praw
import json
import os
from config import *

class RedditCrawler:
    def __init__(self, client_id, client_secret, user_agent, output_dir = DEFAULT_OUTPUT_DIR, max_file_size_mb = MAX_FILE_SIZE_MB, max_total_size_mb = MAX_TOTAL_SIZE_MB):
        '''
        - initialize all class variables
        - call connect_to_reddit(self) to create PRAW instance
        - initialize other class variables that will be used
             - file_count, post_count, current_buffer_size, current_total_size...
        '''
        self.client_id = client_id
        self.client_secret = client_secret
        self.user_agent = user_agent
        self.output_dir = output_dir
        self.max_file_size_mb = max_file_size_mb
        self.max_total_size_mb = max_total_size_mb

        self.reddit = self.connect_to_reddit()

        self.file_count = 0                             # should count how many file already in output_dir
        self.post_count = 0
        self.current_buffer_size = 0
        self.current_total_size = 0

        self.buffer = []                                # buffer (list of dictionaries, JSON-serializable)
    
    def connect_to_reddit(self):
        '''
        - Creates and returns a PRAW Reddit instance using provided credentials
        '''
        return praw.Reddit(
            client_id = self.client_id,
            client_secret = self.client_secret,
            redirect_uri = "http://localhost:8080",
            user_agent = self.user_agent
        )

    def should_skip_post(self, post, keywords, users):
        '''
        - Decide if post should be filtered out based on the provided keywords and users
        - If post contains one of the keywords or is from one of the users, return True
        - Otherwise return False
        '''
        return False

    def post_to_json(self, post):
        '''
        - extracts fields from a Reddit post object and convert to json string
        - check slides and project requirement to see which fields
        - have to also crawl comments
        - if a post contains URLs to external html pages
             - get title of that page
             - add url and title to the JSON of the post
             - maybe in a list??
             
             - ex. 
                post_dict = {
                            "title": "post title", "author": "username", ...
                            "external_urls": [{"url":...,"title":...}, {"url":...,"title":...}],
                            "comments": [{"user":...,"text":...}, {"user":...,"text":...}]
                            }
                post_json = json.dump(post_dict)
        '''

    def add_json_to_buffer(self, json):
        '''
        - store json to buffer
        - check json size and update current buffer size
        - when buffer reaches max_file_size_mb (10MB), call write_buffer_to_file()
        '''
    
    def write_buffer_to_file(self):
        '''
        - write the current buffer to a new output file
        - output files should all be in self.output_dir 
        - add index to file names: "reddit_<index>.json
        - one line per post
            - for line in buffer: f.write(line + "\n")
        - update total written size
        - reset buffer
        - increment file count
        '''
    
    def total_size_limit_reached(self):
        '''
        - returns True if max_total_size_mb is reached
        '''
        # Convert bytes to MB (1 MB = 1024 * 1024 bytes)
        total_size_mb = self.current_total_size / (1024 * 1024)
        return total_size_mb >= self.max_total_size_mb

    def log_progress(self):
        '''
        - utility to print progress metrics 
        - (current MB, file count, crawled post count...)
        '''
        total_size_mb = self.current_total_size / (1024 * 1024)
        buffer_size_mb = self.current_buffer_size / (1024 * 1024)
        
        print(f"\nCrawling Progress:")
        print(f"Posts collected: {self.post_count}")
        print(f"Files written: {self.file_count}")
        print(f"Current buffer size: {buffer_size_mb:.2f}MB")
        print(f"Total data collected: {total_size_mb:.2f}MB / {self.max_total_size_mb}MB")

    def crawl(self, limit, subreddits, keywords=None, users=None):
        '''
        - loop through each subreddit
        - apply keywords and users filters (should_skip_post())
        - convert post obj to JSON (post_to_json())
        - add JSON to buffer (add_post_to_buffer())
        - check total size limit (total_size_limit_reached())
             - if reached: add any remaining data in buffer to file
        '''
        combined_subreddit = "+".join(subreddits)
        for post in self.reddit.subreddit(combined_subreddit).new(limit=limit):             # use .new() to get the latest
            
            if self.should_skip_post(post, keywords, users): continue                       # filter with lists keywords and users
            
            post_json = self.post_to_json(post)                                             # convert post to json_string

            self.add_json_to_buffer(post_json)                                              # will write buffer to file when size reached

            if(self.total_size_limit_reached()):
                if(self.current_buffer_size!=0):
                    self.write_buffer_to_file()
                else:
                    print("Crawl Complete (memory limit reached)")
                    return
