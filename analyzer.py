import matplotlib.pyplot as plt
import numpy as np
from scipy import fft
from network import TrafficType

class TrafficAnalyzer:
    def __init__(self, controller):
        self.controller = controller
        plt.style.use("dark_background")

    def plot_traffic_over_time(self, ax):
        history = self.controller.traffic_history
        if not history:
            ax.set_title("Tráfico en el Tiempo (Sin Datos)")
            return

        timestamps = np.array([t[0] for t in history])
        normal_traffic_times = [t for t, type in history if type != TrafficType.ATTACK]
        attack_traffic_times = [t for t, type in history if type == TrafficType.ATTACK]

        start_time = timestamps.min()
        end_time = timestamps.max()

        bins = np.linspace(start_time, end_time, 50) 
        
        normal_hist, _ = np.histogram(normal_traffic_times, bins=bins)
        attack_hist, _ = np.histogram(attack_traffic_times, bins=bins)

        bin_centers = (bins[:-1] + bins[1:]) / 2
        relative_time = bin_centers - start_time 

        ax.plot(relative_time, normal_hist, label="Tráfico Normal", color="cyan", marker='o', linewidth=2, alpha=0.8, linestyle='--')
        ax.plot(relative_time, attack_hist, label="Tráfico de Ataque", color="#ff00ff",linewidth=2, marker='x')
        ax.set_title("Tráfico en el Tiempo (Paquetes por ventana)")
        ax.set_xlabel("Tiempo (segundos)")
        ax.set_ylabel("Volumen de Paquetes")
        ax.grid(True, alpha=0.3)
        ax.legend()
        ax.grid(True)

    def plot_blocked_hosts(self, ax):
        blocked_count = len(self.controller.blocked_hosts)
        total_hosts = len(self.controller.hosts)
        active_count = total_hosts - blocked_count

        labels = ['Activos', 'Bloqueados']
        counts = [active_count, blocked_count]
        colors = ['green', 'red']

        ax.bar(labels, counts, color=colors)
        ax.set_title("Estado de los Hosts")
        ax.set_ylabel("Cantidad de Hosts")
        for i, count in enumerate(counts):
            ax.text(i, count + 0.1, str(count), ha='center', fontweight='bold')

    def simulate_fourier_analysis(self, ax):
        
        N = 600 
        T = 1.0 / 100.0 
        time = np.linspace(0.0, N*T, N, endpoint=False)
        
        normal_signal = 0.5 * np.sin(2.0 * np.pi * 5.0 * time) 
        normal_signal += np.random.randn(N) * 0.5 
        
        attack_burst = 1.5 * np.sin(2.0 * np.pi * 40.0 * time) 
        attack_signal = normal_signal + attack_burst
        
        normal_fft = fft.fft(normal_signal)
        attack_fft = fft.fft(attack_signal)
        
        freq = fft.fftfreq(N, T)[:N//2] 
        
        normal_mag = 2.0/N * np.abs(normal_fft[0:N//2])
        attack_mag = 2.0/N * np.abs(attack_fft[0:N//2])
        
        ax.plot(freq, normal_mag, label="Espectro Normal", color='blue', alpha=0.7)
        ax.plot(freq, attack_mag, label="Espectro de Ataque", color='red', linestyle='--')
        ax.set_title("Análisis de Fourier (Simulado)")
        ax.set_xlabel("Frecuencia (Hz)")
        ax.set_ylabel("Amplitud")
        ax.legend()
        ax.grid(True)

    def show_all_analytics(self):
        print("\nSimulación finalizada. Generando analíticas...")
        
        fig, axs = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle("Dashboard de Análisis de Red SDN", fontsize=16)

        self.plot_traffic_over_time(axs[0, 0])
        self.plot_blocked_hosts(axs[0, 1])
        self.simulate_fourier_analysis(axs[1, 0])
                
        ax_info = axs[1, 1]
        ax_info.axis('off')
        info_text = (
            f"Resumen de Simulación:\n"
            f"--------------------------\n"
            f"Total de Hosts: {len(self.controller.hosts)}\n"
            f"Hosts Bloqueados: {len(self.controller.blocked_hosts)}\n"
            f"IPs Bloqueadas: {', '.join(self.controller.blocked_hosts) or 'Ninguna'}\n\n"
            f"Total de Paquetes: {len(self.controller.traffic_history)}\n"
            f"Umbral de Ataque: {self.controller.attack_threshold} pps"
        )
        ax_info.text(0.5, 0.5, info_text, 
                     horizontalalignment='center', 
                     verticalalignment='center', 
                     fontsize=12, 
                     fontfamily='monospace',
                     bbox=dict(boxstyle="round,pad=1", fc="black", ec="grey"))
        ax_info.set_title("Resumen de Ejecución")
        
        plt.tight_layout(rect=[0, 0.03, 1, 0.95]) 
        plt.show()