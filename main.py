import sys
import psutil
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QListWidget, QPushButton, QMessageBox, QInputDialog
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QIcon

from modules.attack import NetworkEngine
from modules.graph import show_device_graphs
import os


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

STYLE = """
QMainWindow { background-color: #0d0d11; }
QLabel { color: #00ffcc; font-family: 'Segoe UI'; }
QListWidget { 
    background-color: #121217; 
    border: 1px solid #333; 
    border-radius: 10px; 
    color: #00ffcc; 
    font-family: 'Consolas';
}
QPushButton {
    background-color: #1a1a21;
    color: white;
    border: 1px solid #444;
    padding: 12px;
    border-radius: 8px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #00ffcc;
    color: black;
}
QPushButton#kickBtn {
    border: 1px solid #ff3366;
    color: #ff3366;
}
"""

class ModernDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.engine = NetworkEngine()
        self.setWindowTitle("Net-Sentinel Pro")
        self.setMinimumSize(800, 600)
        self.setStyleSheet(STYLE)
        self.setWindowIcon(QIcon(resource_path("icon.ico")))

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        self.info_lbl = QLabel("SİSTEM HAZIR")
        self.info_lbl.setAlignment(Qt.AlignCenter)
        self.info_lbl.setFont(QFont("Segoe UI", 12, QFont.Bold))
        layout.addWidget(self.info_lbl)

        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

        btn_box = QHBoxLayout()
        self.btn_scan = QPushButton("CİHAZLARI TARA")
        self.btn_graph = QPushButton("CANLI GRAFİK")
        self.btn_kick = QPushButton("BAĞLANTIYI KES")
        self.btn_kick.setObjectName("kickBtn")

        btn_box.addWidget(self.btn_scan)
        btn_box.addWidget(self.btn_graph)
        btn_box.addWidget(self.btn_kick)
        layout.addLayout(btn_box)

        self.btn_scan.clicked.connect(self.handle_scan)
        self.btn_graph.clicked.connect(self.handle_graph)
        self.btn_kick.clicked.connect(self.handle_kick)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_stats)
        self.timer.start(2000)

    def update_stats(self):
        net = psutil.net_io_counters()
        up = round(net.bytes_sent / 1024 / 1024, 2)
        down = round(net.bytes_recv / 1024 / 1024, 2)
        self.info_lbl.setText(f"IP: {self.engine.get_local_ip()} | UP: {up}MB | DOWN: {down}MB")

    def handle_scan(self):
            self.list_widget.clear()
            self.list_widget.addItem("Ağ taranıyor (Lütfen bekleyin)...")
            
            # Motor üzerinden taramayı başlat
            devices = self.engine.scan_devices()
            
            self.list_widget.clear()
            # Sütun başlıklarını daha okunaklı yapalım
            header = f"{'İP ADRESİ VE ETİKET':<40} | {'MAC ADRESİ'}"
            self.list_widget.addItem(header)
            self.list_widget.addItem("-" * 75)
            
            for d in devices:
                # d['display_ip'] içinde artık "192.168.1.1 (Modem)" gibi tam veri var
                line = f"{d['display_ip']:<40} | {d['mac']}"
                self.list_widget.addItem(line)

    def handle_graph(self):
        ip, ok = QInputDialog.getText(self, "Grafik", "Hedef IP:")
        if ok and ip: self.graph_win = show_device_graphs(ip)

    def handle_kick(self):
        if self.engine.is_attacking:
            self.engine.stop_attack()
            self.btn_kick.setText("BAĞLANTIYI KES")
            return

        target_ip, ok = QInputDialog.getText(self, "Test", "Kesilecek Hedef IP:")
        if ok and target_ip:
            gateway = ".".join(self.engine.get_local_ip().split(".")[:-1]) + ".1"
            self.engine.start_attack(target_ip, gateway)
            self.btn_kick.setText("DURDUR")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ModernDashboard()
    window.show()
    sys.exit(app.exec())