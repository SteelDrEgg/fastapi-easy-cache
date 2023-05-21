from functools import wraps
import hashlib
import time, sqlite3, json

db = ''

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
        global db
        if in_memory:
            db = "file:{dbName}?mode=memory&cache=shared".format(dbName=hashlib.md5(db_path.encode()).hexdigest())
        else:
            db = db_path
        conn = sqlite3.connect(db)

        initCur = conn.cursor()
        try:
            initCur.execute('''create table fastapicache(identifier varchar, data TEXT, time integer);''')
        except sqlite3.OperationalError:
            initCur.execute('drop table fastapicache')
            initCur.execute('''create table fastapicache(identifier varchar, data TEXT, time integer);''')
        conn.commit()
        initCur.close()
        conn.close()

# Executing querys to sqlite
def exec(query, commit: bool=False, *queryArgs):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute(query, queryArgs)
    if commit:
        conn.commit()
    data=cursor.fetchone()
    cursor.close()
    conn.close()
    return data

# Add new cache
def add2cache(result, identifier, expire):
    data = json.dumps(result)

    query = '''INSERT INTO fastapicache (identifier, data, time) VALUES (?, ?, ?)'''
    exec(query, True, *(identifier, data, int(time.time())+expire))

# Get cache
def getCache(identifier):
    query='select data, time from fastapicache where identifier=?'
    data=exec(query, False, identifier)
    if data:
        if data[1]>int(time.time()):
            return json.loads(data[0])
        else:
            return False
    else:
        return None

# Update expired cache
def updataCache(result, identifier, expire):
    data = json.dumps(result)
    query = '''UPDATE fastapicache SET identifier=?, data=?, time=? '''
    exec(query, True, *(identifier, data, int(time.time())+expire))

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
            identifier=getIdentifier(func, kwargs)
            cached=getCache(identifier)
            if cached:
                return cached
            elif cached==False:
                result = func(*args, **kwargs)
                updataCache(result, identifier, expire)
                return result
            elif cached==None:
                result = func(*args, **kwargs)
                add2cache(result, identifier, expire)
                return result
        return wrapper
    return decor