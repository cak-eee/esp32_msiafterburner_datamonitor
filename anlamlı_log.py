import time
import os

# --- AYARLAR ---
UPDATE_INTERVAL = 1  # Saniyede bir güncelleme

# --- OTOMATİK DOSYA YOLU BULMA ---
try:
    program_files_x86 = os.environ['ProgramFiles(x86)']
    LOG_FILE_PATH = os.path.join(program_files_x86, "MSI Afterburner", "HardwareMonitoring.hml")
except KeyError:
    LOG_FILE_PATH = r"C:\Program Files (x86)\MSI Afterburner\HardwareMonitoring.hml"

def clear_screen():
    """Terminal ekranını temizler."""
    os.system('cls' if os.name == 'nt' else 'clear')

def follow(thefile):
    """Dosyanın sonundan itibaren yeni eklenen satırları canlı olarak takip eder."""
    thefile.seek(0, 2)
    while True:
        line = thefile.readline()
        if not line:
            time.sleep(0.1)
            continue
        yield line.strip()

# --- ANA PROGRAM ---
print("MSI Afterburner Canli ve Anlamli Log Okuyucu Baslatildi.")
print(f"Izlenen dosya: {LOG_FILE_PATH}")
time.sleep(2)

try:
    with open(LOG_FILE_PATH, 'r') as logfile:
        # Başlık satırını bulup, sensör isimlerini bir listeye alalım
        lines = [line.strip() for line in logfile.readlines() if line.strip()]
        if len(lines) < 3:
            print("HATA: Log dosyasi yeterli veri icermiyor.")
            exit()
        
        header_line = lines[2]
        headers = [h.strip().replace('"', '') for h in header_line.split(',')][2:]
        print(f"Algilanan Sensorler: {headers}")
        
        # Dosyayı canlı olarak takip etmeye başla
        log_lines = follow(logfile)
        
        for line in log_lines:
            clear_screen()
            print(f"--- {time.strftime('%H:%M:%S')} itibariyle Canli Veriler ---")
            
            values = [v.strip() for v in line.split(',')][2:]
            
            if len(headers) == len(values):
                # Her bir sensör ve değerini ekrana yazdır
                for header, value in zip(headers, values):
                    try:
                        display_value = f"{float(value):.1f}"
                    except (ValueError, TypeError):
                        display_value = value
                    
                    print(f"{header:<25}: {display_value}") # Sola yaslı ve hizalı format
            else:
                print("Veri hatasi: Baslik ve sutun sayisi eslesmiyor.")

            time.sleep(UPDATE_INTERVAL)

except FileNotFoundError:
    print(f"HATA: Log dosyasi bulunamadi! -> {LOG_FILE_PATH}")
except KeyboardInterrupt:
    print("\n\nProgram sonlandırıldı.")
except Exception as e:
    print(f"\nBeklenmedik bir hata olustu: {e}")