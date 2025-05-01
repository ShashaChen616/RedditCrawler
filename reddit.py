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
    
    def connect_to_reddit(self):
        '''
        - Creates a PRAW Reddit instance using provided credentials
        - stored praw.Reddit(...) as self.reddit
        '''

    def should_skip_post(post, keywords, users):
        '''
        - Decide if post should be filtered out based on the provided keywords and users
        - If post contains one of the keywords or is from one of the users, return True
        - Otherwise return False
        '''

    def post_to_json(post):
        '''
        - extracts fields from a Reddit post object into a serialized JSON string
        - if a post contains URLs to external html pages
             - get title of that page
             - add url and title to the JSON of the post
             - maybe in a list??
             
             "title": "post title",
             "author": "username",
             ...
             "external_urls": [
                  {
                  "url":...,
                  "title":...
                  },
                  {
                  "url":...,
                  "title":...
                  }
               ]
        '''

    def add_json_to_buffer(json):
        '''
        - initialize buffer as a class variable
        - Given a JSON string, stored to a buffer
        - track the size of the buffer
        - when buffer reaches max_file_size_mb (10MB), call write_buffer_to_file()
        '''
    
    def write_buffer_to_file():
        '''
        - write the current buffer to a new output file
        - output files should all be in self.output_dir 
        - add index to file names: "reddit_<index>.json
        - update total written size
        - reset buffer
        - increment file count
        '''
    
    def total_size_limit_reached():
        '''
        - returns True if max_total_size_mb is reached
        '''

    def log_progress():
        '''
        - utility to print progress metrics 
        - (current MB, file count, crawled post count...)
        '''

    def crawl(self, subreddits, keywords, users):
        '''
        - loop through each subreddit
        - apply keywords and users filters (should_skip_post())
        - convert post obj to JSON (post_to_json())
        - add JSON to buffer (add_post_to_buffer())
        - check total size limit (total_size_limit_reached())
             - if reached: add any remaining data in buffer to file
        '''
    


