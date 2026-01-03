"""
Утилиты и вспомогательные функции
"""

import sys
import time
import threading
import ctypes
from ui import Colors

# Глобальная переменная для управления спиннером
_stop_spinner = False


def is_admin():
    """Проверка, запущена ли программа от имени администратора"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def spinner(msg="⏳ Подождите"):
    """
    Анимация спиннера в консоли
    
    Args:
        msg: Сообщение для отображения
    """
    global _stop_spinner
    symbols = ['|', '/', '-', '\\']
    idx = 0
    while not _stop_spinner:
        sys.stdout.write(f"\r{Colors.CYAN}{msg}... {symbols[idx % len(symbols)]}{Colors.RESET}")
        sys.stdout.flush()
        idx += 1
        time.sleep(0.1)


def start_spinner(msg="⏳ Подождите"):
    """
    Запуск спиннера в отдельном потоке
    
    Args:
        msg: Сообщение для отображения
        
    Returns:
        threading.Thread: Поток со спиннером
    """
    global _stop_spinner
    _stop_spinner = False
    spinner_thread = threading.Thread(target=spinner, args=(msg,), daemon=True)
    spinner_thread.start()
    return spinner_thread


def stop_spinner():
    """Остановка спиннера"""
    global _stop_spinner
    _stop_spinner = True
    time.sleep(0.15)  # Небольшая задержка для завершения анимации

