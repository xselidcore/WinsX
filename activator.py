"""
Модуль для активации Windows
"""

import os
import time
import subprocess
from config import KMS_SERVER
from ui import Colors, print_step, print_success, print_error, print_info
from utils import start_spinner, stop_spinner


def run_command(command, silent=True, timeout=30):
    """
    Выполнение команды в системе
    
    Args:
        command: Команда для выполнения
        silent: Скрывать ли вывод команды
        timeout: Таймаут выполнения в секундах (None = без таймаута)
        
    Returns:
        bool: True если команда выполнена успешно
    """
    try:
        if silent:
            result = subprocess.run(
                command,
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=timeout
            )
        else:
            result = subprocess.run(command, shell=True, timeout=timeout)
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        # Для команды активации таймаут не всегда означает ошибку
        if "ato" in command.lower():
            return None  # Специальное значение - нужно проверить статус
        print_error("Команда выполняется слишком долго")
        return False
    except Exception as e:
        print_error(f"Ошибка при выполнении команды: {str(e)}")
        return False


def install_product_key(product_key):
    """
    Установка ключа продукта
    
    Args:
        product_key: Ключ продукта для установки
        
    Returns:
        bool: True если ключ установлен успешно
    """
    print_step(1, 3, "Установка ключа продукта")
    spinner_thread = start_spinner("Установка ключа")
    
    success = run_command(f"slmgr /ipk {product_key}")
    
    stop_spinner()
    spinner_thread.join(timeout=0.5)
    
    if success:
        print_success("Ключ установлен успешно!")
        return True
    else:
        print_error("Не удалось установить ключ продукта")
        return False


def set_kms_server(server=KMS_SERVER):
    """
    Установка KMS сервера
    
    Args:
        server: Адрес KMS сервера
        
    Returns:
        bool: True если сервер установлен успешно
    """
    print_step(2, 3, "Подключение к KMS-серверу...")
    spinner_thread = start_spinner("Подключение")
    
    success = run_command(f"slmgr /skms {server}")
    
    stop_spinner()
    spinner_thread.join(timeout=0.5)
    
    if success:
        print_success("Сервер подключен!")
        return True
    else:
        print_error("Не удалось подключиться к KMS серверу")
        return False


def check_activation_status():
    """
    Проверка статуса активации Windows через slmgr /dli
    
    Returns:
        bool: True если Windows активирована
    """
    try:
        result = subprocess.run(
            "slmgr /dli",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10
        )
        output = result.stdout.lower() + result.stderr.lower()
        # Проверяем наличие индикаторов успешной активации
        activated_indicators = [
            "license status: licensed",
            "состояние лицензии: лицензировано",
            "license status: ---licensed---",
            "активация выполнена успешно"
        ]
        return any(indicator in output for indicator in activated_indicators)
    except:
        return False


def activate_windows():
    """
    Активация Windows
    
    Returns:
        bool: True если активация прошла успешно
    """
    print_step(3, 3, "Активация Windows...")
    spinner_thread = start_spinner("Активация")
    
    # Команда активации может выполняться долго и показывать диалог
    # Увеличиваем таймаут до 120 секунд
    success = run_command("slmgr /ato", timeout=120)
    
    stop_spinner()
    spinner_thread.join(timeout=0.5)
    
    # Если команда вернула None (таймаут), проверяем реальный статус
    if success is None:
        print_info("Проверка статуса активации...")
        time.sleep(2)  # Небольшая задержка для завершения процесса
        if check_activation_status():
            print_success("Windows активирована!")
            return True
        else:
            print_error("Не удалось активировать Windows")
            return False
    elif success:
        print_success("Windows активирована!")
        return True
    else:
        # Даже если команда вернула ошибку, проверим статус
        print_info("Проверка статуса активации...")
        time.sleep(2)
        if check_activation_status():
            print_success("Windows активирована!")
            return True
        print_error("Не удалось активировать Windows")
        return False


def check_license():
    """Проверка статуса лицензии"""
    print_info("\n🪪 Проверка лицензии через slmgr /xpr:")
    run_command("slmgr /xpr", silent=False)


def activate(edition_name, product_key):
    """
    Полный процесс активации Windows
    
    Args:
        edition_name: Название редакции
        product_key: Ключ продукта
        
    Returns:
        bool: True если активация прошла успешно
    """
    if not install_product_key(product_key):
        return False
    
    if not set_kms_server():
        return False
    
    if not activate_windows():
        return False
    
    print_success(f"Windows {edition_name} активирована!")
    return True

