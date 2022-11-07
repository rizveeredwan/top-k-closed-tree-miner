import os

def read(file):
    _dict = {}
    with open(file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for i in range(0, len(lines), 2):
            freq = int(lines[i])
            pattern = lines[i+1].strip()
            _dict[pattern] = freq
    return _dict

def search_func(kclotreeminer, other):
    print("starting")
    for key in kclotreeminer:
        if other.get(key) is None:
            print(f"{key} not found")


kclotreeminer = read(file=os.path.join('E:\Research\K closed SPM\kclotreeminer\kclotreeminer_output.txt'))
other = read(file=os.path.join('E:\Research\Sequential-Pattern-Mining-Algorithms\GSP\gsp_output.txt'))
search_func(kclotreeminer=kclotreeminer, other=other)
search_func(kclotreeminer=other, other=kclotreeminer)
