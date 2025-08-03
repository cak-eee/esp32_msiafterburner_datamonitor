import time
import os

# --- AYARLAR ---
UPDATE_INTERVAL = 1

# --- OTOMATİK DOSYA YOLU BULMA ---
try:
    program_files_x86 = os.environ['ProgramFiles(x86)']
    LOG_FILE_PATH = os.path.join(program_files_x86, "MSI Afterburner", "HardwareMonitoring.hml")
except KeyError:
    LOG_FILE_PATH = r"C:\Program Files (x86)\MSI Afterburner\HardwareMonitoring.hml"

# --- FİLTRE ---
# EKRANDA GÖRMEK İSTEDİĞİMİZ SENSÖRLERİN LİSTESİ
# Bu isimlerin, log dosyasındaki başlıklarla tam olarak eşleşmesi gerekiyor.
ISTENEN_SENSÖRLER = [
    "GPU temperature",
    "GPU usage",
    "Core clock",
    "Power",           # Afterburner genellikle tek bir "Power" değeri verir, bu GPU gücüdür.
    "Fan speed",
    "Fan tachometer",
    "CPU temperature",
    "CPU usage",
    "CPU clock",       # Bu genellikle tüm çekirdeklerin ortalaması veya en yükseğidir.
    "CPU power",
    "RAM usage",
    "Framerate",
    "Frametime"
]

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def follow(thefile):
    thefile.seek(0, 2)
    while True:
        line = thefile.readline()
        if not line:
            time.sleep(0.1)
            continue
        yield line.strip()

# --- ANA PROGRAM ---
print("MSI Afterburner Filtrelenmis Canli Log Okuyucu Baslatildi.")
time.sleep(2)

try:
    with open(LOG_FILE_PATH, 'r') as logfile:
        lines = [line.strip() for line in logfile.readlines() if line.strip()]
        if len(lines) < 3:
            print("HATA: Log dosyasi yeterli veri icermiyor.")
            exit()
        
        header_line = lines[2]
        headers = [h.strip().replace('"', '') for h in header_line.split(',')][2:]
        
        log_lines = follow(logfile)
        
        for line in log_lines:
            clear_screen()
            print(f"--- {time.strftime('%H:%M:%S')} itibariyle Filtrelenmis Canli Veriler ---")
            
            values = [v.strip() for v in line.split(',')][2:]
            
            if len(headers) == len(values):
                # Her bir sensör ve değerini kontrol et
                for header, value in zip(headers, values):
                    # Sadece istediğimiz sensörleri yazdır
                    if header in ISTENEN_SENSÖRLER:
                        try:
                            display_value = f"{float(value):.1f}"
                        except (ValueError, TypeError):
                            display_value = value
                        
                        print(f"{header:<25}: {display_value}")
            else:
                print("Veri hatasi: Baslik ve sutun sayisi eslesmiyor.")

            time.sleep(UPDATE_INTERVAL)

except FileNotFoundError:
    print(f"HATA: Log dosyasi bulunamadi! -> {LOG_FILE_PATH}")
except KeyboardInterrupt:
    print("\n\nProgram sonlandırıldı.")
except Exception as e:
    print(f"\nBeklenmedik bir hata olustu: {e}")