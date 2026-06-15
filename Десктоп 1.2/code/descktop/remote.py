import os
import json
import shutil
import platform
import io

from threading import Thread

from tkinter import *

from window import Window

chunk_size = 512 # Количество байт, передаваемых за раз

import grpc
import gen.rws_client_pb2
import gen.rws_client_pb2_grpc

import pyautogui as pg

kill_threads = False

JS_TO_PYAUTOGUI = {
    "Control": "ctrl",
    "Shift": "shift",
    "Alt": "alt",
    "Meta": "win",
    "Enter": "enter",
    "Backspace": "backspace",
    "ArrowUp": "up",
    "ArrowDown": "down",
    "ArrowLeft": "left",
    "ArrowRight": "right",
    "Tab": "tab",
    "Escape": "escape",
    "Delete": "delete"
}

def get_dir(LoginResponse, dir):
    try:
        for filename in os.listdir(dir):
            is_dir = ""
            if platform.system() == "Windows":
                is_dir = "folder" if os.path.isdir(dir + "\\" + filename) else "file"
            else:
                is_dir = "folder" if os.path.isdir(dir + "/" + filename) else "file"
            dir_request = gen.rws_client_pb2.DirRequest(token = LoginResponse.token, file_name = filename, is_dir = is_dir)
            yield dir_request
    except Exception as e:
        print(f"GRPC error: {e}")
        return

def get_disks(LoginResponse):
    if platform.system() == "Windows":
        for drive in os.listdrives():
            disk_request = gen.rws_client_pb2.DiskRequest(token = LoginResponse.token, disk_name = drive)
            yield disk_request
    else:
        disk_request = gen.rws_client_pb2.DiskRequest(token = LoginResponse.token, disk_name = "/")
        yield disk_request

def download_file(LoginResponse, file):

    try:

        with open(file, 'rb') as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break

                fileChunk = gen.rws_client_pb2.FileChunk(file_token = LoginResponse.token, content = chunk)
                yield fileChunk

        return
    except Exception as e:
        print(f"GRPC error: {e}")
        return
    
def get_monitor_size(LoginResponse):
    screenWidth, screenHeight = pg.size()
    monitor_request = gen.rws_client_pb2.MonitorRequest(token = LoginResponse.token, width = screenWidth, height = screenHeight)
    return monitor_request

def get_screen(LoginResponse):
    frame = pg.screenshot()
    buffer = io.BytesIO()
    frame.save(buffer, format="JPEG", quality=60)
    jpeg_bytes = buffer.getvalue()

    screen_request = gen.rws_client_pb2.ScreenRequest(
        token=LoginResponse.token, 
        frame=jpeg_bytes
    )
    
    return screen_request

def get_pyautogui_key(js_key):
    if js_key in JS_TO_PYAUTOGUI:
        return JS_TO_PYAUTOGUI[js_key]
    return js_key.lower() if len(js_key) == 1 else None


def executeCommands(stub, LoginResponse):
    try:
        while True:
            if kill_threads == True:
                break
            commandResponses = stub.WaitCommand(LoginResponse)
            for commandResponse in commandResponses:
                if(commandResponse.command == 0): # Вернуть содержимое папки
                    command_status = stub.SendDir(get_dir(LoginResponse, commandResponse.args))
                    if command_status.status == 1:
                        return
                elif(commandResponse.command == 1): # Вернуть все диски
                    command_status = stub.SendDisks(get_disks(LoginResponse))
                    if command_status.status == 1:
                        return
                elif(commandResponse.command == 2): # Скачать файл клиента
                    upload_status = stub.UploadFile(download_file(LoginResponse, commandResponse.args))
                    if upload_status.success == False:
                        return
                elif(commandResponse.command == 3): # Отправить файл клиенту

                    download_request = gen.rws_client_pb2.DownloadRequest(token = LoginResponse.token, path = commandResponse.args)

                    file_chunks = stub.DownloadFile(download_request)
                    with open(commandResponse.args, 'wb') as f:
                        for file_chunk in file_chunks:
                            f.write(file_chunk.content)
                elif(commandResponse.command == 4): # Удалить файл
                    os.remove(commandResponse.args)
                elif(commandResponse.command == 5): # Переименовать файл
                    args = json.loads(commandResponse.args)
                    os.rename(args["file"], args["new_name"])
                elif(commandResponse.command == 6): # Копировать файл
                    args = json.loads(commandResponse.args)
                    shutil.copy(args["file"], args["copy_path"])
                elif(commandResponse.command == 7): # Переместить файл
                    args = json.loads(commandResponse.args)
                    shutil.move(args["file"], args["copy_path"])
                elif(commandResponse.command == 8): # Создать папку
                    os.mkdir(commandResponse.args)
                elif(commandResponse.command == 10): # Вернуть разрешение монитора
                    command_status = stub.SendMonitorSize(get_monitor_size(LoginResponse))
                    if command_status.status == 1:
                        return
                elif(commandResponse.command == 12): # Передвинуть мышку
                    args = json.loads(commandResponse.args)
                    pg.moveTo(args["x"], args["y"])
                elif(commandResponse.command == 13): # Клик мышкой
                    args = json.loads(commandResponse.args)
                    pg.click(args["x"], args["y"], button=args["button"])
                elif(commandResponse.command == 14): # Клик мышкой дважды
                    args = json.loads(commandResponse.args)
                    pg.doubleClick(args["x"], args["y"])
                elif(commandResponse.command == 16): # Нажатие кнопок
                    args = json.loads(commandResponse.args)

                    key = get_pyautogui_key(args["key"])
                    if key:
                        try:
                            pg.keyDown(key)
                        except Exception:
                            pass
                elif(commandResponse.command == 17): # Отпускание кнопок
                    args = json.loads(commandResponse.args)

                    key = get_pyautogui_key(args["key"])
                    if key:
                        try:
                            pg.keyUp(key)
                        except Exception:
                            pass
                elif(commandResponse.command == 20): # Вернуть текущий кадр
                    command_status = stub.SendScreen(get_screen(LoginResponse))
                    if command_status.status == 1:
                        return
    except Exception as e:
        print(f"GRPC error: {e}")
        return

def run(main_window: Window, stub, LoginResponse):

    global kill_threads

    remote_window = main_window.createChild(300, 300, "WebDesktop", (False, False), "logo.png").root
    
    l = Label(remote_window, text="Соединение установлено. Теперь администраторы имеют доступ к Вашей файловой системе. Для отзыва доступа, закройте это окно.", font="Arial 15", wraplength=300)
    l.pack()

    command_thread = Thread(target=executeCommands, args=(stub, LoginResponse), daemon=True)
    command_thread.start()

    remote_window.wait_window()
    kill_threads = True