import pyautogui
import time
import random
import logging
import subprocess
from logging.handlers import RotatingFileHandler
import os

def setup_logging():
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    log_file = os.path.join("logs", "execucao.log")
    handlers = [
        RotatingFileHandler(
            log_file,
            maxBytes=5*1024*1024,  # 5 MB
            backupCount=3,
            encoding="utf-8"
        ),
        logging.StreamHandler()
    ]
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=handlers
    )

def mover_mouse():
    t = 0
    while t<10:
        x = random.randint(200, 1600)
        y = random.randint(150, 950)
        pyautogui.moveTo(x, y, duration=0.5)
        time.sleep(1)
        t+=1
    logging.info("Movimentação do mouse concluída.")

def enviar_mensagem(numero):
    try:
        # Abre o WhatsApp Desktop usando Win + pesquisar
        pyautogui.hotkey('win')
        time.sleep(1)
        pyautogui.write('WhatsApp')
        time.sleep(1)
        pyautogui.press('enter')
        time.sleep(2)
        mover_mouse()
        time.sleep(10)  # Tempo para o app carregar
        # Atalho para nova conversa (Ctrl + N)
        pyautogui.hotkey('ctrl', 'n')
        time.sleep(2)
        # Digita o número e pressiona Enter
        pyautogui.write(numero)
        time.sleep(2)
        pyautogui.press('tab')
        time.sleep(2)
        pyautogui.press('tab')
        time.sleep(2)
        pyautogui.press('enter')
        time.sleep(2)
        mover_mouse()
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(1)
        pyautogui.press('enter')
        logging.info("Mensagem enviada com sucesso!")
        time.sleep(2)
        mover_mouse()
        pyautogui.hotkey('alt', 'F4')  # Fecha a conversa
        logging.info("Conversa fechada com sucesso!")
        logging.info(" ")
    except Exception as e:
        logging.error(f"Erro ao enviar mensagem: {e}")
