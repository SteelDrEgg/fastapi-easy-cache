from fastapi import FastAPI, Response
import uvicorn
from starlette.requests import Request

from fastapi_easy_cache import apiCache, cache

app = FastAPI(version='1.0', title='testServer', docs_url='/docs')

from route2 import rt2
app.include_router(rt2)

apiCache(db_path='cache.db', in_memory=True)

@app.get('/testCache/{path}')
@cache(expire=20)
def testArg(path, arg1, arg2, request: Request):
    data = {'path': path,
         'arg1': arg1,
         'arg2': arg2}
    return data

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=5055, reload=True)