from fastapi import APIRouter
from fastapi_easy_cache import cache

rt2 = APIRouter(prefix='/route2')

@rt2.get('/')
@cache(expire=60)
def rtrot():
    return 'this is route 2'