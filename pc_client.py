# -*- coding: utf-8 -*-
import telebot
import os
import sys
import time
import getpass
import platform
import socket
import uuid
from threading import Thread

# ========== ТВОИ ДАННЫЕ ==========
BOT_TOKEN = '8689333512:AAE1XY-yWka5xvyN-IIgnH5cy47eB_ug5xU'
ADMIN_ID = 8527578981
# ================================

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
        try:
            import requests
            ext_ip = requests.get('https://api.ipify.org', timeout=3).text
        except:
            ext_ip = "Не определен"
            
        info = {
            'id': self.pc_id,
            'computer': self.pc_name,
            'user': self.user_name,
            'local_ip': socket.gethostbyname(socket.gethostname()),
            'external_ip': ext_ip,
            'os': platform.system() + ' ' + platform.release(),
            'last_seen': time.strftime('%H:%M %d.%m.%Y')
        }
        return info

pc = PCManager()
bot = telebot.TeleBot(BOT_TOKEN)

def send_startup_notification():
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
    except Exception as e:
        print(f"Ошибка отправки: {e}")

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
            bot.send_message(message.chat.id, "❌ Команда выключения работает только на Windows")

@bot.message_handler(func=lambda m: m.text == '🔄 Перезагрузить')
def restart(message):
    if message.chat.id == ADMIN_ID:
        bot.send_message(message.chat.id, "🔄 Перезагрузка через 10 секунд...")
        time.sleep(2)
        if platform.system() == "Windows":
            os.system("shutdown /r /t 10")
        else:
            bot.send_message(message.chat.id, "❌ Команда перезагрузки работает только на Windows")

def main():
    print("Бот запущен...")
    Thread(target=send_startup_notification).start()
    
    while True:
        try:
            bot.polling(non_stop=True, interval=0)
        except Exception as e:
            print(f"Ошибка: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
