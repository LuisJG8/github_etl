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


def github_api_data_point(repo_data_point):
    
    try:
        repo_data_point
    except Exception as e:
        print(e)
        print(f"{repo_data_point} not found")
    else:
       print(repo_data_point)
       

    return repo_data_point


repositories = gh.get_repos(since=0)
def get_github_data():

    counter = 0
    for repo in repositories:
        # github_api_data_point(repo.full_name)
        github_api_data_point(repo.stargazers_count)
        github_api_data_point(repo.open_issues)
        # github_api_data_point(repo.topics)
        # github_api_data_point(repo.open_issues_count)
        # github_api_data_point(repo.language)
        # github_api_data_point(repo.watchers_count)
        # github_api_data_point(repo.id)
        # github_api_data_point(repo.forks_count)
        # github_api_data_point(repo.license)
        # github_api_data_point(repo.get_contents("README.md"))
        # github_api_data_point(repo.created_at)
        # github_api_data_point(repo.name)
        # github_api_data_point(repo.private)
        test = github_api_data_point(repo.get_contents(""))
        github_api_data_point(repo.owner.avatar_url)
        github_api_data_point(repo.description)
        

        counter += 1
        break
    
    return f" the name of the repo is actually going to be {repo.full_name}" if repo else "idk man"

time_nw = datetime.now()

get_github_data()

print(time_nw - time_before)