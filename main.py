import os 
import asyncio
import time
from datetime import datetime
from github import Auth, Github
from dotenv import load_dotenv
load_dotenv()

api_token = os.getenv("GITHUB_API_TOKEN")
print(api_token)
auth = Auth.Token(api_token)
gh = Github(auth=auth)

time_before = datetime.now()

repositories = gh.get_repos(since=0)

counter = 0
for repo in repositories:
    counter += 1 
    print((repo))
    print(repo.stargazers_count)

    if counter == 5:
        break

time_after = datetime.now()

print((time_after - time_before).total_seconds())