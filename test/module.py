from multiprocessing import Process
from .file2 import print_x

def run_test():
    Process(target=print_x, daemon=True)
