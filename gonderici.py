import serial
import time
import os
import json

# --- AYARLAR ---
COM_PORT = 'COM3'  # ESP32'nin bağlı olduğu COM portu (Kendine göre değiştir)
BAUD_RATE = 115200
UPDATE_INTERVAL = 1

# --- OTOMATİK DOSYA YOLU BULMA ---
try:
    program_files_x86 = os.environ['ProgramFiles(x86)']
    LOG_FILE_PATH = os.path.join(program_files_x86, "MSI Afterburner", "HardwareMonitoring.hml")
except KeyError:
    LOG_FILE_PATH = r"C:\Program Files (x86)\MSI Afterburner\HardwareMonitoring.hml"

# --- FİLTRE & KISALTMALAR ---
# ESP32'ye göndereceğimiz veriyi ve kısa etiketlerini tanımlayalım
TARGET_SENSORS = {
    "GPU temperature": "GPUT", "GPU usage": "GPUU", "Core clock": "GPUC", "Power": "GPUP", 
    "Fan speed": "FAN", "Fan tachometer": "FANS", "CPU temperature": "CPUT", 
    "CPU usage": "CPUU", "CPU clock": "CPUC", "CPU power": "CPUP", 
    "RAM usage": "RAM", "Framerate": "FPS", "Frametime": "FT"
}

def follow(thefile):
    thefile.seek(0, 2)
    while True:
        line = thefile.readline()
        if not line:
            time.sleep(0.1)
            continue
        yield line.strip()

# --- ANA PROGRAM ---
print("MSI Afterburner Veri Gonderici Baslatildi.")

# Seri portu başlat
try:
    ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=1)
    print(f"ESP32 baglantisi kuruldu: {COM_PORT}")
    time.sleep(2)
except serial.SerialException as e:
    print(f"HATA: {COM_PORT} portu acilamadi.")
    exit()

try:
    with open(LOG_FILE_PATH, 'r') as logfile:
        lines = [line.strip() for line in logfile.readlines() if line.strip()]
        header_line = lines[2]
        headers = [h.strip().replace('"', '') for h in header_line.split(',')][2:]
        
        log_lines = follow(logfile)
        
        for line in log_lines:
            values = [v.strip() for v in line.split(',')][2:]
            
            if len(headers) == len(values):
                data_to_send = {}
                # Verileri ayıkla ve sözlüğe ekle
                for header, value in zip(headers, values):
                    if header in TARGET_SENSORS:
                        try:
                            # Değerleri sayısal formata çevir
                            numeric_value = float(value)
                            # Ondalık kısmı sadece frametime için koru, diğerlerini tam sayı yap
                            if header == "Frametime" or header == "CPU power" or header == "Power":
                                data_to_send[TARGET_SENSORS[header]] = round(numeric_value, 1)
                            else:
                                data_to_send[TARGET_SENSORS[header]] = int(numeric_value)
                        except (ValueError, TypeError):
                            pass # Sayısal olmayanları (N/A) atla
                
                # Sözlüğü JSON string'ine çevir ve gönder
                json_data = json.dumps(data_to_send)
                print(f"\rGonderiliyor: {json_data}", end="")
                ser.write((json_data + '\n').encode('utf-8'))
            
            time.sleep(UPDATE_INTERVAL)

except FileNotFoundError:
    print(f"HATA: Log dosyasi bulunamadi!")
except KeyboardInterrupt:
    print("\nProgram sonlandırıldı.")
finally:
    if 'ser' in locals() and ser.is_open:
        ser.close()
        print("\nSeri port kapatildi.")