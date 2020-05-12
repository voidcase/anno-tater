import re
from pathlib import Path

paths = Path('.').glob('**/*.jpg')
target = Path('./garbage-crystals')
pattern = r'crystal_(.*)_rot_([0-9]{3})'

matches = [
        (p,*re.search(pattern,str(p)).groups())
        for p in paths
        ]
for path, name, rot in matches:
    if name[:2] == 'th' and int(rot) > 180:
        print(f'mv {path} {target};')
