# import os 
# import asyncio
# import time
# from datetime import datetime
# from github import Auth, Github
# from dotenv import load_dotenv
# from pydantic import BaseModel
# from typing import List
# load_dotenv()


# api_token = os.getenv("GITHUB_API_TOKEN")
# auth = Auth.Token(api_token)
# gh = Github(auth=auth)

# time_before = datetime.now()

# def github_api_data_point(repo_data_point):
    
#     try:
#         repo_data_point
#     except Exception as e:
#         print(e)
#         print(f"{repo_data_point} not found")
#     else:
#        print(repo_data_point)
       
#     return repo_data_point

# repo_offset = 0
# repositories = gh.get_repos(since=repo_offset)



# def get_github_data():

#     counter = 0
#     for repo in repositories:
#         # Define all data points in a dictionary
#         data_points = {
#             "Full Name": repo.full_name,
#             "Stargazers Count": repo.stargazers_count,
#             "Updated At": repo.updated_at,
#             "Homepage": repo.homepage,
#             "Allow Forking": repo.allow_forking,
#             "Visibility": repo.visibility,
#             "Topics": repo.topics,
#             "Open Issues Count": repo.open_issues_count,
#             "Language": repo.language,
#             "Watchers Count": repo.watchers_count,
#             "ID": repo.id,
#             "Forks Count": repo.forks_count,
#             "License": repo.license,
#             "Created At": repo.created_at,
#             "Name": repo.name,
#             "Owner User View Type": repo.owner.user_view_type,
#             "Root Contents": repo.get_contents(""),
#             "Owner Avatar URL": repo.owner.avatar_url,
#             "Description": repo.description,
#         }
        

#         for label, value in data_points.items():
#             print(f"{label}:")
#             github_api_data_point(value)


#         counter += 1
#         print()
#         time.sleep(5)
        
#         if counter == 5:
#             break

#         return data_points


# get_github_data()

# time_nw = datetime.now()
# print(time_nw - time_before)


import os
import random 
import json
import boto3
from celery import Celery
from datetime import datetime
from github import Auth, Github, GithubIntegration
from dotenv import load_dotenv
load_dotenv()

todays_date = datetime.now().strftime("%m-%d-%Y")
S3_BUCKET_NAME = "github-etl-data-bucket"


s3_client = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION", "us-east-1")
)


app = Celery(
    'github_repos',
    broker = os.getenv('CELERY_BROKER_URL'),
    backend = os.getenv('CELERY_BACKEND_URL')
)


def save_to_s3(data, file_directory):
    s3_client.put_object(
        Bucket=S3_BUCKET_NAME,
        Key=file_directory,
        Body=json.dumps(data, default=str)
    )


api_token = os.getenv("GITHUB_API_TOKEN")
auth = Auth.Token(api_token)
gh = Github(auth=auth)


@app.task
def get_github_data():

    counter = 0
    repo_collection = []

    repositories = gh.get_repos(since=0)
    rate_limit = gh.rate_limiting
    print(f"Rate limit: {rate_limit[0]} remaining / {rate_limit[1]} total")

    for repo in repositories:
        github_data_points = {
            # ===== BASIC INFO =====
            "ID": repo.id if repo.id else None,
            "Name": repo.name if repo.name else None,
            "Full Name": repo.full_name if repo.full_name else None,
            "Description": repo.description if repo.description else None,
            "GitHub URL": repo.html_url if repo.html_url else None,
            "Clone URL": repo.clone_url if repo.clone_url else None,
            "Git URL": repo.git_url if repo.git_url else None,
            "Homepage": repo.homepage if repo.homepage else None,
            "Default Branch": repo.default_branch if repo.default_branch else None,
            
            # ===== POPULARITY METRICS =====
            "Stargazers Count": repo.stargazers_count if repo.stargazers_count else 0,
            "Forks Count": repo.forks_count if repo.forks_count else 0,
            "Watchers Count": repo.watchers_count if repo.watchers_count else 0,
            "Subscribers Count": repo.subscribers_count if repo.subscribers_count else 0,
            "Network Count": repo.network_count if repo.network_count else 0,
            "Open Issues Count": repo.open_issues_count if repo.open_issues_count else 0,
            
            # ===== DATES =====
            "Created At": str(repo.created_at) if repo.created_at else None,
            "Updated At": str(repo.updated_at) if repo.updated_at else None,
            "Pushed At": str(repo.pushed_at) if repo.pushed_at else None,
            
            # ===== REPOSITORY SETTINGS =====
            "Language": repo.language if repo.language else None,
            "License": repo.license.name if repo.license else None,
            "License Key": repo.license.key if repo.license else None,
            "License SPDX ID": repo.license.spdx_id if repo.license else None,
            "Topics": repo.topics if repo.topics else [],
            "Topics Count": len(repo.topics) if repo.topics else 0,
            "Visibility": repo.visibility if repo.visibility else None,
            "Size KB": repo.size if repo.size else 0,
            
            # ===== BOOLEAN FLAGS =====
            "Is Fork": repo.fork if repo.fork else False,
            "Is Archived": repo.archived if repo.archived else False,
            "Is Disabled": repo.disabled if repo.disabled else False,
            "Is Private": repo.private if repo.private else False,
            "Is Template": repo.is_template if repo.is_template else False,
            "Has Issues": repo.has_issues if repo.has_issues else False,
            "Has Projects": repo.has_projects if repo.has_projects else False,
            "Has Downloads": repo.has_downloads if repo.has_downloads else False,
            "Has Wiki": repo.has_wiki if repo.has_wiki else False,
            "Has Pages": repo.has_pages if repo.has_pages else False,
            "Has Discussions": repo.has_discussions if repo.has_discussions else False,
            "Allow Forking": repo.allow_forking if repo.allow_forking else False,
            "Allow Squash Merge": repo.allow_squash_merge if repo.allow_squash_merge else False,
            "Allow Merge Commit": repo.allow_merge_commit if repo.allow_merge_commit else False,
            "Allow Rebase Merge": repo.allow_rebase_merge if repo.allow_rebase_merge else False,
            "Allow Auto Merge": repo.allow_auto_merge if repo.allow_auto_merge else False,
            "Delete Branch On Merge": repo.delete_branch_on_merge if repo.delete_branch_on_merge else False,
            "Web Commit Signoff Required": repo.web_commit_signoff_required if repo.web_commit_signoff_required else False,
            
            # ===== OWNER INFO =====
            "Owner Login": repo.owner.login if repo.owner else None,
            "Owner ID": repo.owner.id if repo.owner else None,
            "Owner Type": repo.owner.type if repo.owner else None,
            "Owner Avatar URL": repo.owner.avatar_url if repo.owner else None,
            "Owner URL": repo.owner.html_url if repo.owner else None,
            "Owner User View Type": repo.owner.user_view_type if repo.owner else None,
            "Owner Site Admin": repo.owner.site_admin if repo.owner else False,
            
            # ===== PARENT/SOURCE (for forks) =====
            "Parent Full Name": repo.parent.full_name if repo.parent else None,
            "Source Full Name": repo.source.full_name if repo.source else None,
        }

        repo_collection.append(github_data_points)

        counter += 1
        if counter == 5:
            break


    filekey = "github_repos/test.json"
    with open ("s3_data.json", "w") as f:
        json.dump(repo_collection, f)

    # s3_url = save_to_s3(github_data_points, filekey)



print("data saved to s3")

get_github_data()