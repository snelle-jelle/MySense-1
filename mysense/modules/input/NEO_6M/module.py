# This file is part of the MySense software (https://github.com/MarcoKull/MySense).
# Copyright (c) 2020 Marco Kull
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from core.modules import InputModule
from core.config_file import ConfigFile
from core.devices import UART_Device

class NEO_6M(InputModule, UART_Device):
    """
    Input module for the NEO-6M GPS sensor.
    """

    def __init__(self):
        InputModule.__init__(self)
        UART_Device.__init__(self, "NEO-6M")

        from modules.input.NEO_6M.dep.gps_dexter import GROVEGPS
        self.sensor = GROVEGPS(port=self.uart_port(), pins=("P" + str(self.config().get("pin_rx")), "P" + str(self.config().get("pin_tx"))))

    def get_id():
        return 5

    def get(self):
        data = self.sensor.MyGPS()

        # no gps
        if data == None:
            return InputModule.concat_bytearrays(
                (
                    InputModule.uint32_to_bytearray(0),
                    InputModule.uint32_to_bytearray(0),
                    InputModule.uint16_to_bytearray(0)
                )
            )

        return InputModule.concat_bytearrays(
            (
                InputModule.uint32_to_bytearray(data[0] * 10000),
                InputModule.uint32_to_bytearray(data[1] * 10000),
                InputModule.uint16_to_bytearray(data[2])
            )
        )

    def decode(array):
        s = "\t\"NEO-6M\":\n\t{\n"
        s += "\t\t\"latitude\": " + str(InputModule.bytearray_to_uint32(array, 0) / 10000) + ",\n"
        s += "\t\t\"longitude\": " + str(InputModule.bytearray_to_uint32(array, 4) / 10000) + ",\n"
        s += "\t\t\"altitude\": " + str(InputModule.bytearray_to_uint16(array, 8)) + "\n"
        s += "\t}"
        return s

    def test(self):
        pass

    def get_config_definition():
        return (
            "input_neo-6m",
            "Support for the NEO-6M GPS sensor.",
            (
                ("pin_rx", "3", "Defines RX pin.", ConfigFile.VariableType.uint),
                ("pin_tx", "4", "Defines TX pin.", ConfigFile.VariableType.uint),
            )
        )
