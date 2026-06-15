#!/usr/bin/env python
# -*- coding: utf-8 -*-
import gevent
from gevent import monkey; monkey.patch_all()
from bottle import run, Bottle

app = Bottle()

import database
import api_routes
import routes
import grpc_server
import websocket

from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler

host = "localhost" # Хост, на котором будет работать сервер
server_port = 3000 # Порт, на котором будет работать сервер

command_stack = []
command_response_stack = []

def http_server_run(func_command_stack, func_command_response_stack):
    global command_stack
    global command_response_stack
    global host
    global server_port

    command_stack = func_command_stack
    command_response_stack = func_command_response_stack

    api_routes.init_api_routes(command_stack, command_response_stack)
    websocket.init_websocket_routes(command_stack, command_response_stack)

    app.merge(api_routes.api_routes)
    app.merge(routes.main_routes)
    app.merge(websocket.websocket_route)

    server = WSGIServer((host, server_port), app,
                    handler_class=WebSocketHandler)

    server.serve_forever()


# Server startup
if __name__ == '__main__':
    print("=" * 60)
    print("WEB DESKTOP SERVER")
    print("=" * 60)
    print("Server started on http://localhost:%d" %(server_port))
    print("\nMain Pages:")
    print("  • Main page:     http://localhost:%d" %(server_port))
    print("  • Login:         Click 'Login' button")
    print("  • Registration:  Click 'Registration' button")

    api_routes.init_api_routes(command_stack, command_response_stack)

    gevent.joinall([
        gevent.spawn(grpc_server.serve, command_stack, command_response_stack),
        gevent.spawn(http_server_run, command_stack, command_response_stack),
    ])