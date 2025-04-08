import os
import sys

path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
print(path)
sys.path.append(path)

from surveyor_lib import helpers as hlp

print(hlp.append_to_csv.out_dir_path)
