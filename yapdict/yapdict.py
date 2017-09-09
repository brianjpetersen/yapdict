""" yapdict is a sqlite-backed key-value store with a dict-like API.
"""
import os
import apsw


class _Default: pass
_default = _Default()


class Store:
    """A sqlite-backed key-value store with a dict-like API.
    
    Attributes:
        
        filename (str): path of sqlite file to be used for the storage
        timeout (float): duration in seconds to block if sqlite file has an active writer and 
            another write operation is attempted
    
    Example:
        
        >>> store = Store(':memory:')
        >>> store['a'] = '1'
        >>> assert store['a'] == '1'
        >>> store['b'] = b'2'
        >>> assert store['b'] = b'2'
    
    Note that the string ":memory:" can be supplied as the filename argument to use a sqlite memory
    database instance instead of an on-disk version.  Note that if two difference Stores are created
    within ":memory:", each is it's own namespace and the state is not shared.  The ":memory:" 
    option is primarily to support testing of the yapdict library and for libraries using it.
    
    The store can also be used as a context manager to perform transactions against the sqlite
    database, allowing transactional updates and consistent reads of multiple keys.
    
    The sqlite database is configured for maximum concurrency, although it does block on writes.
    Multiple concurrent readers are supported.  This object is not threadsafe; given the small 
    memory footprint and the low connection time, it is recommended each thread spawn its own store 
    if threading is needed.  The sqlite write-ahead-log is used to minimize the duration of blocking 
    writes.
    
    The directory, database, and all relevant tables are created if they do not exist upon 
    instantiation.  The sqlite database created uses a table called yapdict.
    
    """
    def __init__(self, filename, timeout=1.0):
        self.filename = filename
        if filename != ':memory:':
            directory = os.path.dirname(self.filename)
            if directory != '':
                os.makedirs(directory, exist_ok=True)
        self.connection = apsw.Connection(self.filename)
        self.cursor = self.connection.cursor()
        self.cursor.execute('PRAGMA synchronous = NORMAL')
        self.cursor.execute('PRAGMA journal_mode = WAL')
        self.cursor.execute(
            'CREATE TABLE IF NOT EXISTS yapdict'
            '(key TEXT PRIMARY KEY NOT NULL, value TEXT NOT NULL)'
        )
        self.cursor.execute(
            'CREATE UNIQUE INDEX IF NOT EXISTS key_index ON yapdict(key)'
        )
        self.timeout = timeout
    
    def get_timeout(self):
        return self._timeout
    
    def set_timeout(self, timeout):
        self._timeout = timeout
        self.connection.setbusytimeout(int(1000*timeout))
        
    timeout = property(get_timeout, set_timeout)
        
    def __getitem__(self, key):
        try:
            (value, ), = self.cursor.execute(
                'SELECT value FROM yapdict WHERE key = :key', 
                {'key': key},
            )
            return value
        except:
            raise KeyError(key) from None
    
    def __setitem__(self, key, value):
        if not isinstance(key, (str, bytes)):
            raise TypeError('The key must be an instance of str or bytes.')
        if not isinstance(value, (str, bytes)):
            raise TypeError('The value must be an instance of str or bytes.')
        self.cursor.execute(
            'INSERT OR REPLACE INTO yapdict(key, value) VALUES(:key, :value)',
            {'key': key, 'value': value},
        )
        
    def __delitem__(self, key):
        # note, SQL does not throw an exception when DELETEing a key that doesn't exist, so we wrap
        # this in a transaction to ensure the exception occurs.
        with self.connection:
            try:
                if key not in self:
                    raise KeyError(key) from None
                self.cursor.execute(
                    'DELETE FROM yapdict WHERE key = :key',
                    {'key': key},
                )
            except:
                raise KeyError(key) from None
                
    def __contains__(self, key):
        # according to Richard Hipp (https://goo.gl/WQzDde), EXISTS short-circuits, so no need for 
        # a limit (also, it's a unique column; let's make it easy for the query-planner)
        (contains, ), = self.cursor.execute(
            'SELECT EXISTS (SELECT 1 FROM yapdict WHERE key=:key)',
            {'key': key},
        )
        return bool(contains)
    
    def __len__(self):
        (length, ), = self.cursor.execute('SELECT count(1) FROM yapdict')
        return length
    
    def keys(self):
        for (key, ) in self.cursor.execute('SELECT key FROM yapdict ORDER BY ROWID'):
            yield key
            
    __iter__ = keys
            
    def values(self):
        for (value, ) in self.cursor.execute('SELECT value FROM yapdict ORDER BY ROWID'):
            yield value
            
    def items(self):
        for (key, value, ) in self.cursor.execute('SELECT key, value FROM yapdict ORDER BY ROWID'):
            yield key, value
    
    def update(self, other):
        with self.connection:
            for key, value in other.items():
                self[key] = value
    
    def popitem(self, key):
        value = self.pop(key)
        return key, value
    
    def pop(self, key, default=_default):
        with self.connection:
            try:
                value = self[key]
            except KeyError:
                if default == _default:
                    raise KeyError(key) from None
                else:
                    return default
            else:
                del self[key]
                return value
        return value
        
    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default
    
    def clear(self):
        self.cursor.execute('DELETE FROM yapdict')
    
    def __eq__(self, other):
        self.connection.__enter__()
        if isinstance(other, Store):
            other.connection.__enter__()
        if len(self) != len(other):
            self.connection.__exit__(None, None, None)
            if isinstance(other, Store):
                other.connection.__exit__(None, None, None)
            return False
        for key, value in self.items():
            try:
                other_value = other[key]
            except KeyError:
                self.connection.__exit__(None, None, None)
                if isinstance(other, Store):
                    other.connection.__exit__(None, None, None)
                return False
            if other_value != value:
                self.connection.__exit__(None, None, None)
                if isinstance(other, Store):
                    other.connection.__exit__(None, None, None)
                return False
        else:
            self.connection.__exit__(None, None, None)
            if isinstance(other, Store):
                other.connection.__exit__(None, None, None)
            return True
        
    def __neq__(self, other):
        return not self.__eq__(other)
    
    def __enter__(self):
        return self.connection.__enter__()
    
    def __exit__(self, *args, **kwargs):
        return self.connection.__exit__(*args, **kwargs)
    
    def __repr__(self):
        return '{}.{}(filename={}, timeout={})'.format(
            self.__module__,
            self.__class__.__name__,
            repr(self.filename),
            repr(self.timeout),
        )
