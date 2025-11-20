import time
# sdn_controller.py - ESQUELETO BASE
from network import Packet, Host,Router
class SimpleSDNController:
    def __init__(self):
        # HECHO: Inicializar estructuras de datos
        self.hosts = {}  
        self.routers = {}
        self.blocked_hosts = set()
        self.traffic_history = []
        self.attack_threshold = 30 # Paquetes/segundo
    def add_host(self, host: Host):
        # HECHO: Agregar host a la red
        print(f"Controlador: Host {host.id} ({host.ip} añadido.)")
        self.hosts[host.ip] = host
        pass
    def add_router(self, router: Router):
        # HECHO: Agregar router a la red
        print(f"Controlador: Router {router.id} añadido.")
        self.routers[router.id] = router
        pass
    def detect_attacks(self):
    # HECHO: Implementar detección de ataques por tasa de paquetes
        current_time = time.time()
        
        for id,host_data in self.hosts.items():
            if id in self.blocked_hosts:
                continue
            
            elapsed = current_time - host_data.last_reset
            if elapsed >= 1.0:
                packet_rate = host_data.traffic_count / elapsed

                if packet_rate > self.attack_threshold:
                    print(f"¡¡¡ATAQUE DETECTADO!!! Fuente: {host_data.id} (Tasa: {packet_rate:.2f} pps)")
                    print(f"Controlador: Bloqueando host {host_data.id}.")
                    self.blocked_hosts.add(id)
                
                host_data.traffic_count = 0
                host_data.last_reset = current_time
            pass
    def route_packet(self, packet: Packet):
        # 1. Agregar a historial
        
        self.traffic_history.append((packet.timestamp, packet.traffic_type))
        
        # 2. Verificar si el host fuente está bloqueado
        if packet.src in self.blocked_hosts:
        # 3. Aplicar detección de ataques
            return "BLOCKED"
        
        
        host = self.hosts.get(packet.src)
        # 4. Retornar decisión de enrutamiento
        if host:
            host.traffic_count += 1
        else:
            print(f"[ERROR] ¡Host desconocido! IP recibida en paquete: '{packet.src}'")
            print(f"        IPs registradas en controlador: {list(self.hosts.keys())}")
        
        # HECHO: Decidir ruta y detectar ataques
        return "FORWARDED"

        pass    