#!/bin/bash

# Display usage if incorrect number of arguments
if [ "$#" -lt 2 ] || [ "$#" -gt 4 ]; then
    echo "Usage: $0 <subreddits> <post-limit> [keywords] [users]"
    echo "Example: $0 'technology,science' 100 'ai,blockchain' 'user1,user2'"
    echo ""
    echo "Arguments:"
    echo "  subreddits  : Comma-separated list of subreddits to crawl"
    echo "  post-limit  : Maximum number of posts to collect from each subreddit"
    echo "  keywords    : Optional, comma-separated keywords to filter posts"
    echo "  users       : Optional, comma-separated usernames to filter posts"
    exit 1
fi

SUBREDDITS=$1
POST_LIMIT=$2
KEYWORDS=${3:-""} 
USERS=${4:-""} 

PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    if python -c "import sys; sys.exit(0 if sys.version_info >= (3,) else 1)" &> /dev/null; then
        PYTHON_CMD="python"
    fi
fi

# Check if we found a valid Python 3 command
if [ -z "$PYTHON_CMD" ]; then
    echo "Error: Python 3 is required but not found"
    echo "Please install Python 3 to run this script"
    exit 1
fi

# Check if required packages are installed
if ! $PYTHON_CMD -c "import praw" &> /dev/null; then
    echo "Installing required packages..."
    $PYTHON_CMD -m pip install --user -r requirements.txt
fi

mkdir -p data

# Run the crawler
echo "Starting Reddit crawler..."
echo "Subreddits: $SUBREDDITS"
echo "Post limit per subreddit: $POST_LIMIT"
[ ! -z "$KEYWORDS" ] && echo "Keywords filter: $KEYWORDS"
[ ! -z "$USERS" ] && echo "Users filter: $USERS"
echo "-----------------------------------"

CMD="$PYTHON_CMD main.py --subreddits \"$SUBREDDITS\" --limit \"$POST_LIMIT\""
[ ! -z "$KEYWORDS" ] && CMD="$CMD --keywords \"$KEYWORDS\""
[ ! -z "$USERS" ] && CMD="$CMD --users \"$USERS\""

$CMD

# Check exit status
if [ $? -eq 0 ]; then
    echo "Crawling completed successfully!"
else
    echo "Error occurred during crawling"
    exit 1
fi
