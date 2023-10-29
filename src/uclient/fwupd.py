
from fwupd import fwupd
from uclient.device import device_base


class fwupd_device(device_base, fwupd):
    def __init__(self, serial, dtype=device_base.DEVICE_TYPE, regs={}, status=0) -> None:
        super().__init__(serial, dtype, regs, status)
        super(device_base, self).__init__()

    def hnd_msg(self, topic, msg):
        if topic == 'fw_upd':
            self.pub_dev(topic, self.fwupd(msg))
            return
        if topic == 'fw_pkg':
            self.pub_dev(topic, self.fwpkg(msg))
            return

        return super().hnd_msg(topic, msg)