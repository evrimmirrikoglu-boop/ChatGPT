# PhonePad Web

iPhone (veya herhangi bir telefon) tarayıcısını, bilgisayarında **gerçek sistem faresini** kontrol eden kaliteli bir touchpad'e çeviren web tabanlı çözüm.

> Not: Tarayıcılar güvenlik nedeniyle doğrudan işletim sistemi faresini hareket ettiremez. Bu yüzden PC tarafında küçük bir Python köprü uygulaması çalışır. Telefon tarafı tamamen web'dir.

## Özellikler

- Tek parmak: hassas imleç hareketi
- Tek dokunma: sol tık
- İki parmak dokunma: sağ tık
- Çift dokunma: çift tık
- İki parmak sürükleme: dikey/yatay scroll
- Gerçek zamanlı WebSocket iletişimi
- Eşleştirme için tek kullanımlık session token
- Mobilde düşük gecikme için `requestAnimationFrame` tabanlı gönderim

## Gereksinimler

- Python 3.10+
- Bağımlılıklar:
  - `websockets`
  - `pynput`

## Kurulum

### Windows (`py` komutu olan sistemler)

```powershell
py -m venv .venv
.\.venv\Scripts\activate
py -m pip install -r requirements.txt
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

## Çalıştırma

### Windows

```powershell
py bridge.py
```

### macOS / Linux

```bash
python3 bridge.py
```

Sonra terminalde görünen adımları takip et:

1. Script sana bilgisayar IP adresini ve token'ı verir.
2. Telefonda aç: `http://BILGISAYAR_IP:8765`
3. Ekrandaki token alanına terminalde yazan token'ı gir.
4. **Bağlan** butonuna bas.

## Aynı Wi‑Fi zorunlu mu?

Hayır, zorunlu değil. 2 kullanım şekli var:

1. **Aynı ağ (en düşük gecikme)**
   - Direkt `http://BILGISAYAR_IP:8765` üzerinden bağlan.

2. **Farklı ağ / internet üzerinden**
   - Bilgisayardaki `8765` (UI) ve `8766` (WS) portlarını dışarı açman gerekir.
   - En pratik yöntemler:
     - Tailscale / ZeroTier ile sanal aynı ağ kurmak (önerilir).
     - Router port forwarding + domain/reverse proxy.
   - Eğer siteyi `https://` ile açıyorsan WebSocket adresi `wss://` olmalı.

İstersen scripti public URL bilgisiyle başlatabilirsin:

```bash
python3 bridge.py --public-url https://pad.senin-domainin.com
```

## İndirme

Bu ortamda sana herkese açık bir dosya hosting linki üretemiyorum; ama projeyi bu depodan ZIP olarak indirebilirsin:

- GitHub'da: **Code → Download ZIP**
- veya terminal:

```bash
git clone <repo-url>
```

## Ayarlar

- **Sensitivity** ile hareket hassasiyeti
- **Invert scroll** ile scroll yönü

## Güvenlik

- Token eşleşmesi olmadan komut kabul etmez.
- İnternetten açarsan mutlaka güçlü ağ kuralları/VPN kullan.
- `bridge.py` içinde host/port parametrelerini CLI ile değiştirebilirsin.
