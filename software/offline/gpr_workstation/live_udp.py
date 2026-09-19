import socket,struct,numpy as np
from dataclasses import dataclass
HEADER_FMT='!4sBBHIHHHHIQ';HEADER_BYTES=struct.calcsize(HEADER_FMT)
@dataclass
class Packet:frame_id:int;packet_id:int;packet_count:int;tone0:int;tone_count:int;position_id:int;timestamp_ns:int;iq:np.ndarray
def parse_packet(data,magic=b'GPR1'):
 if len(data)<HEADER_BYTES:raise ValueError('short packet')
 mg,ver,flags,hb,fr,pid,pc,t0,tc,pos,ts=struct.unpack(HEADER_FMT,data[:HEADER_BYTES]);
 if mg!=magic:raise ValueError('bad magic')
 a=np.frombuffer(data[hb:],dtype='<i2');
 if len(a)!=tc*2:raise ValueError('payload length mismatch')
 a=a.reshape(tc,2);return Packet(fr,pid,pc,t0,tc,pos,ts,a[:,0].astype(float)+1j*a[:,1].astype(float))
class UDPFrameReceiver:
 def __init__(self,host='0.0.0.0',port=50000,timeout=1):self.s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM);self.s.bind((host,port));self.s.settimeout(timeout)
 def receive_position(self,n_tones):
  chunks={};fid=pos=ts=pc=None
  while True:
   p=parse_packet(self.s.recvfrom(65535)[0])
   if fid is None:fid,pos,ts,pc=p.frame_id,p.position_id,p.timestamp_ns,p.packet_count
   if p.frame_id!=fid or p.position_id!=pos:continue
   chunks[p.packet_id]=p
   if len(chunks)==pc:
    out=np.zeros(n_tones,complex)
    for q in chunks.values():out[q.tone0:q.tone0+q.tone_count]=q.iq
    return fid,pos,ts,out
