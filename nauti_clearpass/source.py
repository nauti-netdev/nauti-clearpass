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

from typing import Optional

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from aiocppm import CPPMClient as _CPPMClient
from aiocppm.mixins.network_device import CPPMNetworkDeviceMixin
from nauti.source import Source
from nauti.config_models import SourcesModel

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from nauti_clearpass import NAUTI_SOURCE_NAME


class CPPMClient(_CPPMClient, CPPMNetworkDeviceMixin):
    pass


__all__ = ["ClearpassSource", "CPPMClient"]


class ClearpassSource(Source):

    name = NAUTI_SOURCE_NAME
    client_class = CPPMClient

    def __init__(self, source_config: Optional[SourcesModel] = None, **kwargs):
        super(ClearpassSource, self).__init__()
        initargs = dict()

        if source_config:
            initargs.update(dict(
                base_url=source_config.default.url,
                client_id=source_config.default.credentials.client_id.get_secret_value(),
                client_secret=source_config.default.credentials.client_secret.get_secret_value(),
                **source_config.default.options
            ))
            initargs.update(kwargs)

        self.client = CPPMClient(**(initargs or kwargs))

    async def login(self, *vargs, **kwargs):
        await self.client.login()

    async def logout(self):
        await self.client.logout()

    @property
    def is_connected(self):
        return not self.client.api.is_closed
