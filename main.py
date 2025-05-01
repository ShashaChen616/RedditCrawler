import argparse
from reddit import RedditCrawler
from config import *


def parse_arguments():
    ''' 
    Use argparse to parse arguments from user, return args obj
    - access argument using args.argument_name (ex. args.subreddits)
    - args.subreddit: list of subreddit names to crawl
    - args.output: directory to store crawled data
    - args.keywords: list of keywords to filter posts
    - args.users: list of users to filter posts
    '''
    parser = argparse.ArgumentParser(description="Reddit post crawler")
    parser.add_argument(
        "--subreddits", type=str, default=DEFAULT_SUBREDDITS,
        help="list of subreddits, comma separated (e.g. technology,technews)"
    )
    parser.add_argument(
        "--output", type=str, default=DEFAULT_OUTPUT_DIR,
        help="Directory for storing crawled JSON file (default : data/)"
    )
    parser.add_argument(
        "--keywords", type=str, default = "",
        help="list of keywords to filter posts, comma separated"
    )
    parser.add_argument(
        "--users", type=str, default = "",
        help="list of usernames to filter posts, comma separated"
    )
    args = parser.parse_args()

    # Post-process into lists
    args.subreddits = [s.strip() for s in args.subreddits.split(",") if s.strip()]
    args.keywords = [k.strip().lower() for k in args.keywords.split(",") if k.strip()]
    args.users = [u.strip().lower() for u in args.users.split(",") if u.strip()]
    
    return args

def main():
    '''
    Example program run w/ arguments:
    python main.py --subreddits news,science --keywords ai,climate --users user1,user2
    args.subreddits = ['news','science']
    
    - initalize reddit crawler class
    - start the crawling process
    '''
    print(parse_arguments().subreddits)


if __name__ == "__main__":
    main()