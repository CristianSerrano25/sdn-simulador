import random
from sdn_controller import SimpleSDNController
from network import Host, Router, TrafficType, Packet
from analyzer import TrafficAnalyzer
import threading
import time
import traceback  
class NetworkSimulator:
    def __init__(self):
        self.controller = SimpleSDNController()
        self.analyzer = TrafficAnalyzer(self.controller)
        self.setup_network()
        self.running = False
    def setup_network(self):
        # HECHO: Configurar 6 hosts y 2 routers
        print("Configurando red")
        
        # H4 como servidor web, H5 como impresora
        hosts = [
            Host("H1", "192.168.1.1", role="normal"),
            Host("H2", "192.168.1.2", role="normal"),
            Host("H3", "192.168.1.3", role="normal"),
            Host("H4", "192.168.1.4", role="server"), 
            Host("H5", "192.168.1.5", role="printer"),
            Host("H6", "192.168.1.6", role="attacker") 
        ]
        
        routers = [
            Router("R1"),
            Router("R2")
        ]

        for host in hosts:
            self.controller.add_host(host)
        
        for router in routers:
            self.controller.add_router(router)
        pass
    def generate_normal_traffic(self):
        host_ips = [h.ip for h in self.controller.hosts.values() if h.role != 'attacker']
        
        while self.running:
            try:
                src_ip = random.choice(host_ips)
                dst_ip = random.choice(host_ips)
                if src_ip == dst_ip:
                    continue
                
                traffic_type = random.choice([
                    TrafficType.WEB, TrafficType.VIDEO, TrafficType.AUDIO, 
                    TrafficType.TEXT, TrafficType.PRINT
                ])
                
                src_host = self.controller.hosts[src_ip]
                packet = src_host.send_packet(dst_ip, traffic_type, "TCP")
                
                # Este era para ver qué hacía cada host
                # print(f"--> Host {src_ip} enviando {traffic_type.name} a {dst_ip}")
                
                self.controller.route_packet(packet)
                
                time.sleep(random.uniform(0.1, 0.5)) 
            except Exception as e:
                print("\n!!! ERROR EN HILO DE TRÁFICO NORMAL !!!")
                traceback.print_exc()
                print(f"Error en tráfico normal: {e}")
                self.running = False
        # HECHO: Generar tráfico normal entre hosts
        pass
    def generate_attack_traffic(self):
        try:
            attacker = self.controller.hosts["192.168.1.6"]
            victim_ip = "192.168.1.4" 
            print(f"\nIniciando hilo de ataque: {attacker.ip} -> {victim_ip}\n")
        except KeyError:
            print("No se encontró al atacante o víctima.")
            return

        while self.running:
            packet = attacker.send_packet(victim_ip, TrafficType.ATTACK, "UDP")
            self.controller.route_packet(packet)
            
            time.sleep(random.uniform(0.001, 0.005))
        # HECHO: Generar tráfico de ataque aleatorio
        pass
    
    def run_detector(self):
        while self.running:
            time.sleep(1.0) 
            self.controller.detect_attacks()
        
    
    def run_simulation(self, duration=60):
        print(f"\nIniciando simulación SDN por {duration} segundos...")
        self.running = True

        t_normal = threading.Thread(target=self.generate_normal_traffic, daemon=True)
        t_attack = threading.Thread(target=self.generate_attack_traffic, daemon=True)
        t_detector = threading.Thread(target=self.run_detector, daemon=True)

        t_normal.start()
        t_attack.start()
        t_detector.start()

        try:
            start_time = time.time()
            while time.time() - start_time < duration:
                print(f"Simulación en curso... {int(duration - (time.time() - start_time))}s restantes. "
                      f"Bloqueados: {len(self.controller.blocked_hosts)}", end='\r')
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nSimulación interrumpida manualmente.")
            
        self.running = False
        print("\nDeteniendo hilos de simulación...")
        
        time.sleep(2) 

        self.analyzer.show_all_analytics()
        # HECHO: Ejecutar simulación con múltiples hilos
        pass

if __name__ == "__main__":
    simulator = NetworkSimulator()
    simulator.run_simulation(duration=3)