import os 
import asyncio
import time
from datetime import datetime
from github import Auth, Github
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List
load_dotenv()


api_token = os.getenv("GITHUB_API_TOKEN")
auth = Auth.Token(api_token)
gh = Github(auth=auth)

time_before = datetime.now()
 
class Repo(BaseModel):
    id: int
    name: str
    full_name: str 
    stars: int
    open_issues_: List[str]
    first_issue: str
    updated_at: datetime
    homepage: str 
    allow_forking: bool
    visibility: str 
    topics: List[str]
    open_issues: int
    prog_language: str
    watchers_count: int
    fork_count: int
    license: str 
    repo_content: List[str]
    creation_data: datetime 
    owner_avatar: str
    description: str 


def github_api_data_point(repo_data_point):
    
    try:
        repo_data_point
    except Exception as e:
        print(e)
        print(f"{repo_data_point} not found")
    else:
       print(repo_data_point)
       
    return repo_data_point

repo_offset = 0
repositories = gh.get_repos(since=repo_offset)


def get_github_data(github_data_formatted: Repo):

    counter = 0
    for repo in repositories:
        print("Full Name:")
        github_api_data_point(repo.full_name)
        print("Stargazers Count:")
        github_api_data_point(repo.stargazers_count)
        print("Open Issues:")
        github_api_data_point(repo.open_issues)
        print("First Issue:")
        github_api_data_point(repo.get_issue(number=1))
        print("Updated At:")
        github_api_data_point(repo.updated_at)
        print("Homepage:")
        github_api_data_point(repo.homepage)
        print("Allow Forking:")
        github_api_data_point(repo.allow_forking)
        print("Visibility:")
        github_api_data_point(repo.visibility)
        print("Topics:")
        github_api_data_point(repo.topics)
        print("Open Issues Count:")
        github_api_data_point(repo.open_issues_count)
        print("Language:")
        github_api_data_point(repo.language)
        print("Watchers Count:")
        github_api_data_point(repo.watchers_count)
        print("ID:")
        github_api_data_point(repo.id)
        print("Forks Count:")
        github_api_data_point(repo.forks_count)
        print("License:")
        github_api_data_point(repo.license)
        print("README.md:")
        github_api_data_point(repo.get_contents("README.md"))
        print("Created At:")
        github_api_data_point(repo.created_at)
        print("Name:")
        github_api_data_point(repo.name)
        print("Owner User View Type:")
        github_api_data_point(repo.owner.user_view_type)
        print("Root Contents:")
        github_api_data_point(type(repo.get_contents("")))
        print("Owner Avatar URL:")
        github_api_data_point(repo.owner.avatar_url)
        print("Description:")
        github_api_data_point(repo.description)
        

        counter += 1
        break


get_github_data()

time_nw = datetime.now()
print(time_nw - time_before)