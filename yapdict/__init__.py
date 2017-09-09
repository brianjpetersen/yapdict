import os
from . import yapdict


__where__ = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(__where__, 'VERSION.txt'), 'rb') as f:
    __version__ = f.read().decode('ascii').strip()


Store = yapdict.Store
