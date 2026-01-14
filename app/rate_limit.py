import time,redis
from .settings import REDIS_URL
r=redis.from_url(REDIS_URL,decode_responses=True)

def allow(key:str,limit:int,window_sec:int):
    now=int(time.time())
    bucket=f"rl:{key}:{now//window_sec}"
    cnt=r.incr(bucket)
    if cnt==1:
        r.expire(bucket,window_sec)
    return cnt<=limit
