#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os
import sys
import subprocess
import time
import signal
import platform
from pathlib import Path


class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header():
    print(f"{Colors.HEADER}{Colors.BOLD}")
    print("========================================")
    print("      SecureVision - Запуск системи")
    print("========================================")
    print(f"{Colors.ENDC}\n")

def print_success(message):
    print(f"{Colors.OKGREEN}✅ {message}{Colors.ENDC}")

def print_error(message):
    print(f"{Colors.FAIL}❌ {message}{Colors.ENDC}")

def print_info(message):
    print(f"{Colors.OKCYAN}ℹ️  {message}{Colors.ENDC}")

def print_warning(message):
    print(f"{Colors.WARNING}⚠️  {message}{Colors.ENDC}")

def check_python():
    """Перевірка версії Python"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print_error(f"Потрібен Python 3.8+, знайдено {version.major}.{version.minor}")
        return False
    print_success(f"Python {version.major}.{version.minor}.{version.micro}")
    return True

def check_dependencies():
    """Перевірка та встановлення залежностей"""
    if not os.path.exists('requirements.txt'):
        print_error("Файл requirements.txt не знайдено!")
        return False
    
    print_info("Перевірка залежностей...")
    try:
        subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt', '--quiet'],
            check=True,
            capture_output=True
        )
        print_success("Залежності встановлено")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Помилка встановлення залежностей: {e}")
        return False

def create_logs_dir():
    """Створення папки для логів"""
    logs_dir = Path('logs')
    if not logs_dir.exists():
        logs_dir.mkdir()
        print_success("Створено папку logs/")

def run_applications():
    """Запуск обох додатків"""
    print(f"\n{Colors.HEADER}========================================")
    print("🚀 Запуск додатків...")
    print(f"========================================{Colors.ENDC}\n")
    
    # Список процесів для відстеження
    processes = []
    
    try:
        # Запуск Telegram бота
        print_info("Запуск Telegram бота...")
        bot_process = subprocess.Popen(
            [sys.executable, 'bot.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        processes.append(('Telegram Bot', bot_process))
        time.sleep(2)  # Даємо час на ініціалізацію
        
        if bot_process.poll() is None:
            print_success("Telegram бот запущено")
        else:
            print_error("Telegram бот не вдалось запустити")
            return
        
        # Запуск веб-додатку
        print_info("Запуск веб-додатку...")
        web_process = subprocess.Popen(
            [sys.executable, 'webapp.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        processes.append(('Web App', web_process))
        time.sleep(2)  # Даємо час на ініціалізацію
        
        if web_process.poll() is None:
            print_success("Веб-додаток запущено")
        else:
            print_error("Веб-додаток не вдалось запустити")
            bot_process.terminate()
            return
        
        print(f"\n{Colors.OKGREEN}{Colors.BOLD}✅ Система успішно запущена!{Colors.ENDC}\n")
        print(f"{Colors.OKCYAN}📱 Telegram бот: працює{Colors.ENDC}")
        print(f"{Colors.OKCYAN}🌐 Веб-додаток: http://localhost:5001{Colors.ENDC}")
        print(f"{Colors.OKCYAN}📋 Логи: logs/bot.log та logs/webapp.log{Colors.ENDC}\n")
        print(f"{Colors.WARNING}💡 Натисніть Ctrl+C для зупинки...{Colors.ENDC}\n")
        
        # Функція для обробки сигналу зупинки
        def signal_handler(sig, frame):
            print(f"\n\n{Colors.WARNING}🛑 Зупинка додатків...{Colors.ENDC}")
            for name, proc in processes:
                try:
                    proc.terminate()
                    proc.wait(timeout=5)
                    print_success(f"{name} зупинено")
                except:
                    proc.kill()
                    print_warning(f"{name} примусово завершено")
            print(f"\n{Colors.OKGREEN}👋 Додатки зупинено{Colors.ENDC}\n")
            sys.exit(0)
        
        # Встановлення обробника сигналу
        signal.signal(signal.SIGINT, signal_handler)
        if platform.system() != 'Windows':
            signal.signal(signal.SIGTERM, signal_handler)
        
        # Очікування завершення процесів
        while True:
            time.sleep(1)
            # Перевірка чи працюють процеси
            for name, proc in processes:
                if proc.poll() is not None:
                    print_error(f"{name} несподівано завершився!")
                    # Зупинка інших процесів
                    for n, p in processes:
                        if p != proc and p.poll() is None:
                            p.terminate()
                    return
    
    except Exception as e:
        print_error(f"Помилка при запуску: {e}")
        for name, proc in processes:
            if proc.poll() is None:
                proc.terminate()

def main():
    """Головна функція"""
    print_header()
    
    # Перевірка Python
    if not check_python():
        sys.exit(1)
    
    # Перевірка та встановлення залежностей
    if not check_dependencies():
        sys.exit(1)
    
    # Створення папки для логів
    create_logs_dir()
    
    # Запуск додатків
    run_applications()

if __name__ == '__main__':
    main()