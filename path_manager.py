import os, sys

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

def add_root_path():
    if ROOT_DIR not in sys.path:
        sys.path.append(ROOT_DIR)

def add_submodule_path(module_names):
    for module_name in module_names:
        path = os.path.join(ROOT_DIR,module_name)
        if os.path.isdir(path) and path not in sys.path:
            sys.path.insert(0,path)