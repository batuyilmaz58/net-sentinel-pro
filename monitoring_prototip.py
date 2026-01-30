# live_protocol_monitor.py
from scapy.all import sniff, IP, TCP, UDP, ICMP
import socket
from collections import Counter
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# -------------------------------
# IP TESPİTİ
# -------------------------------
def get_own_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    finally:
        s.close()

OWN_IP = get_own_ip()
protocol_counter = Counter()

# -------------------------------
# PAKET SINIFLANDIRMA
# -------------------------------
def classify_packet(pkt):
    if IP not in pkt:
        return

    ip = pkt[IP]
    if ip.src != OWN_IP and ip.dst != OWN_IP:
        return

    if ICMP in pkt:
        protocol_counter["ICMP"] += 1

    elif TCP in pkt:
        tcp = pkt[TCP]
        if 80 in (tcp.sport, tcp.dport):
            protocol_counter["HTTP"] += 1
        elif 443 in (tcp.sport, tcp.dport):
            protocol_counter["HTTPS"] += 1
        elif 22 in (tcp.sport, tcp.dport):
            protocol_counter["SSH"] += 1
        else:
            protocol_counter["TCP"] += 1

    elif UDP in pkt:
        udp = pkt[UDP]
        if 53 in (udp.sport, udp.dport):
            protocol_counter["DNS"] += 1
        else:
            protocol_counter["UDP"] += 1

# -------------------------------
# CANLI GRAFİK
# -------------------------------
fig, ax = plt.subplots()

def update(frame):
    ax.clear()

    if not protocol_counter:
        ax.set_title("Trafik bekleniyor...")
        return

    protocols = list(protocol_counter.keys())
    counts = list(protocol_counter.values())

    ax.bar(protocols, counts)
    ax.set_title(f"Canlı Ağ Protokol Dağılımı ({OWN_IP})")
    ax.set_xlabel("Protokol")
    ax.set_ylabel("Paket Sayısı")
    ax.grid(True, axis="y")

# -------------------------------
# PAKET DİNLEYİCİ (NON-BLOCKING)
# -------------------------------
def start_sniffing():
    sniff(prn=classify_packet, store=False)

# -------------------------------
# ANA ÇALIŞMA
# -------------------------------
if __name__ == "__main__":
    print(f"İzlenen IP: {OWN_IP}")
    print("Ağ trafiği dinleniyor...")

    import threading
    sniff_thread = threading.Thread(target=start_sniffing, daemon=True)
    sniff_thread.start()

    ani = FuncAnimation(fig, update, interval=1000)
    plt.show()
