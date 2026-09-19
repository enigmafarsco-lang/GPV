# RFSoC-to-PC data contract
Raw file: little-endian int16 I,Q interleaved, shape [average,tone,position]. UDP GPR1 carries frame, packet, tone and position identifiers plus complex int16 payload. Missing packets invalidate a position unless an explicit policy is enabled.
