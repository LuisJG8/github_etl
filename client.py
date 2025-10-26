import time
from celery.result import AsyncResult
from worker import random_number, app 

time.sleep(5)

result_future = random_number.delay(100)
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