import sys
import os
node_root = os.path.dirname(__file__)
sys.path.append(node_root)
print(sys.path)

from .nodes import *
