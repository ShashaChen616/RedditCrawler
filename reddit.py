import praw
import json
import os
import re
import requests
from bs4 import BeautifulSoup
from config import *

class RedditCrawler:
    def __init__(self, client_id, client_secret, user_agent, output_dir = DEFAULT_OUTPUT_DIR, max_file_size_mb = MAX_FILE_SIZE_MB):
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
        os.makedirs(self.output_dir, exist_ok=True)
        self.max_file_size_mb = max_file_size_mb
        self.max_total_size_mb = 0                      # set in crawl with memlimit

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
        title  =  post.title.lower()
        if post.author:
            author =  str(post.author).lower() 
        else: 
            author = ""

        if users and author in users:
            return True
        if keywords and any(kw in title for kw in keywords):
            return True


        return False
    
    @staticmethod
    def get_http_url(text):
        url_pattern = r'(http://[^\s]+)'
        return re.findall(url_pattern, text)
    
    @staticmethod
    def get_url_title(url):
        try: 
            page =  requests.get(url)
            soup =  BeautifulSoup(page.content, 'html.parser')
            title_tag = soup.find('title')
            return title_tag.string
        except Exception as e:
            return "Failed to fetch title"

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
        
        post_dict = {
            "post_ID" : post.id,
            "title" : post.title,
            "author" : str(post.author),
            "body_text": post.selftext,
            "url": post.url,
            "upvotes": post.score,
            "comments": [],
            "external_url" : [],
            "external_url_comments" : [],
        }
        #gets all the comments from a post(submission)
        #also extract url from comments (http only)
        post.comments.replace_more(limit=0)
        for comment in post.comments.list():
            urls = self.get_http_url(comment.body)
            if urls:
                for url in urls:
                    title = self.get_url_title(url)
                    post_dict["external_url_comments"].append({
                        "title": title,
                        "url" : urls
                    })
            post_dict["comments"].append({
                "user": str(comment.author),
                "text_comment" : comment.body
        })

        urls = self.get_http_url(post.selftext)
        if urls:
            for url in urls:
                title = self.get_url_title(url)
                post_dict["external_url"].append({
                    "title": title,
                    "url" : urls
                    })
        #print(post_dict)
        
        return json.dumps(post_dict)
    

    def add_json_to_buffer(self, json):
        '''
        - store json to buffer
        - check json size and update current buffer size
        - when buffer reaches max_file_size_mb (10MB), call write_buffer_to_file()
        '''
        json_bytes = len(json.encode('utf-8'))
        self.buffer.append(json)
        self.current_buffer_size += json_bytes

        if self.current_buffer_size >= self.max_file_size_mb * 1024 * 1024:
            self.write_buffer_to_file()

    
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

        #create filename with current index
        filename = os.path.join(self.output_dir, f"reddit_{self.file_count}.json")

        with open(filename, "w", encoding="utf-8") as f:
            for post_json in self.buffer:
                f.write(post_json + "\n")
        
        #get file size and update stats
        file_size = os.path.getsize(filename)
        self.current_total_size += file_size
        self.current_buffer_size = 0
        self.buffer = []
        self.file_count += 1
        print(f"Wrote buffer to file: {filename} ({file_size / (1024 * 1024):.2f} MB)")
    
    
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

    def crawl(self, subreddits, memlimit, limit, keywords=None, users=None):
        '''
        - loop through each subreddit
        - apply keywords and users filters (should_skip_post())
        - convert post obj to JSON (post_to_json())
        - add JSON to buffer (add_post_to_buffer())
        - check total size limit (total_size_limit_reached())
             - if reached: add any remaining data in buffer to file
        '''
        self.max_total_size_mb = memlimit
        if(self.max_file_size_mb > self.max_total_size_mb):
            self.max_file_size_mb = self.max_total_size_mb

        combined_subreddit = "+".join(subreddits)
        for post in self.reddit.subreddit(combined_subreddit).new(limit=limit):             # use .new() to get the latest
            
            if self.should_skip_post(post, keywords, users): continue                       # filter with lists keywords and users
            
            post_json = self.post_to_json(post)                                             # convert post to json_string
            self.post_count+=1

            self.add_json_to_buffer(post_json)                                              # will write buffer to file when size reached

            if(self.total_size_limit_reached()):
                if(self.current_buffer_size!=0):
                    self.write_buffer_to_file()
                print("-------------------------------------")
                print("Crawl Complete (memory limit reached)")
                print("-------------------------------------")

                return
