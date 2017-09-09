import os
import pytest
import doctest
import yapdict


def test_docs():
    doctest.testmod(yapdict, raise_on_error=True)


class TestStoreMemory:
    
    def test_key_set_and_get_item(self):
        store = yapdict.Store(':memory:')
        store['a'] = '1'
        store['b'] = '2'
        assert store['a'] == '1'
        assert store['b'] == '2'
    
    def test_invalid_types(self):
        store = yapdict.Store(':memory:')
        with pytest.raises(TypeError):
            store[1] = 'a'
        with pytest.raises(TypeError):
            store['a'] = 1
    
    def test_key_error_on_get_item(self):
        store = yapdict.Store(':memory:')
        store['a'] = '1'
        assert store['a'] == '1'
        with pytest.raises(KeyError):
            store['b']
            
    def test_delete_item(self):
        store = yapdict.Store(':memory:')
        store['a'] = '1'
        assert 'a' in store
        del store['a']
        assert 'a' not in store
        with pytest.raises(KeyError):
            del store['a']
        with pytest.raises(KeyError):
            del store['b']
    
    def test_len(self):
        store = yapdict.Store(':memory:')
        assert len(store) == 0
        store['a'] = '1'
        assert len(store) == 1
        del store['a']
        assert len(store) == 0
        store['a'] = '1'
        store['b'] = '2'
        assert len(store) == 2
        store['a'] = '1'
        assert len(store) == 2
    
    def test_contains(self):
        store = yapdict.Store(':memory:')
        store['a'] = '1'
        assert 'a' in store
        assert 'b' not in store
        del store['a']
        assert 'a' not in store
    
    def test_key_replace(self):
        store = yapdict.Store(':memory:')
        store['a'] = '1'
        assert store['a'] == '1'
        store['a'] = 'a'
        assert store['a'] == 'a'
    
    def test_update(self):
        store = yapdict.Store(':memory:')
        store['a'] = '1'
        store['b'] = '2'
        store['c'] = '3'
        store.update({'a': 'a', 'b': 'b'})
        assert store['a'] == 'a'
        assert store['b'] == 'b'
        assert store['c'] == '3'
    
    def test_iter_order(self):
        store = yapdict.Store(':memory:')
        store['b'] = '2'
        store['a'] = '1'
        for key, expected_value, expected_item in zip(store.keys(), store.values(), store.items()):
            assert store[key] == expected_value
            assert (key, store[key], ) == expected_item
        store['b'] = '1'
        for key, expected_value, expected_item in zip(store.keys(), store.values(), store.items()):
            assert store[key] == expected_value
            assert (key, store[key], ) == expected_item
            
    def test_get(self):
        store = yapdict.Store(':memory:')
        store['a'] = '1'
        assert store.get('a') == '1'
        assert store.get('b') == None
        
    def test_pop(self):
        store = yapdict.Store(':memory:')
        store['a'] = '1'
        assert store.pop('a') == '1'
        with pytest.raises(KeyError):
            store.pop('a')
        assert store.pop('a', None) is None
    
    def test_clear(self):
        store = yapdict.Store(':memory:')
        store['a'] = '1'
        store['b'] = '2'
        assert len(store) == 2
        assert 'a' in store
        assert 'b' in store
        store.clear()
        assert len(store) == 0
        assert 'a' not in store
        assert 'b' not in store
        store.clear()
    
    def test_popitem(self):
        store = yapdict.Store(':memory:')
        store['a'] = '1'
        assert store.popitem('a') == ('a', '1')
        with pytest.raises(KeyError):
            store.popitem('a')
            
    def test_eq(self):
        store_1 = yapdict.Store(':memory:')
        store_1['a'] = '1'
        store_1['b'] = '2'
        assert store_1 == {'a': '1', 'b': '2'}
        assert store_1 != {'a': '1', 'b': '2', 'c': '3'}
        assert store_1 != {'a': '1', 'c': '3'}
        assert store_1 != {'a': '1', 'b': '1'}
        store_2 = yapdict.Store(':memory:')
        store_2.update({'a': '1', 'b': '2'})
        assert store_1 == store_2
        store_2 = yapdict.Store(':memory:')
        store_2.update({'a': '1', 'b': '2', 'c': '3'})
        assert store_1 != store_2
        store_2 = yapdict.Store(':memory:')
        store_2.update({'a': '1', 'c': '3'})
        assert store_1 != store_2
        store_2 = yapdict.Store(':memory:')
        store_2.update({'a': '1', 'b': '1'})
        assert store_1 != store_2


class TestStoreFile:
    
    def test_multiple_stores(self):
        store_1 = yapdict.Store('.store')
        store_2 = yapdict.Store('.store')
        store_1['a'] = '1'
        store_2['b'] = '2'
        assert store_1['a'] == '1'
        assert store_2['a'] == '1'
        assert store_1['b'] == '2'
        assert store_2['b'] == '2'
    
    def teardown_method(self, test):
        try:
            os.remove('.store')
        except:
            pass