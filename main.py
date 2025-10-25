import asyncio
import aiohttp
import time
from github import Auth, Github


api_token = 
auth = Auth.Token(api_token)
gh = Github(auth=auth)

some = gh.get_repo("Netflix/Maestro")

async def giting_data():

    async with aiohttp.ClientSession() as session:
        async with some as response:

            print("Status: ", response.status)



print(repositories.stargazers_count)
      
# rep = gh.get_repos()

