import window

from tkinter import *
import tkinter.messagebox as mb

import grpc
import gen.rws_client_pb2
import gen.rws_client_pb2_grpc

import remote

grpc_server_host = "localhost:50051"
stub = {}

default_font = "Arial 15"
program_name = "WebDesktop"

main_window = window.Window(300, 300, program_name, (False, False), "logo.png")

logo = PhotoImage(file="logo.png")
l_logo = Label(main_window.root, image=logo)
l_logo.pack()

ip_label = Label(main_window.root, text="Введите IP:", font=default_font)
ip_label.pack()

ip_entry = Entry(main_window.root)
ip_entry.pack()

login_label = Label(main_window.root, text="Введите логин:", font=default_font)
login_label.pack()

login_entry = Entry(main_window.root)
login_entry.pack()

password_label = Label(main_window.root, text="Введите пароль:", font=default_font)
password_label.pack()

password_entry = Entry(main_window.root, show="*")
password_entry.pack()

def login_button_click():

    try:

        with grpc.insecure_channel(ip_entry.get()) as channel:
            stub = gen.rws_client_pb2_grpc.RWS_serverStub(channel)

            login_request = gen.rws_client_pb2.LoginRequest(login = login_entry.get(), password = password_entry.get())
            login_response = stub.Login(login_request)

            if(login_response.token == ""):
                mb.showerror(program_name, "Неверный логин/пароль!")
            else:
                remote.run(main_window, stub, login_response)
    except Exception as e:
        mb.showerror(program_name, f"Произошла неизвестная ошибка: {e}")

login_button = Button(main_window.root, text="Войти", command=login_button_click, font=default_font)
login_button.pack()

main_window.run()