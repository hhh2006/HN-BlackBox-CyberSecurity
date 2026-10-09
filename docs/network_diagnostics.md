# Real Network Diagnostics

HN BlackBox now includes a local/private-scope network diagnostics deck.

- TCP connect port scanning for an explicitly selected host.
- Bounded private IPv4 subnet scanning (maximum 256 addresses; eight ports per subnet run).
- OS-visible TCP/UDP socket endpoint inspection through psutil when available.
- Real interface byte/packet/error/drop counters through psutil.
- Read-only OS routing-table inspection.
- Topology matrix derived from local interfaces, routing gateways, and private/local socket peers.
- Autonomous HUD animation is driven by the shared ~60 FPS compositor and does not depend on mouse hover.
- Clipboard export is local only.

## Packet capture boundary

`CAPTURE PACKETS` enables live **socket-flow and interface-counter telemetry**. It intentionally does **not** collect raw packet payloads or inject traffic. Raw packet capture is platform/privilege dependent and is not silently substituted with fabricated data.

## Safety boundary

The scanner rejects public/non-local targets and oversized scopes. No exploit, credential attack, packet injection, or route-table modification is performed. `FLUSH ROUTING` clears the application view/cache only; it does not change operating-system routes.
