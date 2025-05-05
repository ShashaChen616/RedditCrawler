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
        "--memlimit", type=int, default=MAX_TOTAL_SIZE_MB, 
        help="max data size to collect from a single crawl (in MB)"
    )
    parser.add_argument(
        "--limit", type=int, default=DEFAULT_LIMIT,
        help="maximum number of post to collect from each subreddit (default : ...)"
    )
    parser.add_argument(
        "--keywords", type=str, default = None,
        help="list of keywords to filter posts, comma separated"
    )
    parser.add_argument(
        "--users", type=str, default = None,
        help="list of usernames to filter posts, comma separated"
    )
    args = parser.parse_args()

    # Post-process into lists
    # return empty [] if None
    args.subreddits = [s.strip() for s in args.subreddits.split(",") if s.strip()] if args.subreddits is not None else []
    args.keywords = [k.strip().lower() for k in args.keywords.split(",") if k.strip()] if args.keywords is not None else []
    args.users = [u.strip().lower() for u in args.users.split(",") if u.strip()] if args.users is not None else []
    
    return args

def main():
    '''
    Example program run w/ arguments:
    python main.py --subreddits news,science --keywords ai,climate --users user1,user2
    args.subreddits = ['news','science']
    
    - initalize reddit crawler class
    - start the crawling process
    '''
    args = parse_arguments()
    subreddits, keywords, users = args.subreddits, args.keywords, args.users        # filters
    memlimit, limit = args.memlimit, args.limit                                     # max post to collect
    output = args.output                                                            # output folder to store JSON

    redditCrawler = RedditCrawler(CLIENT_ID,CLIENT_SECRET,USER_AGENT,output,MAX_FILE_SIZE_MB)               # main crawler class obj
    redditCrawler.crawl(subreddits, memlimit, limit, keywords, users)


if __name__ == "__main__":
    main()