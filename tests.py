import unittest
import time
import matplotlib.pyplot as plt
from network import Host, Packet, TrafficType
from sdn_controller import SimpleSDNController
from analyzer import TrafficAnalyzer

class TestSDNNetwork(unittest.TestCase):

    def setUp(self):
        """Se ejecuta antes de CADA prueba. Crea un ambiente limpio."""
        self.controller = SimpleSDNController()
        self.host1 = Host("H1", "10.0.0.1")
        self.host2 = Host("H2", "10.0.0.2")
        self.controller.add_host(self.host1)
        self.controller.add_host(self.host2)
        
        self.analyzer = TrafficAnalyzer(self.controller)

    def test_attack_detection(self):
        """Verificar que se detecten hosts que envían demasiados paquetes"""
        print("\nEjecutando prueba: Detección de Ataques...")

        self.host1.traffic_count = 150  
        self.host1.last_reset = time.time() - 1.1         
        self.host2.traffic_count = 20
        self.host2.last_reset = time.time() - 1.1
        self.controller.detect_attacks()


        self.assertIn("10.0.0.1", self.controller.blocked_hosts, 
                        "FALLO: El Host 1 debería haber sido bloqueado por exceso de tráfico.")
        
        self.assertNotIn("10.0.0.2", self.controller.blocked_hosts, 
                        "FALLO: El Host 2 fue bloqueado incorrectamente.")
        
        print(">> Prueba de Detección: PASÓ")

    def test_routing_decisions(self):
        """Verificar que el enrutamiento funcione correctamente"""
        print("\nEjecutando prueba: Decisiones de Enrutamiento...")

        packet_normal = self.host1.send_packet("10.0.0.2", TrafficType.WEB, "TCP")
        decision = self.controller.route_packet(packet_normal)
        
        self.assertEqual(decision, "FORWARDED", 
                        "FALLO: El tráfico normal debería ser reenviado.")

        self.controller.blocked_hosts.add("10.0.0.1")
        
        packet_blocked = self.host1.send_packet("10.0.0.2", TrafficType.WEB, "TCP")
        decision_blocked = self.controller.route_packet(packet_blocked)

        self.assertEqual(decision_blocked, "BLOCKED", 
                        "FALLO: El tráfico de una IP bloqueada debería ser rechazado.")
        
        print(">> Prueba de Enrutamiento: PASÓ")

    def test_traffic_analysis(self):
        """Verificar que el análisis de tráfico genere gráficas sin errores"""
        print("\nEjecutando prueba: Análisis de Tráfico...")

        self.controller.traffic_history = [
            (time.time(), TrafficType.WEB),
            (time.time(), TrafficType.ATTACK),
            (time.time(), TrafficType.VIDEO)
        ]

        try:
            fig, ax = plt.subplots()
            self.analyzer.plot_traffic_over_time(ax)
            plt.close(fig) 
            success = True
        except Exception as e:
            success = False
            print(f"Error al graficar: {e}")

        self.assertTrue(success, "FALLO: El analizador lanzó un error al intentar graficar.")
        print(">> Prueba de Análisis: PASÓ")

if __name__ == '__main__':
    unittest.main()