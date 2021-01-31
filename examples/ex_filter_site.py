from nauti.source import get_source
from nauti.config import load_default_config_file
from nauti.collection import get_collection
from nauti.diff import diff

load_default_config_file()

cp = get_source("clearpass")
cp_devs = get_collection(cp, "devices")
