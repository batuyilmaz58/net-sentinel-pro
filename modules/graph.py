# graph.py dosyasındaki update_ui kısmına metinsel değerler eklendi
import asyncio
from collections import Counter, deque
from datetime import datetime
import scapy.all as scapy
from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from pysnmp.hlapi.v3arch.asyncio import *

async def get_snmp_data(ip):
    try:
        snmp_engine = SnmpEngine()
        auth_data = CommunityData('public', mpModel=0)
        transport = await UdpTransportTarget.create((ip, 161), timeout=1, retries=0)
        errorIndication, errorStatus, errorIndex, varBinds = await get_cmd(
            snmp_engine, auth_data, transport, ContextData(),
            ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysUpTime', 0))
        )
        if not errorIndication and not errorStatus:
            return str(varBinds[0][1])
    except: pass
    return "Bağlantı Yok"

class DeviceMonitorWorker(QThread):
    data_ready = Signal(dict)

    def __init__(self, target_ip):
        super().__init__()
        self.target_ip = target_ip
        self.running = True
        self.protocol_counter = Counter()

    def run(self):
        while self.running:
            snapshot = {}
            snapshot["time"] = datetime.now().strftime("%H:%M:%S")
            
            # SNMP asenkron yönetim
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            snapshot["snmp_status"] = loop.run_until_complete(get_snmp_data(self.target_ip))
            loop.close()

            packets = scapy.sniff(timeout=1.2, filter=f"host {self.target_ip}")
            snapshot["packets"] = len(packets)
            snapshot["traffic"] = sum(len(p) for p in packets) / (1024 * 1024)

            for p in packets:
                if p.haslayer(scapy.TCP): self.protocol_counter["TCP"] += 1
                elif p.haslayer(scapy.UDP): self.protocol_counter["UDP"] += 1
                elif p.haslayer(scapy.ICMP): self.protocol_counter["ICMP"] += 1

            snapshot["protocols"] = dict(self.protocol_counter)
            self.data_ready.emit(snapshot)

    def stop(self): self.running = False

class GraphWindow(QWidget):
    def __init__(self, target_ip):
        super().__init__()
        self.setWindowTitle(f"Cihaz Analizi: {target_ip}")
        self.resize(1000, 700)
        self.traffic_data = deque([0]*40, maxlen=40)
        self.packet_data = deque([0]*40, maxlen=40)
        self.protocols = Counter()

        layout = QVBoxLayout(self)
        self.info_lbl = QLabel("Veri bekleniyor...")
        layout.addWidget(self.info_lbl)

        self.figure = Figure(figsize=(10, 6))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        self.axes = self.figure.subplots(2, 2)

        self.worker = DeviceMonitorWorker(target_ip)
        self.worker.data_ready.connect(self.update_ui)
        self.worker.start()

    def update_ui(self, data):
        self.traffic_data.append(data["traffic"])
        self.packet_data.append(data["packets"])
        self.protocols.update(data["protocols"])
        
        self.info_lbl.setText(f"Hedef: {self.worker.target_ip} | SNMP Durumu: {data['snmp_status']}")

        ax1, ax2, ax3, ax4 = self.axes.flatten()
        for ax in [ax1, ax2, ax3, ax4]: ax.clear()

        # Metinsel Değerleri Başlıklara Yazma
        last_traffic = data["traffic"]
        ax1.plot(list(self.traffic_data), color="#2ecc71")
        ax1.set_title(f"Anlık Trafik: {last_traffic:.4f} MB")

        last_pkt = data["packets"]
        ax2.bar(range(len(self.packet_data)), list(self.packet_data), color="#e67e22")
        ax2.set_title(f"Paket Hızı: {last_pkt} pkt/sn")

        if self.protocols:
            ax3.pie(self.protocols.values(), labels=self.protocols.keys(), autopct='%1.1f%%')
        ax3.set_title("Protokol Dağılımı")

        ax4.text(0.5, 0.5, f"TOPLAM VERİ ANALİZİ\n\nToplam Paket: {sum(self.protocols.values())}\nDurum: İzleniyor", 
                 ha='center', va='center', fontsize=12, fontweight='bold')
        ax4.axis('off')

        self.figure.tight_layout()
        self.canvas.draw()

    def closeEvent(self, event):
        self.worker.stop()
        self.worker.wait()
        event.accept()

def show_device_graphs(target_ip):
    win = GraphWindow(target_ip)
    win.show()
    return win