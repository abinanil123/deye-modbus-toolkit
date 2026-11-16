# Deye Modbus Toolkit

Asynchronous Python engine and command-line interface for communicating locally with Deye, Sunsynk, and Sol-Ark hybrid solar inverters via native Modbus TCP (port 502) and Modbus RTU.

## Overview

Modern solar installations often rely on vendor cloud servers with polling latencies of 5–10 minutes. This engine provides direct, zero-cloud local polling (<25ms response time) over the inverter's Wi-Fi / Ethernet data logger.

### Core Capabilities

- **Zero-Cloud Architecture:** Queries holding registers directly over raw TCP sockets without vendor cloud dependencies.
- **Asynchronous Protocol Pipeline:** Pure Python `asyncio` implementation of Modbus Function Codes `0x03` (Read Holding), `0x06` (Write Single), and `0x10` (Write Multiple).
- **Automated Register Sweeping:** Utility to scan register spaces across single-phase (`LP1`, `SG04`) and three-phase units for active telemetry telemetry addresses.
- **Dynamic Energy Dispatch:** Mathematical rules engine for predictive battery charging, SmartLoad throttling, and grid peak shaving.

## Architectural Layout

```
[ Deye / Sunsynk Inverter ]
          │
          │ Modbus RTU / Internal Bus
          ▼
[ DL1000B / Solarman Logger (Port 502) ]
          │
          │ Local TCP / IP (<20ms latency)
          ▼
[ DeyeModbusClient (asyncio) ] ──▶ [ Real-time Telemetry Stream ]
          │
          ├──▶ [ Holding Register Codec ]
          └──▶ [ Home Assistant Integration ]
```

## Supported Register Domains

- **Live Flow:** PV1/PV2 Power, Inverter Load, Grid Power, Grid Current & Voltage, Battery Voltage, Signed Battery Watts.
- **Battery Management:** State of Charge (SOC), Battery Temp, Max Charge/Discharge limits, Shutdown & Restart SOC thresholds.
- **SmartLoad & Generator Port:** Real-time port output power, SmartLoad ON/OFF SOC gates, minimum solar generation triggers.
- **Grid Health Assessment:** Relay state verification, AC frequency tracking, reverse active power monitoring.

## License

Licensed under the MIT License.
