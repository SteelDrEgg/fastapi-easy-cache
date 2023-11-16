from functools import wraps
import hashlib
import time, json

import sqlalchemy.exc
from sqlalchemy import create_engine, text
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

sessionManager: scoped_session


# Initializing the module
class apiCache():
    def __init__(self, db_path: str, in_memory: bool = False):
        '''This module is for caching fastapi route

        This module uses sqlite to cache content, and use md5 as an identifier to each route
        Please note that this module is only for GET request and json serializable data

        Args:
            db_path: path to sqlite database, expected str
            in_memory: set up cache in memory, expected bool

        Returns:
            None
        '''
        global sessionManager
        if in_memory:
            eng = create_engine("sqlite+pysqlite:///file:{name}?mode=memory&cache=shared&uri=true".format(name=db_path))
        else:
            eng = create_engine("sqlite+pysqlite:///{name}".format(name=db_path))
        sessionManager = scoped_session(sessionmaker(bind=eng))

        newSession = sessionManager()
        try:
            newSession.execute(text('''create table fastapicache(identifier varchar, data TEXT, time integer);'''))
        except sqlalchemy.exc.OperationalError:
            newSession.execute(text('drop table fastapicache'))
            newSession.execute(text('''create table fastapicache(identifier varchar, data TEXT, time integer);'''))
        newSession.commit()
        sessionManager.remove()


# Executing querys to sqlite
def exec(query, commit: bool = False, fetch: bool = False, params: dict = None):
    newSession = sessionManager()
    if params:
        result = newSession.execute(text(query), params)
    else:
        result = newSession.execute(text(query))
    if commit:
        newSession.commit()
    if fetch:
        data = result.all()
        return data
    sessionManager.remove()

# Add new cache
def add2cache(result, identifier, expire):
    data = json.dumps(result)

    query = '''INSERT INTO fastapicache (identifier, data, time) VALUES (:a, :b, :c)'''
    exec(query, True, params={"a": identifier, "b": data, "c": (int(time.time()) + expire)})

# Get cache
def getCache(identifier):
    query = 'select data, time from fastapicache where identifier=:a'
    data = exec(query, False, True, params={"a": identifier})
    if data:
        if data[0][1] > int(time.time()):
            return json.loads(data[0][0])
        else:
            return False
    else:
        return None

# Update expired cache
def updataCache(result, identifier, expire):
    data = json.dumps(result)
    query = '''UPDATE fastapicache SET identifier=:a, data=:b, time=:c'''
    exec(query, True, params={"a": identifier, "b": data, "c": (int(time.time()) + expire)})

# Get route identifier
def getIdentifier(func, kwargs):
    if 'request' in kwargs.keys():
        identifier = str(kwargs['request'].url.path)
        if kwargs['request'].query_params:
            identifier += '?' + str(kwargs['request'].query_params)
    else:
        identifier = func.__name__

    # identifier took less space
    # identifier = base64.b64encode(hashlib.md5(identifier.encode()).digest())
    # identifier took more space
    identifier = hashlib.md5(identifier.encode()).hexdigest()

    return identifier

# Main decorator
def cache(expire: int):
    def decor(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            identifier = getIdentifier(func, kwargs)
            cached = getCache(identifier)
            if cached:
                return cached
            elif cached == False:
                result = func(*args, **kwargs)
                updataCache(result, identifier, expire)
                return result
            elif cached == None:
                result = func(*args, **kwargs)
                add2cache(result, identifier, expire)
                return result

        return wrapper

    return decor
