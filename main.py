from github import Auth, Github
import asyncio

api_token = ''
auth = Auth.Token(api_token)
gh = Github(auth=auth)


# repositories = gh.get_repo("Netflix/Maestro")
# print(repositories.stargazers_count)
      
rep = gh.get_repos()

for x in rep:
    print(x)
    break