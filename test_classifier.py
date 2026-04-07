import sys
import os
sys.path.insert(0, os.path.abspath("src"))

from src.classifiers import classify_input

import sys
import logging
logging.basicConfig(level=logging.DEBUG)

print(classify_input("我不知道怎么做", ""))
