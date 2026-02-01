import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QInputDialog
from PySide6.QtCore import QTimer, QThread, Signal
from modules.ui import Ui_Dashboard 
from modules.attack import NetworkEngine
from modules.graph import show_device_graphs
import scapy.all as scapy
import psutil

class ScanWorker(QThread):
    finished = Signal(list)
    def __init__(self, engine):
        super().__init__()
        self.engine = engine
    def run(self):
        devices = self.engine.scan_devices()
        self.finished.emit(devices)

class ModernDashboard(QMainWindow, Ui_Dashboard):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.engine = NetworkEngine()
        
        # Sinyal-Slot Bağlantıları
        self.btn_scan.clicked.connect(self.start_async_scan)
        self.btn_kick.clicked.connect(self.handle_kick)
        self.btn_graph.clicked.connect(self.handle_graph)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_stats)
        self.timer.start(2000)

    def start_async_scan(self):
        self.list_widget.clear()
        self.list_widget.addItem("⏳ Tarama işlemi arka planda başlatıldı, lütfen bekleyin...")
        self.btn_scan.setEnabled(False) # Tarama bitene kadar butonu kapat
        
        self.worker = ScanWorker(self.engine)
        self.worker.finished.connect(self.on_scan_finished)
        self.worker.start()


    def on_scan_finished(self, devices):
        self.list_widget.clear()
        self.btn_scan.setEnabled(True)
        
        header = f"{'IP ADRESİ VE ETİKET':<45} | {'MAC ADRESİ'}"
        self.list_widget.addItem(header)
        self.list_widget.addItem("="*80)
        
        for d in devices:
            line = f"{d['display_ip']:<45} | {d['mac']}"
            self.list_widget.addItem(line)

    def update_stats(self):
        net = psutil.net_io_counters()
        up = round(net.bytes_sent / 1024 / 1024, 1)
        down = round(net.bytes_recv / 1024 / 1024, 1)
        self.info_lbl.setText(f"📡 LOCAL IP: {self.engine.get_local_ip()}   |   ⬆ {up} MB   |   ⬇ {down} MB")

    def handle_graph(self):
        ip, ok = QInputDialog.getText(self, "Grafik", "Hedef IP:")
        if ok and ip:
            scapy.send(scapy.IP(dst=ip)/scapy.ICMP(), verbose=False, count=1)
            self.graph_win = show_device_graphs(ip)

    def handle_kick(self):
        if self.engine.is_attacking:
            self.engine.stop_attack()
            self.btn_kick.setText("BAĞLANTI KES")
            return
        target_ip, ok = QInputDialog.getText(self, "Saldırı", "Kesilecek Hedef IP:")
        if ok and target_ip:
            gateway = ".".join(self.engine.get_local_ip().split(".")[:-1]) + ".1"
            self.engine.start_attack(target_ip, gateway)
            self.btn_kick.setText("SALDIRIYI DURDUR")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ModernDashboard()
    window.show()
    sys.exit(app.exec())