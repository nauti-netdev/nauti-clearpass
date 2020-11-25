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
from nauti.config_models import CollectionSourceModel

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
        if (filters := params.get("filters")) is not None:
            params["filters"] = parse_filter(filters)

        client: CPPMClient = self.source.client
        self.source_records.extend(await client.fetch_devices())

    def _normalize_vendor(self, rec: Dict) -> str:
        """
        This method is used to map a Clearpass Vendor value to a shared
        vendor field name.  There are cases, such as Cisco, where there
        is not a 1-to-1 mapping between field.vendor and CP.Vendor.  In
        these cases the configuration file uses a "<vendor>:<map-os_name>"
        syntax where the <map-name> is used as the second-stage lookup
        based on field.os_name.

        Parameters
        ----------
        rec: dict
            The native Clearpass device record

        Returns
        -------
        str: field.vendor normalized value.
        """
        cp_cfg = self.config.sources[ClearpassSource.name]
        v_map = cp_cfg.maps['vendor']
        vendor_name = v_map.get(rec['vendor_name'])
        return vendor_name.split(':')[0]

    def itemize(self, rec: Dict) -> Dict:
        attrs = rec['attributes']
        return dict(
            sn='',
            hostname=normalize_hostname(rec["name"]),
            ipaddr=rec["ip_address"],
            site=attrs["Location"],
            os_name=attrs["OS Version"],
            vendor=self._normalize_vendor(rec),
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
