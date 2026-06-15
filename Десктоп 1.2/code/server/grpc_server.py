from concurrent import futures

import gevent
import time
from gevent import monkey; monkey.patch_all()

import grpc
import gen.rws_client_pb2
import gen.rws_client_pb2_grpc

import database
import json

grpc_server_host = "localhost:50051"

command_stack = []
command_response_stack = []

class GRPC_Servicer(gen.rws_client_pb2_grpc.RWS_serverServicer):

    def Login(self, request, context):
        # Authentication
        jwt_token = database.db.authenticate_user(request.login, request.password)
        login_response = gen.rws_client_pb2.LoginResponse()

        if jwt_token:
            login_response.token = jwt_token
        else:
            login_response.token = ""

        return login_response
    def WaitCommand(self, request, context):

        global command_stack

        current_user = database.db.check_jwt_token(request.token)
        if not current_user:
            return
        
        start = time.time()
        while True:
            if time.time() - start > 10:
                return
            for command in command_stack:
                if int(command["id"]) == current_user["id"]:
                    if int(command["command"]) == 3 and command["args"]["step"] != 0:
                        continue

                    if (int(command["command"]) >= 5 and int(command["command"]) <= 7) or (int(command["command"] >= 12) and int(command["command"] <= 17)): # Команды копирования, перемещения и удаления файлов, а также передвижения и кликов мышкой
                        command_response = gen.rws_client_pb2.CommandResponse()
                        command_response.command = int(command["command"])
                        command_response.args = json.dumps(command["args"])
                        yield command_response
                        command_stack.remove(command)
                        return

                    try:
                        command_response = gen.rws_client_pb2.CommandResponse()
                        command_response.command = int(command["command"])
                        command_response.args = command["args"]
                        yield command_response
                        command_stack.remove(command)
                        return
                    except Exception as e:
                        print(f"GRPC error: {e}")
                        return None
            gevent.sleep(0)

    def SendDisks(self, request_iterator, context):

        global command_response_stack

        disks = []
        for request in request_iterator:

            try:

                current_user = database.db.check_jwt_token(request.token)
                if not current_user:
                    return

                disks.append(request.disk_name)
            except Exception as e:
                print(f"GRPC error: {e}")
                return

        command_response_stack.append({"command": 1, "token": request.token, "disks": disks})
        
        command_status = gen.rws_client_pb2.CommandStatus(status = 0) # Успех
        return command_status
    
    def SendDir(self, request_iterator, context):

        global command_response_stack
        files = []

        for request in request_iterator:

            try:

                current_user = database.db.check_jwt_token(request.token)
                if not current_user:
                    return

                files.append({"file_name": request.file_name, "is_dir": request.is_dir})
            except Exception as e:
                print(f"GRPC error: {e}")
                return
            
        try:
            command_response_stack.append({"command": 0, "token": request.token, "files": files})
            command_status = gen.rws_client_pb2.CommandStatus(status = 0) # Успех
            return command_status
        except Exception as e:
            print(f"GRPC error: {e}")
            return
        
    def UploadFile(self, request_iterator, context): #Скачать файл у клиента

        global command_response_stack

        file_step = 0

        for request in request_iterator:

            try:

                current_user = database.db.check_jwt_token(request.file_token)
                if not current_user:
                    return

                command_response_stack.append({"command": 2, "token": request.file_token, "content": request.content, "step": file_step, "end": False})
                file_step += 1
            except Exception as e:
                print(f"GRPC error: {e}")
                return
            
        try:
            command_response_stack.append({"command": 2, "token": request.file_token, "content": "", "step": file_step, "end": True})
            upload_status = gen.rws_client_pb2.UploadStatus(success = True, message="") # Успех
            return upload_status
        except Exception as e:
            print(f"GRPC error: {e}")

    def DownloadFile(self, request, context): # Отправить файл клиенту

        global command_stack

        current_user = database.db.check_jwt_token(request.token)
        if not current_user:
            return

        current_flle_step = 1

        start = time.time()
        while True:
            if time.time() - start > 10:
                return
            for stack_command in command_stack:
                if stack_command["command"] == 3 and int(stack_command["id"]) == int(current_user["id"]):
                    if int(stack_command["args"]["step"]) == int(current_flle_step):
                        if stack_command["args"]["end"] == True:
                            command_stack.remove(stack_command)
                            return
                        content = stack_command["args"]["chunk"]
                        command_stack.remove(stack_command)
                        current_flle_step = current_flle_step + 1

                        file_chunk = gen.rws_client_pb2.FileChunk(file_token = stack_command["args"]["filename"], content = content)
                        yield file_chunk
            gevent.sleep(0)

    def SendMonitorSize(self, request, context):

        global command_response_stack

        try:

            current_user = database.db.check_jwt_token(request.token)
            if not current_user:
                return
        except Exception as e:
            print(f"GRPC error: {e}")
            return

        command_response_stack.append({"command": 10, "token": request.token, "width": request.width, "height": request.height})
        
        command_status = gen.rws_client_pb2.CommandStatus(status = 0) # Успех
        return command_status
    
    def SendScreen(self, request, context):

        global command_response_stack

        try:

            current_user = database.db.check_jwt_token(request.token)
            if not current_user:
                return
        except Exception as e:
            print(f"GRPC error: {e}")
            return

        command_response_stack.append({"command": 20, "token": request.token, "frame": request.frame})
        
        command_status = gen.rws_client_pb2.CommandStatus(status = 0) # Успех
        return command_status
    
def serve(func_command_stack, func_command_response_stack):

    global command_stack
    global command_response_stack

    command_stack = func_command_stack
    command_response_stack = func_command_response_stack

    grpc._cython.cygrpc.init_grpc_gevent()

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    gen.rws_client_pb2_grpc.add_RWS_serverServicer_to_server(GRPC_Servicer(), server)
    server.add_insecure_port(grpc_server_host)

    print("GRPC Server started on %s" %(grpc_server_host))

    server.start()

    server.wait_for_termination()