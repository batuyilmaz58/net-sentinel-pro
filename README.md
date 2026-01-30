# 🛡️ Net-Sentinel Pro v3.0

## Paylaşımlı Ağlar İçin Trafik Analiz ve Gecikme (Ping) Optimizasyon Aracı

Net-Sentinel, yerel ağınızdaki (LAN) veri trafiğini analiz etmek, cihazların ağ üzerindeki etkisini ölçmek ve paylaşımlı bağlantılarda (KYK, yurt, ofis vb.) oyun performansını (Ping) stabilize etmek için geliştirilmiş bir Ağ Stres Testi aracıdır.

## 🚀 Öne Çıkan Özellikler

- Üçlü Hibrit Saldırı Motoru: ARP Spoofing, UDP Flooding ve TCP Reset yöntemlerini aynı anda kullanarak hedef cihazın bant genişliğini kısıtlar.

- Canlı Şebeke Analizi: graph.py modülü ile hedef cihazın anlık paket hızını, trafik hacmini ve kullandığı protokolleri (TCP/UDP/ICMP) görselleştirir.

- Donanım Gerektirmez: Kali Linux veya harici Wi-Fi kartı (Monitor Mode) gerektirmeden, standart Windows ağ sürücüleri (Npcap) ile çalışır.

- Modern Arayüz: PySide6 ile güçlendirilmiş, kullanıcı dostu ve karanlık tema odaklı GUI.

## 🛠️ Nasıl Çalışır? (Teknik Yaklaşım)

Bu araç, ağdaki gecikme (ping) sorunlarını çözmek için üç aşamalı bir strateji izler:

- ARP Spoofing: Hedef cihazın modem ile olan iletişim yolunu kendi üzerinizden geçirerek trafiği manipüle eder.

- UDP Flood: Hedef cihazın ağ tamponunu (buffer) anlamsız veri paketleriyle doldurarak cihazın modemden veri çekme önceliğini düşürür.

- TCP Reset: Hedef cihazın kurduğu aktif internet bağlantılarını (sosyal medya, video akışları) yakalayarak zorla sonlandırır.

## 📦 Kurulum ve Hazırlık

- Projenin çalışması için sisteminizde Python 3.10+ ve ağ paketlerini yönetebilmek için Npcap kurulu olmalıdır.

- Npcap Yükleyin: npcap.com adresinden indirin (Kurulumda "Support raw 802.11 traffic" seçeneğini işaretleyin).

    ### Gerekli Kütüphaneler:

    - Bash
    - pip install PySide6 scapy psutil matplotlib pysnmp
    - Çalıştırma: Terminali veya IDE'nizi Yönetici Olarak Çalıştırın ve ana dosyayı başlatın:

    - Bash
    - python main.py

    - Exe ilede çalıştırılabilir exe'yi yönetici olarak açın.

## 🎮 Kullanım Senaryosu: Ping Düşürme

- Paylaşımlı bir ağda (Örn: KYK Yurdu) oyun oynarken yüksek ping alıyorsanız:

- CİHAZLARI TARA butonu ile odadaki diğer cihazları bulun.

- Yüksek veri tüketen (YouTube/Netflix izleyen) cihazın IP adresini seçin.

- BAĞLANTIYI KES (veya Optimize Et) butonuna basarak o cihazın bant genişliğini daraltın.

- Modem üzerindeki yük hafiflediği için oyun paketleriniz (LOL, CS, Valorant vb.) daha hızlı iletilecek ve pinginiz düşecektir.

## ⚠️ Önemli Uyarılar

- Yönetici İzni: Windows güvenlik duvarını aşmak ve paket enjekte etmek için uygulama yönetici haklarıyla çalıştırılmalıdır.

- Apple Cihazlar: iPhone cihazlar uykudayken taramalarda görünmeyebilir. Tarama yaparken hedef cihazın ekranının açık olduğundan emin olun. 

- Arkadaşınızın telefonu Apple cihaz ise telefonunu ondan rica edin wifi kısmında bağlı wifi bloğunda ekstra bilgi tuşunda IP adresi yazar.

- Etik Kullanım: Bu araç yalnızca kendi ağınızda test yapmak ve eğitim amaçlı kullanım için tasarlanmıştır.