import time
import boto3
from datetime import datetime
from celery.result import AsyncResult
from worker import get_github_data, app 
from pydantic import BaseModel
from typing import List

time.sleep(5)


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


result_future = get_github_data.delay()
result = AsyncResult(result_future.id, app=app)

print('Done')
print('The result state of the queue', result.state) 


while True:
    if result.ready():
        print('Getting the result', result.get())
        break
    else:
        print(result.state)
        time.sleep(1)