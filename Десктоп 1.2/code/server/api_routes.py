import os
from bottle import Bottle, route, request, response
import json
import jwt
import datetime
import gevent
import time
from gevent import monkey; monkey.patch_all()

api_routes = Bottle()

import database

command_stack = []
command_response_stack = []

jwt_secret = "30n6C0bTPi53s-8JrkkoGAHuhipbMh_e"
jwt_token_weeks_limit = 1

chunk_size = 512

@api_routes.route('/api/get_workers', method='POST')
def get_workers():
    current_user = database.db.check_jwt_token(request.cookies.get('jwt'))
    if not current_user:
        return

    try:

        company = database.db.get_company_by_owner_id(current_user["id"])
        if not company:
            return

        workers = database.db.get_workers_by_company(company["id"])
        return json.dumps({'workers': workers})
    except Exception as e:
        return {'status': '', 'error': str(e)}
    
@api_routes.route('/api/get_materials', method='POST')
def get_materials():
    current_user = database.db.check_jwt_token(request.cookies.get('jwt'))
    if not current_user:
        return

    try:

        company = database.db.get_company_by_owner_id(current_user["id"])
        if not company:
            return

        materials = database.db.get_materials_by_company(company["id"])
        return json.dumps({'materials': materials})
    except Exception as e:
        return {'status': '', 'error': str(e)}
    
@api_routes.route('/api/get_orders', method='POST')
def get_orders():
    current_user = database.db.check_jwt_token(request.cookies.get('jwt'))
    if not current_user:
        return

    try:

        company = database.db.get_company_by_owner_id(current_user["id"])
        if not company:
            return

        orders = database.db.get_orders_by_company(company["id"])

        for order in orders:
            item = database.db.get_item_by_name(order["item"], company["id"])

            if item:
                order["price"] = item["unit_price"] * 1.20
                order["sum"] = item["unit_price"] * 1.20 * order["count"]
            else:
                continue

        return json.dumps({'orders': orders})
    except Exception as e:
        return {'status': '', 'error': str(e)}
    
@api_routes.route('/api/get_items', method='POST')
def get_items():
    current_user = database.db.check_jwt_token(request.cookies.get('jwt'))
    if not current_user:
        return

    try:

        company = database.db.get_company_by_owner_id(current_user["id"])
        if not company:
            return

        items = database.db.get_items_by_company(company["id"])
        return json.dumps({'items': items})
    except Exception as e:
        return {'status': '', 'error': str(e)}

@api_routes.route('/api/execute_command', method='POST')
def execute_command():

    global command_response_stack

    data = request.json
    user_id = data.get('user_id')
    command = data.get('command')
    args = data.get('args')

    current_user = database.db.check_jwt_token(request.cookies.get('jwt'))
    if not current_user:
        return

    try:

        company = database.db.get_company_by_owner_id(current_user["id"])
        if not company:
            return

        worker = database.db.get_user_by_id(user_id)
        if not worker:
            return

        this_command_stack = get_command_stack()

        if(worker["company_id"] == company["id"]):

            if(command == 2): # Скачать файл
                payload = {"employee_id": worker["id"], "file": args, "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(weeks=jwt_token_weeks_limit)}
                return json.dumps({'status': 'ok', 'token': jwt.encode(payload, jwt_secret, algorithm="HS256")})

            this_command_stack.append({"id": user_id, "command": command, "args": args})

        if(command >= 4 and command <= 8):
            return json.dumps({'status': 'ok'}) # Команда на удаление, переименование, копирование и перемещение файла, создание папки

        start = time.time()
        while True:
            if time.time() - start > 10:
                return json.dumps({'status': '', 'error': 'Не удалось получить ответ от пользователя'})
            for stack_command in command_response_stack:
                current_user = database.db.check_jwt_token(stack_command["token"])
                if not current_user:
                    return

                if int(current_user["id"]) == int(user_id): # И то, что это именно текущая команда
                    if stack_command["command"] == 0:
                        files = stack_command["files"]
                        command_response_stack.remove(stack_command)
                        return json.dumps({'status': 'ok', 'files': files})
                    elif stack_command["command"] == 1:
                        disks = stack_command["disks"]
                        command_response_stack.remove(stack_command)
                        return json.dumps({'status': 'ok', 'disks': disks})
                    elif stack_command["command"] == 10:
                        width = stack_command["width"]
                        height = stack_command["height"]
                        command_response_stack.remove(stack_command)
                        return json.dumps({'status': 'ok', 'width': width, 'height': height})
            gevent.sleep(0)
                    
    except Exception as e:
        return {'status': '', 'error': str(e)}

# Скачивание файлов
@api_routes.route('/download/<token>')
def download_files(token):

    global command_response_stack

    current_user = database.db.check_jwt_token(request.cookies.get('jwt'))
    if not current_user:
        return

    try:

        decoded = jwt.decode(token, jwt_secret, algorithms=["HS256"])

        response.set_header('Content-Disposition', f'attachment; filename="{decoded["file"].split("\\")[-1]}"')

        company = database.db.get_company_by_owner_id(current_user["id"])
        if not company:
            return

        worker = database.db.get_user_by_id(decoded["employee_id"])
        if not worker:
            return

        this_command_stack = get_command_stack()

        if(worker["company_id"] == company["id"]):

            this_command_stack.append({"id": decoded["employee_id"], "command": 2, "args": decoded["file"]}) # Даём команду скачать файл
            
            current_flle_step = 0

            start = time.time()
            while True:
                if time.time() - start > 10:
                    return
                for stack_command in command_response_stack:
                    current_user = database.db.check_jwt_token(stack_command["token"])
                    if not current_user:
                        return
                    
                    if stack_command["command"] == 2:
                        if stack_command["step"] == current_flle_step:
                            if stack_command["end"] == True:
                                command_response_stack.remove(stack_command)
                                return
                            content = stack_command["content"]
                            command_response_stack.remove(stack_command)
                            current_flle_step = current_flle_step + 1
                            yield content
                gevent.sleep(0)
                    
    except Exception as e:
        return {'status': '', 'error': str(e)}
    except jwt.ExpiredSignatureError:
            print("Срок действия токена истёк")
            return None
    except jwt.InvalidSignatureError:
        print("Недействительная подпись токена")
        return None
    except jwt.InvalidTokenError:
        print("Недействительный токен")
        return None

@api_routes.route('/upload_file', method=['POST'])
def upload_file():

    global command_response_stack

    current_user = database.db.check_jwt_token(request.cookies.get('jwt'))
    if not current_user:
        return

    try:

        folder   = request.forms.folder
        employee   = request.forms.employee
        upload     = request.files.get('file')

        company = database.db.get_company_by_owner_id(current_user["id"])
        if not company:
            return

        worker = database.db.get_user_by_id(employee)
        if not worker:
            return
        
        this_command_stack = get_command_stack()

        file_step = 1

        this_command_stack.append({"id": employee, "command": 3, "args": f'{folder}\\{upload.filename}'}) # Отправляем файл

        while True:
            chunk = upload.file.read(chunk_size)
            if not chunk:
                break

            this_command_stack.append({"id": employee, "command": 3, "args": {"folder": folder, "filename": upload.filename, "chunk": chunk, "step": file_step, "end": False}}) # Отправляем файл
            file_step += 1

        this_command_stack.append({"id": employee, "command": 3, "args": {"folder": folder, "filename": upload.filename, "chunk": "", "step": file_step, "end": True}}) # Отправляем файл
        return {'status': 'ok'}
    except Exception as e:
        print("Error in api_routes: ", str(e))
        return {'status': '', 'error': str(e)}

def get_command_stack():
    global command_stack
    return command_stack

def init_api_routes(func_command_stack, func_command_response_stack):
    global command_stack
    global command_response_stack

    command_stack = func_command_stack
    command_response_stack = func_command_response_stack