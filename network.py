## ESTE YA ESTÁ
from dataclasses import dataclass, field
from enum import Enum
from random import randint
from random import random
import time
class TrafficType(Enum):
    WEB = "WEB"
    VIDEO = "VIDEO"
    AUDIO = "AUDIO"
    TEXT = "TEXT"
    ATTACK =  "ATTACK"
    PRINT = "PRINT"
    # HECHO: Definir los tipos de tráfico (WEB, VIDEO, AUDIO, TEXT, ATTACK, PRINT)
    pass

@dataclass
class Packet:
    # HECHO: Definir los campos del paquete (src, dst, traffic_type, size, timestamp, protocol)
    src: str
    dst: str
    traffic_type: str
    size: int
    protocol: str
    timestamp: float = field(default_factory=time.time)

class Host:
    def __init__(self, host_id, ip, role="normal"):
        # HECHO: Inicializar atributos del host
        self.id = host_id
        self.ip = ip
        self.role = role
        self.traffic_count = 0
        self.last_reset = time.time()
        
    def send_packet(self, dst, traffic_type, protocol):
        if traffic_type == TrafficType.VIDEO:
            size = randint(1000,1500)
        elif traffic_type == TrafficType.WEB:
            size = randint(500,1000)
        elif traffic_type == TrafficType.ATTACK:
            size = randint(64,128)
        else:
            size = randint(100,500)
    # HECHO: Crear y retornar un nuevo paquete
        return Packet(
            src=self.ip,
            dst=dst,
            traffic_type=traffic_type,
            size=size,
            protocol=protocol
        )
class Router:
    def __init__(self, router_id):
        self.id = router_id
        self.connections = {}
        self.congestion = 2.0
    # HECHO: Inicializar router con ID, conexiones y estado de congestión
        pass
    def process_packet(self, packet: Packet):
        print(f"Router {self.id} PROCESANDO PAQUETE ${packet.src} A ${packet.dst}")
        self.congestion += 0.01 * (packet.size / 1500)
        time.sleep(0.0001)
        
        if (self.congestion > 1.0):
            if random() < 0.01:
                print(f"Router {self.id} mandó a dormir el paquete por congestión")
                return False
            self.congestion *= 0.9
        return True
        # HECHO: Simular procesamiento de paquete
        pass