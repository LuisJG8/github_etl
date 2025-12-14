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



def get_github_data():

    counter = 0
    for repo in repositories:
        # Define all data points in a dictionary
        data_points = {
            "Full Name": repo.full_name,
            "Stargazers Count": repo.stargazers_count,
            "Updated At": repo.updated_at,
            "Homepage": repo.homepage,
            "Allow Forking": repo.allow_forking,
            "Visibility": repo.visibility,
            "Topics": repo.topics,
            "Open Issues Count": repo.open_issues_count,
            "Language": repo.language,
            "Watchers Count": repo.watchers_count,
            "ID": repo.id,
            "Forks Count": repo.forks_count,
            "License": repo.license,
            "Created At": repo.created_at,
            "Name": repo.name,
            "Owner User View Type": repo.owner.user_view_type,
            "Root Contents": repo.get_contents(""),
            "Owner Avatar URL": repo.owner.avatar_url,
            "Description": repo.description,
        }
        

        for label, value in data_points.items():
            print(f"{label}:")
            github_api_data_point(value)


        counter += 1
        print()
        time.sleep(5)
        
        if counter == 5:
            break

        return data_points


get_github_data()

time_nw = datetime.now()
print(time_nw - time_before)