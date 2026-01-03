"""
Модуль для работы с пользовательским интерфейсом
"""

import sys
import os
from config import APP_NAME, APP_AUTHOR

# ANSI цвета для консоли
class Colors:
    GREEN = "\033[92m"
    CYAN = "\033[96m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


def init_console():
    """Инициализация консоли для корректной работы с кириллицей"""
    os.system("chcp 1251 >nul")


def print_header():
    """Вывод заголовка программы"""
    print(f"{Colors.GREEN}\n{Colors.BOLD}{APP_NAME}")
    print(f"   {APP_AUTHOR} 😎\n{Colors.RESET}")


def print_menu(editions):
    """Вывод меню выбора редакции"""
    print("Выбери редакцию Windows 10/11 для активации:\n")
    for key, (name, _) in editions.items():
        print(f"  {key}. {name}")


def print_step(step_num, total_steps, message):
    """Вывод информации о текущем шаге"""
    print(f"\n{Colors.CYAN}[{step_num}/{total_steps}] {message}{Colors.RESET}")


def print_success(message):
    """Вывод сообщения об успехе"""
    print(f"\r{Colors.GREEN}✅ {message}{Colors.RESET}")


def print_error(message):
    """Вывод сообщения об ошибке"""
    print(f"{Colors.RED}❌ {message}{Colors.RESET}")


def print_warning(message):
    """Вывод предупреждения"""
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.RESET}")


def print_info(message):
    """Вывод информационного сообщения"""
    print(f"{Colors.CYAN}{message}{Colors.RESET}")


def print_footer():
    """Вывод финального сообщения"""
    print(f"\n{Colors.GREEN}Спасибо за использование!")
    print(f"  {APP_AUTHOR} \n{Colors.RESET}")


def get_user_choice():
    """Получение выбора пользователя"""
    return input("\n>>> Введи номер редакции: ").strip()


def wait_for_exit():
    """Ожидание перед выходом"""
    import time
    time.sleep(2)
    os.system("pause")

