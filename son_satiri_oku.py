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

def get_last_line(filepath):
    """Bir dosyayı açar, okur ve boş olmayan en son satırını döndürür."""
    try:
        with open(filepath, 'r') as f:
            lines = f.readlines()
            # Dosyanın sonundan başlayarak boş olmayan ilk satırı bul
            for line in reversed(lines):
                stripped_line = line.strip()
                if stripped_line:
                    return stripped_line
            return None # Dosya boş veya sadece boş satırlar içeriyor
    except FileNotFoundError:
        return "HATA: Dosya bulunamadi"
    except Exception as e:
        return f"HATA: {e}"

# --- ANA PROGRAM ---
print("MSI Afterburner Canli Son Satir Okuyucu Baslatildi.")
print(f"Izlenen dosya: {LOG_FILE_PATH}")
time.sleep(2)

try:
    while True:
        last_line = get_last_line(LOG_FILE_PATH)
        
        clear_screen()
        print(f"--- {time.strftime('%H:%M:%S')} itibariyle Canli Veri ---")
        
        if "HATA" in str(last_line):
            print(f"\n{last_line}")
        elif last_line is not None:
            print("\nGuncellenen Ham Veri Satiri:")
            print(last_line)
        else:
            print("\nLog dosyasi bos veya okunabilir veri yok...")
            
        time.sleep(UPDATE_INTERVAL)

except KeyboardInterrupt:
    print("\n\nProgram sonlandırıldı.")