import sys
import psutil
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QListWidget, QPushButton, QMessageBox, QInputDialog, QFrame
)
from PySide6.QtCore import Qt, QTimer, QThread, Signal
from PySide6.QtGui import QFont, QIcon

from modules.attack import NetworkEngine
from modules.graph import show_device_graphs
import scapy.all as scapy

# --- ARKA PLAN TARAMA İŞÇİSİ ---
class ScanWorker(QThread):
    """Tarama işlemini arayüzü dondurmadan arka planda yapar."""
    finished = Signal(list)

    def __init__(self, engine):
        super().__init__()
        self.engine = engine

    def run(self):
        devices = self.engine.scan_devices()
        self.finished.emit(devices)

# --- MODERN STİL ---
STYLE = """
QMainWindow { background-color: #0f1016; }
QLabel { color: #00f2ff; font-family: 'Segoe UI'; }
QListWidget { 
    background-color: #161b22; 
    border: none; 
    border-radius: 6px; 
    color: #e6edf3; 
    font-family: 'Consolas';
    font-size: 13px;
    padding: 10px;
}
QPushButton {
    background-color: #21262d;
    color: #c9d1d9;
    border: 1px solid #30363d;
    padding: 10px;
    border-radius: 6px;
    font-weight: 600;
}
QPushButton:hover {
    background-color: #30363d;
    border-color: #8b949e;
}
QPushButton#scanBtn { background-color: #238636; color: white; border: none; }
QPushButton#scanBtn:hover { background-color: #2ea043; }
QPushButton#kickBtn { background-color: #da3633; color: white; border: none; }
QPushButton#kickBtn:hover { background-color: #f85149; }
"""

class ModernDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.engine = NetworkEngine()
        self.setWindowTitle("Net-Sentinel Pro v2")
        self.setMinimumSize(850, 550)
        self.setStyleSheet(STYLE)

        # UI Kurulumu
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header Bölümü
        self.info_lbl = QLabel("SİSTEM BAŞLATILIYOR...")
        self.info_lbl.setFont(QFont("Segoe UI", 10))
        layout.addWidget(self.info_lbl)

        # Liste
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

        # Butonlar
        btn_box = QHBoxLayout()
        self.btn_scan = QPushButton("AĞI TARA")
        self.btn_scan.setObjectName("scanBtn")
        self.btn_graph = QPushButton("CANLI İZLE")
        self.btn_kick = QPushButton("BAĞLANTI KES")
        self.btn_kick.setObjectName("kickBtn")

        btn_box.addWidget(self.btn_scan)
        btn_box.addWidget(self.btn_graph)
        btn_box.addWidget(self.btn_kick)
        layout.addLayout(btn_box)

        # Event Bağlantıları
        self.btn_scan.clicked.connect(self.start_async_scan)
        self.btn_graph.clicked.connect(self.handle_graph)
        self.btn_kick.clicked.connect(self.handle_kick)

        # Stats Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_stats)
        self.timer.start(2000)

    def update_stats(self):
        net = psutil.net_io_counters()
        up = round(net.bytes_sent / 1024 / 1024, 1)
        down = round(net.bytes_recv / 1024 / 1024, 1)
        self.info_lbl.setText(f"📡 LOCAL IP: {self.engine.get_local_ip()}   |   ⬆ {up} MB   |   ⬇ {down} MB")

    # --- ASENKRON TARAMA METOTLARI ---
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

    def handle_graph(self):
        # Mevcut kodunuzu koruyabilirsiniz
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