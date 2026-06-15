from bottle import Bottle, route, request, response
from geventwebsocket import WebSocketError
import gevent
import time
import base64
from gevent import monkey; monkey.patch_all()

import json

import database

websocket_route = Bottle()

command_stack = []
command_response_stack = []

def init_websocket_routes(func_command_stack, func_command_response_stack):
    global command_stack
    global command_response_stack

    command_stack = func_command_stack
    command_response_stack = func_command_response_stack

def screenshot_handler(wsock, employee_id):
    
    global command_stack
    global command_response_stack

    last_screen = time.time()
    
    while True:
        if time.time() - last_screen < 0.032:
            continue

        command_stack.append({"id": employee_id, "command": 20, "args": ""}) # Запрашиваем скриншот

        start = time.time()

        answerSended = False

        while answerSended == False:
            if time.time() - start > 10:
                return
            for stack_command in command_response_stack:
                current_user = database.db.check_jwt_token(stack_command["token"])
                if not current_user:
                    return

                if int(current_user["id"]) == int(employee_id): # И то, что это именно текущая команда
                    if stack_command["command"] == 20:
                        frame = stack_command["frame"]
                        command_response_stack.remove(stack_command)

                        encoded = base64.b64encode(frame).decode('ascii')
                        wsock.send(json.dumps({"type": "screen", "frame": encoded}))
                        last_screen = time.time()
                        answerSended = True
                        break
            gevent.sleep(0)

@websocket_route.route('/remote')
def handle_websocket():

    screenshotHandler = None

    wsock = request.environ.get('wsgi.websocket')
    if not wsock:
        return
    
    current_user = database.db.check_jwt_token(request.cookies.get('jwt'))
    if not current_user:
        return

    try:

        company = database.db.get_company_by_owner_id(current_user["id"])
        if not company:
            return
        
        while True:
            try:
                message = wsock.receive()
                data = json.loads(message)

                if data["type"] == "worker_select":
                    worker = database.db.get_user_by_id(data["user_id"])
                    if not worker:
                        return

                    if(worker["company_id"] == company["id"]):
                        screenshotHandler = gevent.spawn(screenshot_handler, wsock, data["user_id"])

                elif data["type"] == "mouse_move":
                    worker = database.db.get_user_by_id(data["user_id"])
                    if not worker:
                        return
                    
                    if(worker["company_id"] == company["id"]):
                        command_stack.append({"id": data["user_id"], "command": 12, "args": {"x": data["x"], "y": data["y"]}}) # Двигаем мышку

                elif data["type"] == "mouse_click":
                    worker = database.db.get_user_by_id(data["user_id"])
                    if not worker:
                        return
                    
                    if(worker["company_id"] == company["id"]):
                        command_stack.append({"id": data["user_id"], "command": 13, "args": {"x": data["x"], "y": data["y"], "button": data["button"]}}) # Кликаем мышкой

                elif data["type"] == "dbl_mouse_click":
                    worker = database.db.get_user_by_id(data["user_id"])
                    if not worker:
                        return
                    
                    if(worker["company_id"] == company["id"]):
                        command_stack.append({"id": data["user_id"], "command": 14, "args": {"x": data["x"], "y": data["y"]}}) # Кликаем мышкой дважды

                elif data["type"] == "keydown":
                    worker = database.db.get_user_by_id(data["user_id"])
                    if not worker:
                        return
                    
                    if(worker["company_id"] == company["id"]):
                        command_stack.append({"id": data["user_id"], "command": 16, "args": {"key": data["key"]}}) # Нажимаем клавишу

                elif data["type"] == "keyup":
                    worker = database.db.get_user_by_id(data["user_id"])
                    if not worker:
                        return
                    
                    if(worker["company_id"] == company["id"]):
                        command_stack.append({"id": data["user_id"], "command": 17, "args": {"key": data["key"]}}) # Отпускаем клавишу

            except WebSocketError:
                print("Websocket error")
                break

    except Exception as e:
        print("Websocket exception: ", str(e))
        return {'status': '', 'error': str(e)}
    finally:
        if screenshotHandler != None:
            screenshotHandler.kill()