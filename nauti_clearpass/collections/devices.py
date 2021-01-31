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
        filters = params.get("filters")
        client: CPPMClient = self.source.client
        self.source_records.extend(await client.fetch_devices(params=filters))

    # -------------------------------------------------------------------------
    #
    #                            PRIVATE METHODS
    #
    # -------------------------------------------------------------------------

    def _vendor_normalize(self, rec: Dict) -> str:
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
        os_ver = rec["attributes"]["OS Version"]
        os_to_vendor = self.config.fields["os_name"]
        return os_to_vendor[os_ver]

    def _vendor_clearpass(self, rec: Dict) -> str:
        """
        This function returns the ClearPass NetworkDevice vendor value that is
        associated with the record `os_name`.  This is used when creating new
        ClearPass NetworkDevice records.

        Parameters
        ----------
        rec: dict
            The normalized item fields of this record.
        """
        return self.config.sources[ClearpassSource.name].maps["vendors"][rec["os_name"]]

    # -------------------------------------------------------------------------
    #
    #               Normalize ClearPass record to Collection Fields
    #
    # -------------------------------------------------------------------------

    def itemize(self, rec: Dict) -> Dict:
        attrs = rec["attributes"]
        return dict(
            sn="",
            hostname=normalize_hostname(rec["name"]),
            ipaddr=rec["ip_address"],
            site=attrs["Location"],
            os_name=attrs["OS Version"],
            vendor=self._vendor_normalize(rec),
            model="",
        )

    # -------------------------------------------------------------------------
    #
    #                         Add Devices to Clearpass
    #
    # -------------------------------------------------------------------------

    async def add_items(
        self, items: Dict, callback: Optional[CollectionCallback] = None
    ):
        client: CPPMClient = self.source.client

        def _create_task(key, fields):  # noqa
            payload = {
                "name": fields["hostname"],
                "description": "",
                "ip_address": fields["ipaddr"],
                "tacacs_secret": self.source.config.vars[
                    "tacacs_secret"
                ].get_secret_value(),
                "radius_secret": "",
                "vendor_name": self._vendor_clearpass(fields),
                "coa_port": 3799,
                "coa_capable": False,
                "attributes": {
                    "Location": fields["site"],
                    "OS Version": fields["os_name"],
                },
            }

            return client.create_device(payload=payload)

        await self.source.update(items, callback, _create_task)

    # -------------------------------------------------------------------------
    #
    #                     Update Existing Devices in Clearpass
    #
    # -------------------------------------------------------------------------

    async def update_items(
        self, items: Dict, callback: Optional[CollectionCallback] = None
    ):
        raise NotImplementedError()

    # -------------------------------------------------------------------------
    #
    #                         Remove Devices from ClearPass
    #
    # -------------------------------------------------------------------------

    async def delete_items(
        self, items: Dict, callback: Optional[CollectionCallback] = None
    ):
        raise NotImplementedError()
