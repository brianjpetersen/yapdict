# yapdict

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![Python: v3.6](https://img.shields.io/pypi/pyversions/yapdict.svg)](https://pypi.python.org/pypi/yapdict)

yapdict is sqlite-backed storage with a Python dict API.

# Example

```python
>>> import yapdict
>>> store = yapdict.Store('test.kv', timeout=2)
>>> store['a'] = '1'
>>> store['b'] = '2'
>>> store['a']
'1'
>>> 'b' in store
True
>>> 'c' in store
False
>>> store.update({'c': '3'})
>>> store == {'a': '1', 'b': '2', 'c': '3'}
True
```

# Installing & Testing

To install yapdict:

```
$ pip install yapdict
```

To run the tests, issue the following command:

```
$ python setup.py test
```
