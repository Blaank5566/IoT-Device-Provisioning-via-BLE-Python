#!/usr/bin/env python3
import dbus
import dbus.exceptions
import dbus.mainloop.glib
import dbus.service
from gi.repository import GLib

BLUEZ_SERVICE_NAME = "org.bluez"
ADAPTER_INTERFACE = "org.bluez.Adapter1"
ADVERTISING_MANAGER_INTERFACE = "org.bluez.LEAdvertisingManager1"
ADVERTisement_INTERFACE = "org.bluez.LEAdvertisement1"

class Advertisement(dbus.service.Object):
    PATH_BASE = "/org/bluez/example/advertisement"

    def __init__(self, bus, index, advertising_type):
        self.path = self.PATH_BASE + str(index)
        self.bus = bus
        self.ad_type = advertising_type
        self.service_uuids = ["180D"]  # Heart Rate Service UUID (example)
        self.local_name = "RPI-BLE"
        self.manufacturer_data = {}
        self.solicit_uuids = None
        self.service_data = {}
        self.include_tx_power = True
        dbus.service.Object.__init__(self, bus, self.path)

    def get_properties(self):
        return {
            ADVERTisement_INTERFACE: {
                "Type": self.ad_type,
                "ServiceUUIDs": dbus.Array(self.service_uuids, signature="s"),
                "LocalName": dbus.String(self.local_name),
                "IncludeTxPower": dbus.Boolean(self.include_tx_power),
            }
        }

    def get_path(self):
        return dbus.ObjectPath(self.path)

    @dbus.service.method("org.freedesktop.DBus.Properties",
                         in_signature="s", out_signature="a{sv}")
    def GetAll(self, interface):
        if interface != ADVERTisement_INTERFACE:
            raise dbus.exceptions.DBusException("Invalid interface")
        return self.get_properties()[ADVERTisement_INTERFACE]

    @dbus.service.method(ADVERTisement_INTERFACE, in_signature="", out_signature="")
    def Release(self):
        print("Advertisement released")

def main():
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SystemBus()

    adapter_path = "/org/bluez/hci0"
    adapter = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, adapter_path),
                             ADAPTER_INTERFACE)

    adapter_props = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, adapter_path),
                                   "org.freedesktop.DBus.Properties")
    adapter_props.Set(ADAPTER_INTERFACE, "Powered", dbus.Boolean(1))

    ad_manager = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, adapter_path),
                                ADVERTISING_MANAGER_INTERFACE)

    advertisement = Advertisement(bus, 0, "peripheral")
    ad_manager.RegisterAdvertisement(advertisement.get_path(), {},
                                     reply_handler=lambda: print("✅ Advertising as RPI-BLE"),
                                     error_handler=lambda e: print(f"❌ Failed: {e}"))

    loop = GLib.MainLoop()
    loop.run()

if __name__ == "__main__":
    main()
