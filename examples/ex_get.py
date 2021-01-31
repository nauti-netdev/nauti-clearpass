#      Copyright (C) 2020  Jeremy Schulman
#
#      This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation, either version 3 of the License, or
#      (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>.

from nauti.source import get_source
from nauti.config import load_default_config_file
from nauti.collection import get_collection
from nauti.diff import diff

load_default_config_file()

shared_fields = ("hostname", "site", "os_name", "ipaddr")
shared_keys = ("hostname",)

cp_devs = get_collection(get_source("clearpass", timeout=5), "devices")
await cp_devs.source.login()
await cp_devs.fetch()
cp_devs.make_keys(*shared_keys)


def tr_nb_rec(item):

    os_name = item["os_name"]
    item["os_name"] = {"iosxe": "ios-xe", "nxos": "nx-os"}.get(os_name, os_name)


def nb_filter_item(item) -> bool:
    tr_nb_rec(item)
    if not item["os_name"]:
        return False

    if not item["ipaddr"]:
        return False

    if item["vendor"] == "pan":
        return False

    if item["status"] != "active":
        return False

    return True


nb_devs = get_collection(get_source("netbox", timeout=60), "devices")
await nb_devs.source.login()
await nb_devs.fetch(filters={"has_primary_ip": "true"})
nb_devs.make_keys(*shared_keys, with_filter=nb_filter_item)

diff_res = diff(origin=nb_devs, target=cp_devs, fields=shared_fields)
