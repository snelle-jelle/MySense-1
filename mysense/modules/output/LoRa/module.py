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

from core.modules import OutputModule
from core.config_file import ConfigFile

from core.log import *

class LoRa(OutputModule):
    """
    Example of an output module that prints the output to the log.
    """
    def __init__(self):
        super(LoRa, self).__init__()

        # check if safety variable is true
        if not self.config().get("antenna_connected"):
            raise Exception("configuration variable 'antenna_connected' is not true")

        # get the reset cause
        import machine
        reset_cause = machine.reset_cause()

        # initialize lora network
        from network import LoRa as LoRa_drv
        self.lora = LoRa_drv(mode=LoRa_drv.LORAWAN, region=LoRa_drv.EU868, adr=self.config().get("adr"))

        # try to load previous lora connection if waking up from deep sleep
        if reset_cause == machine.DEEPSLEEP_RESET:
            self.lora.nvram_restore()

        if reset_cause == machine.DEEPSLEEP_RESET and self.lora.has_joined():
            log_info("Restored previous LoRaWAN join.")

        else:
            # get authentication parameters
            import ubinascii
            app_eui = ubinascii.unhexlify(self.config().get("app_eui"))
            app_key = ubinascii.unhexlify(self.config().get("app_key"))

            # join a network using OTAA (Over the Air Activation)
            self.lora.join(activation=LoRa_drv.OTAA, auth=(app_eui, app_key), timeout=0, dr=self.config().get("data_rate"))

            # wait until the module has joined the network
            log_debug("Waiting until LoRa has joined.")
            while not self.lora.has_joined():
                pass
            log_info("Joined LoRa network.")

        # create a lora socket to send data
        import socket
        self.socket = socket.socket(socket.AF_LORA, socket.SOCK_RAW)

        # set the LoRaWAN data rate
        self.socket.setsockopt(socket.SOL_LORA, socket.SO_DR, self.config().get("data_rate"))


    def send(self, binary, base64, json, json_base64):
        ready_for_Sending = True

        #Implement functionality to set minimum time between messages

        if self.config().get("minimum_time") != 0:
            try:
                lap = chrono.read()
            except:
                log_info("Timer not defined. Defining now.")

                # Import timer
                from machine import Timer
                import time

                #Start timer
                chrono.start()

            #Check if enough time has passed
            if chrono.read() > self.config.get("minimum_time"):
                chrono.reset()

            #If not enough time is passed break loop
            else:        
                ready_for_Sending = False
            

        if ready_for_Sending:
            try:
                # make the socket blocking
                # (waits for the data to be sent and for the 2 receive windows to expire)
                self.socket.setblocking(True)

                # send some data
                #s.send(bytes([0x01, 0x02, 0x03]))
                self.socket.send(binary)

                # make the socket non-blocking
                # (because if there's no data received it will block forever...)
                self.socket.setblocking(False)

                # get any data received (if any...)
                data = self.socket.recv(64)

                # TODO activate ota mode

                # save lora connection
                self.lora.nvram_save()

            except:
                log_error("LoRa send failed!")

    def test(self):
        pass

    def get_config_definition():
        return (
            "output_lora_otaa",
            "LoRaWAN output module using OTAA.",
            (
                ("antenna_connected", "false", "This variable is for safety reasons to ensure a antenna is connected before LoRa is initialzed.\nWARNING: Setting this to true without an actual antenna connected can destroy your device!", ConfigFile.VariableType.bool),
                #("region", "EU868", "Pick the region that matches where you are using the device:\n\tAsia = 'AS923'\n\tAustralia = 'AU915'\n\tEurope = 'EU868'\n\tUnited States = 'US915'", ConfigFile.VariableType.string),
                ("app_eui", "UNSET", "app eui", ConfigFile.VariableType.string),
                ("app_key", "UNSET", "app key", ConfigFile.VariableType.string),
                ("data_rate", "5", "LoRa data rate. Use a value between 0 and 5.", ConfigFile.VariableType.uint),
                ("adr", "false", "Enables LoRa adaptive data rate.", ConfigFile.VariableType.bool)
            )
        )
