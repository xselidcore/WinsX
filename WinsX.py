import os
import time
import threading
import sys

GREEN = "\033[92m"
CYAN = "\033[96m"
RED = "\033[91m"
RESET = "\033[0m"

os.system("chcp 1251 >nul")

print(f"{GREEN}\nWindows 10/11 Activator by xselid.ru")
editions = {
    "1":  ("Home", "TX9XD-98N7V-6WMQ6-BX7FG-H8Q99"),
    "2":  ("Home N", "3KHY7-WNT83-DGQKR-F7HPR-844BM"),
    "3":  ("Home Single Language", "7HNRX-D7KGG-3K4RQ-4WPJ4-YTDFH"),
    "4":  ("Home Country Specific", "PVMJN-6DFY6-9CCP6-7BKTT-D3WVR"),
    "5":  ("Pro", "W269N-WFGWX-YVC9B-4J6C9-T83GX"),
    "6":  ("Pro N", "MH37W-N47XK-V7XM9-C7227-GCQG9"),
    "7":  ("Pro Workstation", "DXG7C-N36C4-C4HTG-X4T3X-2YV77"),
    "8":  ("Pro N Workstation", "WYPNQ-8C467-V2W6J-TX4WX-WT2RQ"),
    "9":  ("Pro Education", "8PTT6-RNW4C-6V7J2-C2D3X-MHBPB"),
    "10": ("Pro Education N", "GJTYN-HDMQY-FRR76-HVGC7-QPF8P"),
    "11": ("Enterprise", "NPPR9-FWDCX-D2C8J-H872K-2YT43"),
    "12": ("Enterprise N", "DPH2V-TTNVB-4X9Q3-TJR4H-KHJW4"),
    "13": ("Enterprise 2015 LTSB", "WNMTR-4C88C-JK8YV-HQ7T2-76DF9"),
    "14": ("Enterprise 2015 LTSB N", "2F77B-TNFGY-69QQF-B8YKP-D69TJ"),
    "15": ("Enterprise 2016 LTSB", "DCPHK-NFMTC-H88MJ-PFHPY-QJ4BJ"),
    "16": ("Enterprise 2016 LTSB N", "QFFDN-GRT3P-VKWWX-X7T3R-8B639"),
    "17": ("Education", "NW6C2-QMPVW-D7KKK-3GKT6-VCFB2"),
    "18": ("Education N", "2WH4N-8QGBV-H22JP-CT43Q-MDWWJ"),
    "19": ("Starter", "D6RD9-D4N8T-RT9QX-YW6YT-FCWWJ"),
    "20": ("S", "3NF4D-GF9GY-63VKH-QRC3V-7QW8P"),
    "21": ("Enterprise G N", "FW7NV-4T673-HF4VX-9X4MM-B4H4T")
}

stop_spinner = False
def spinner(msg="⏳ Подождите"):
    symbols = ['|', '/', '-', '\\']
    idx = 0
    while not stop_spinner:
        sys.stdout.write(f"\r{CYAN}{msg}... {symbols[idx % len(symbols)]}{RESET}")
        sys.stdout.flush()
        idx += 1
        time.sleep(0.1)

print("Выбери редакцию Windows 10/11 для активации:\n")
for key, (name, _) in editions.items():
    print(f"  {key}. {name}")

choice = input("\n>>> Введи номер редакции: ").strip()
if choice not in editions:
    print(f"{RED}❌ Неверный выбор. Пока, xselid отключается...{RESET}")
    time.sleep(2)
    exit()

edition_name, product_key = editions[choice]

print(f"\n{CYAN}[1/3] Установка ключа для {edition_name}{RESET}")
spinner_thread = threading.Thread(target=spinner, args=("Установка ключа",))
spinner_thread.start()
os.system(f"slmgr /ipk {product_key} >nul 2>&1")
stop_spinner = True
spinner_thread.join()
print(f"\r{GREEN}✅ Ключ установлен успешно!{RESET}")

stop_spinner = False
print(f"\n{CYAN}[2/3] Подключение к KMS-серверу...{RESET}")
spinner_thread = threading.Thread(target=spinner, args=("Подключение",))
spinner_thread.start()
os.system("slmgr /skms kms.digiboy.ir >nul 2>&1")
stop_spinner = True
spinner_thread.join()
print(f"\r{GREEN}✅ Сервер подключен!{RESET}")

stop_spinner = False
print(f"\n{CYAN}[3/3] Активация Windows...{RESET}")
spinner_thread = threading.Thread(target=spinner, args=("Активация",))
spinner_thread.start()
os.system("slmgr /ato >nul 2>&1")
stop_spinner = True
spinner_thread.join()
print(f"\r{GREEN}✅ Windows {edition_name} активирована!{RESET}")

# Проверка
print(f"\n{CYAN}🪪 Проверка лицензии через slmgr /xpr:{RESET}")
os.system("slmgr /xpr")

# Финал
print(f"\n{GREEN}Спасибо за использование!")
time.sleep(2)
os.system("pause")
