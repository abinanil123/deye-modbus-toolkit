"""Asynchronous Modbus TCP client implementation for Deye inverters."""

import asyncio
import struct
import logging
from typing import Optional, Dict, Any, List

logger = logging.getLogger("deye_modbus")


class ModbusCodec:
    """Encoder and decoder for standard Modbus TCP Application Protocol (MBAP) frames."""

    @staticmethod
    def build_read_holding_request(transaction_id: int, unit_id: int, start_reg: int, count: int) -> bytes:
        # MBAP Header: Transaction ID (2B), Protocol ID (2B=0), Length (2B), Unit ID (1B)
        # Function Code: 0x03, Start Address (2B), Quantity (2B)
        pdu = struct.pack(">BHH", 0x03, start_reg, count)
        mbap = struct.pack(">HHHB", transaction_id, 0x0000, len(pdu) + 1, unit_id)
        return mbap + pdu

    @staticmethod
    def parse_read_holding_response(data: bytes) -> List[int]:
        if len(data) < 9:
            raise ValueError(f"Packet too short for Modbus TCP response: {len(data)} bytes")
        
        _, _, length, _ = struct.unpack(">HHHB", data[:7])
        function_code = data[7]
        if function_code & 0x80:
            error_code = data[8]
            raise RuntimeError(f"Modbus exception response: FC={function_code:#04x}, code={error_code:#04x}")
            
        byte_count = data[8]
        register_bytes = data[9:9 + byte_count]
        num_regs = len(register_bytes) // 2
        return list(struct.unpack(f">{num_regs}H", register_bytes))


class DeyeModbusClient:
    """Asynchronous client managing connections and register telemetry queries."""

    def __init__(self, host: str, port: int = 502, unit_id: int = 1, timeout: float = 3.0):
        self.host = host
        self.port = port
        self.unit_id = unit_id
        self.timeout = timeout
        self._tx_id = 1
        self._lock = asyncio.Lock()

    def _next_tx_id(self) -> int:
        self._tx_id = (self._tx_id + 1) & 0xFFFF
        return self._tx_id or 1

    async def read_holding_registers(self, start_reg: int, count: int) -> List[int]:
        """Read a continuous block of 16-bit holding registers."""
        async with self._lock:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(self.host, self.port),
                timeout=self.timeout
            )
            try:
                tx_id = self._next_tx_id()
                req = ModbusCodec.build_read_holding_request(tx_id, self.unit_id, start_reg, count)
                writer.write(req)
                await writer.drain()

                # Read MBAP header (7 bytes)
                mbap_data = await asyncio.wait_for(reader.readexactly(7), timeout=self.timeout)
                _, _, length, _ = struct.unpack(">HHHB", mbap_data)

                # Read remaining payload
                payload = await asyncio.wait_for(reader.readexactly(length - 1), timeout=self.timeout)
                full_packet = mbap_data + payload
                return ModbusCodec.parse_read_holding_response(full_packet)
            finally:
                writer.close()
                await writer.wait_closed()
