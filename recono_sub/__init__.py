import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
common_path = os.path.join(parent_dir, 'common.py')
sys.path.append(parent_dir)

from recono_sub.common import common