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

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Dict, Optional

from aioipfabric.filters import parse_filter

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from nauti.collection import Collection, CollectionCallback
from nauti.collections.devices import DeviceCollection
from nauti_clearpass.source import ClearpassSource, CPPMClient
from nauti.mappings import normalize_hostname

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["ClearpassDeviceCollection"]


# -----------------------------------------------------------------------------
#
#                              CODE BEGINS
#
# -----------------------------------------------------------------------------


class ClearpassDeviceCollection(Collection, DeviceCollection):

    source_class = ClearpassSource

    async def fetch(self, **params):
        breakpoint()
        if (filters := params.get("filters")) is not None:
            params["filters"] = parse_filter(filters)

        client: CPPMClient = self.source.client
        self.source_records.extend(await client.fetch_devices())

    def itemize(self, rec: Dict) -> Dict:
        attrs = rec['attributes']
        return dict(
            sn='',
            hostname=normalize_hostname(rec["name"]),
            ipaddr=rec["ip_address"],
            site=attrs["Location"],
            os_name=attrs["OS Version"],
            vendor=rec["vendor_name"],
            model=''
        )

    async def add_items(self, items: Dict, callback: Optional[CollectionCallback] = None):
        pass

    async def update_items(
        self, items: Dict, callback: Optional[CollectionCallback] = None
    ):
        pass

    async def delete_items(
        self, items: Dict, callback: Optional[CollectionCallback] = None
    ):
        pass
