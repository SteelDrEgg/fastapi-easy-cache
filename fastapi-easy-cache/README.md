# Fastapi easy cache

<hr>
An easy to use tool for caching fastapi response

### When should I use fastapi-easy-cache?
1. Returning json serializable data
2. Using GET method
3. Returning dynamic but repeated data (like data refresh everyday)
4. Don't have complicated requirements and too lazy to build a tool yourself

### When should I NOT use fastapi-easy-cache?
1. Returning not json serializable data (bytes, datetime, etc)
2. Using POST method
3. Returning frequently changing data (like data refresh every second)
4. Need advanced features (recommend: [fastapi-cache](https://github.com/long2ice/fastapi-cache))

<hr>

## Installation
We recommend you have fastapi installed
```shell
pip install fastapi-easy-cache
```

## Usage

### Initializing

The following code will
1. create a sqlite database in **dbPath**
2. using peformance mode when calculating route identifier
```python
import fastapi_easy_cache

fastapi_easy_cache.apiCache(dbPath='cachedb/cache.db',
                              peformance_or_capacity='peformance')
```
#### args
    dbPath: path to sqlite database, expected str
    peformance_or_capacity (optional): more peformance or capacity when calculating route id, epected 'peformance' or 'capacity'


### Using
You just need to add `@cache(expire=20)` under fastapi route decorator, add flil in expire time and it's all done.

`expire` is counted in second

```python
from fastapi_easy_cache import cache

@app.get('/testCache/{path}')
@cache(expire=20)
def test(path):
    data = path
    return data
```

With GET route with arguments, you must add request: Request to your function
```python
from starlette.requests import Request
from fastapi_easy_cache import cache

@app.get('/testCacheWithArg/{path}')
@cache(expire=20)
def testArg(path, arg1, arg2, request: Request):
    data = {'path': path,
         'arg1': arg1,
         'arg2': arg2}
    return data
```