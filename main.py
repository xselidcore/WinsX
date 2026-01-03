"""
Главный модуль WinsX - точка входа в программу
"""

import sys
from config import WINDOWS_EDITIONS
from ui import (
    init_console, print_header, print_menu, 
    print_error, print_warning, get_user_choice, 
    print_footer, wait_for_exit
)
from utils import is_admin
from activator import activate, check_license


def main():
    """Главная функция программы"""
    # Инициализация консоли
    init_console()
    
    # Проверка прав администратора
    if not is_admin():
        print_warning("⚠️  Программа требует прав администратора!")
        print_warning("Запустите программу от имени администратора.")
        wait_for_exit()
        sys.exit(1)
    
    # Вывод заголовка
    print_header()
    
    # Вывод меню
    print_menu(WINDOWS_EDITIONS)
    
    # Получение выбора пользователя
    choice = get_user_choice()
    
    # Проверка корректности выбора
    if choice not in WINDOWS_EDITIONS:
        print_error("Неверный выбор. Программа завершает работу...")
        wait_for_exit()
        sys.exit(1)
    
    # Получение данных о выбранной редакции
    edition_name, product_key = WINDOWS_EDITIONS[choice]
    
    # Процесс активации
    success = activate(edition_name, product_key)
    
    if success:
        # Проверка лицензии
        check_license()
        
        # Финальное сообщение
        print_footer()
    else:
        print_error("Произошла ошибка при активации. Проверьте права администратора и подключение к интернету.")
    
    # Ожидание перед выходом
    wait_for_exit()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nПрограмма прервана пользователем.")
        sys.exit(0)
    except Exception as e:
        print_error(f"Критическая ошибка: {str(e)}")
        wait_for_exit()
        sys.exit(1)

