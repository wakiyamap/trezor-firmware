# This file is part of the Trezor project.
#
# Copyright (C) 2012-2019 SatoshiLabs and contributors
#
# This library is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3
# as published by the Free Software Foundation.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the License along with this library.
# If not, see <https://www.gnu.org/licenses/lgpl-3.0.html>.

from trezorlib import device

from .. import buttons
from ..device_handler import BackgroundDeviceHandler
from ..emulators import EmulatorWrapper


def enter_word(debug, word):
    word = word[:4]
    for coords in buttons.type_word(word):
        debug.click(coords)
    return debug.click(buttons.CONFIRM_WORD, wait=True)


def test_persistence():
    with EmulatorWrapper("core") as emu, BackgroundDeviceHandler(
        emu.client
    ) as device_handler:
        debug = device_handler.debuglink()
        features = device_handler.features()

        assert features.recovery_mode is False

        device_handler.run(device.recover, pin_protection=False)
        layout = debug.wait_layout()
        assert layout.text.startswith("Recovery mode")

        layout = debug.click(buttons.OK, wait=True)
        assert "Select numer of words" in layout.text

        storage = emu.storage()
        device_handler.kill_task()

    with EmulatorWrapper("core", storage=storage) as emu, BackgroundDeviceHandler(
        emu.client
    ) as device_handler:
        debug = device_handler.debuglink()
        features = device_handler.features()

        assert features.recovery_mode is True

        # no waiting for layout because layout doesn't change
        layout = debug.read_layout()
        assert "Select number of words" in layout.text
        layout = debug.click(buttons.CANCEL, wait=True)

        assert layout.text.startswith("Abort recovery")
        layout = debug.click(buttons.OK, wait=True)

        assert layout.text == "Homescreen"
        features = device_handler.features()
        assert features.recovery_mode is False
