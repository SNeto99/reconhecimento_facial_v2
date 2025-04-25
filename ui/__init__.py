import sys, os
# Inclui SDK oficial pyzk para permitir `import zk`
this_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(this_dir)
pyzk_lib_path = os.path.join(project_root, 'sdks_oficiais', 'biblioteca pyzk')
if pyzk_lib_path not in sys.path:
    sys.path.insert(0, pyzk_lib_path)
