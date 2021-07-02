import os
import toml
import yaml
from glob import glob

try:
    from yaml import CSafeLoader as SafeLoader
except ImportError:
    from yaml import SafeLoader

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

supported_families = [
    "STM32F0",
    'STM32F4',
    'STM32L0',
    'STM32L4',
    'STM32H7',
    'STM32WB55',
    'STM32WL55',
]

# ======= load chip list
features = {}
for f in sorted(glob('../stm32-data/data/chips/*.yaml')):
    # Use the filename to get the chip name. Ultra fast, we don't have to read YAML!
    name = os.path.splitext(os.path.basename(f))[0]
    if any((family in name for family in supported_families)):
        name = name.lower()
        # ======= load chip
        with open(f, 'r') as f:
            chip = yaml.load(f, Loader=SafeLoader)

        if len(chip['cores']) > 1:
            for core in chip['cores']:
                features[name + "_" + core['name']] = ['stm32-metapac/' + name + '_' + core['name']]
        else:
            features[name] = ['stm32-metapac/' + name]

# ========= Update Cargo features

SEPARATOR_START = '# BEGIN GENERATED FEATURES\n'
SEPARATOR_END = '# END GENERATED FEATURES\n'
HELP = '# Generated by gen_features.py. DO NOT EDIT.\n'
with open('Cargo.toml', 'r') as f:
    cargo = f.read()
before, cargo = cargo.split(SEPARATOR_START, maxsplit=1)
_, after = cargo.split(SEPARATOR_END, maxsplit=1)
cargo = before + SEPARATOR_START + HELP + toml.dumps(features) + SEPARATOR_END + after
with open('Cargo.toml', 'w') as f:
    f.write(cargo)