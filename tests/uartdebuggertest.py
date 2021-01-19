import itertools

from nmigen import *
from nmigen.build import *
from nmigen_boards import versa_ecp5_5g as FPGA
from nmigen_stdio import serial
from ..utils import UARTDebugger

__all__ = ["UARTDebuggerTest"]

class UARTDebuggerTest(Elaboratable):
    def elaborate(self, platform: Platform) -> Module:
        m = Module()
        
        uart_pins = platform.request("uart", 0)
        uart = serial.AsyncSerial(divisor = int(100 * 1000 * 1000 / 115200), pins = uart_pins)

        m.submodules += uart

        words = 4
        data = Signal(words * 8)
        m.d.sync += data.eq(data + 1)
        debugger = UARTDebugger(uart, words, 10000, data)

        m.submodules += debugger
        return m

import os
os.environ["NMIGEN_verbose"] = "Yes"
FPGA.VersaECP55GPlatform().build(UARTDebuggerTest(), do_program=True, nextpnr_opts="--timing-allow-fail")