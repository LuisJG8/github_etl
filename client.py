import time
from celery.result import AsyncResult
from worker import get_github_data, app 

time.sleep(5)

result_future = get_github_data.delay(100)
result = AsyncResult(result_future.id, app=app)

print('Done')

print(result.state) 

while True:
    if result.ready():
        print(result.get())
        break
    else:
        print(result.state)
        time.sleep(1)