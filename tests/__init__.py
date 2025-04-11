import os
import sys

surveyor_lib_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)
tests_path = os.path.dirname(__file__)
sys.path.append(surveyor_lib_path)
sys.path.append(tests_path)
