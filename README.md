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
- Aynı Wi‑Fi ağına bağlı telefon + bilgisayar
- Bağımlılıklar:
  - `websockets`
  - `pynput`

Kurulum:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Çalıştırma

```bash
python3 bridge.py
```

Sonra terminalde görünen adımları takip et:

1. Script sana bilgisayar IP adresini ve token'ı verir.
2. Telefonda şu adresi aç: `http://BILGISAYAR_IP:8765`
3. Ekrandaki token alanına terminalde yazan token'ı gir.
4. Connect'e bas.

Artık telefon touchpad olarak çalışır.

## Ayarlar

- **Sensitivity** ile hareket hassasiyeti
- **Invert scroll** ile scroll yönü

## Güvenlik

- Sunucu yalnızca local ağ için tasarlandı.
- Token eşleşmesi olmadan komut kabul etmez.
- İstersen `bridge.py` içinde host/port değerlerini değiştir.
