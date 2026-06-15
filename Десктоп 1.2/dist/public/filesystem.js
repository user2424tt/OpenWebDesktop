let current_employee = null;
let path_stack = [];
let current_folder = null;
let current_file = null;
let copy_file = null;
let copy_mode = null;

function GetWorkers() {

    document.getElementById("file_system_block").innerHTML = ``;

    fetch('/api/get_workers', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'}
    })
    .then(response => response.json())
    .then(data => {
        if(!data.error) {
            data.workers.forEach(worker => {
                
                document.getElementById("file_system_block").innerHTML += `
                <div class="worker_block" data-id="${worker['id']}">${worker['name']}</div>
                `;

            });

        } else {
            alert("Ошибка: " + data.error);
        }
    });
}

function GetDisksForEmployee(employee_id) {
    fetch('/api/execute_command', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            user_id: employee_id,
            command: 1, // Получить список дисков
            args: "" 
        })
    })
    .then(response => response.json())
    .then(data => {
        if(data.status) {
            document.getElementById("file_system_block").innerHTML = `
            <div onclick="GetWorkers()">Назад...</div>
            `;

            data.disks.forEach(disk => {
                
                document.getElementById("file_system_block").innerHTML += `
                <div class="file_block" data-type="folder" data-id="${disk}">${disk}</div>
                `;

            });

        } else {
            alert("Ошибка: " + data.error);
            console.error(data.error);
        }
    });
}

function GetFolder(folder) {

    current_folder = folder;

    fetch('/api/execute_command', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            user_id: current_employee,
            command: 0, // Получить содержемое папки
            args: `${folder}` 
        })
    })
    .then(response => response.json())
    .then(data => {
        if(data.status) {
            
            document.getElementById("file_system_block").innerHTML = `
            <div onclick="GetBackFolder()">Назад...</div>
            `;

            data.files.forEach(file => {
                
                document.getElementById("file_system_block").innerHTML += `
                <div class="file_block" data-type="${file["is_dir"]}" data-id="${current_folder}/${file["file_name"]}">${file["file_name"]}</div>
                `;

            });

        } else {
            alert("Ошибка: " + data.error);
            console.error(data.error);
        }
    });
}

function GetBackFolder() {
    if(path_stack.length > 0) {
        GetFolder(path_stack.pop());
    }
    else {
        GetDisksForEmployee(current_employee);
    }
}

function CloseContextMenu() {
    current_file = null;

    document.getElementById("context_menu").style.display = "none";
    document.getElementById("outer_context_menu").style.display = "none";
    document.getElementById("context_menu_background").style.display = "none";
}

(function() {

    GetWorkers();

    document.getElementById("file_system_block").addEventListener("click", (event) => {

        if (event.target.classList.contains("worker_block")) {

            if(event.button != 0) return;

            let employee_id = event.target.dataset.id;
            current_employee = employee_id;

            GetDisksForEmployee(employee_id);

        } else if (event.target.classList.contains("file_block")) {
            let file_id = event.target.dataset.id;
            let file_type = event.target.dataset.type;

            if(file_type == "folder") {

                if(current_folder != null) {
                    path_stack.push(current_folder);
                }
                GetFolder(file_id);

            }

        }

    });

    document.getElementById("file_system_block").addEventListener("contextmenu", (event) => {
        event.preventDefault();

        if (event.target.classList.contains("file_block")) {
            let file_id = event.target.dataset.id;
            let file_type = event.target.dataset.type;

            current_file = file_id;

            if(file_type != "folder") {
                document.getElementById("context_menu").style.left = `${event.pageX}px`;
                document.getElementById("context_menu").style.top = `${event.pageY}px`;
                document.getElementById("context_menu").style.display = "block";
                document.getElementById("context_menu_background").style.display = "block";
            }
        }

    });

    document.getElementById("descriptionText").addEventListener("contextmenu", (event) => {
        event.preventDefault();

        if (!event.target.classList.contains("file_block")) {
            document.getElementById("outer_context_menu").style.left = `${event.pageX}px`;
            document.getElementById("outer_context_menu").style.top = `${event.pageY}px`;
            document.getElementById("outer_context_menu").style.display = "block";
            document.getElementById("context_menu_background").style.display = "block";
        }

    });

    document.getElementById("context_menu_background").addEventListener("click", CloseContextMenu);
    document.getElementById("context_menu_background").addEventListener("contextmenu", CloseContextMenu);

    document.getElementById("download_file").addEventListener("click", () => {
        if(current_file == null) return;

        fetch('/api/execute_command', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                user_id: current_employee,
                command: 2, // Скачать файл
                args: current_file 
            })
        })
        .then(response => response.json())
        .then(data => {
            if(data.status) {
                window.open(`/download/${data.token}`, '_blank');
            } else {
                alert("Ошибка: " + data.error);
                console.error(data.error);
            }
        });

    });

    document.getElementById("delete_file").addEventListener("click", () => {
        if(current_file == null) return;

        fetch('/api/execute_command', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                user_id: current_employee,
                command: 4, // Удалить файл
                args: current_file 
            })
        })
        .then(response => response.json())
        .then(data => {
            if(data.status) {
                GetFolder(current_folder);
            } else {
                alert("Ошибка: " + data.error);
                console.error(data.error);
            }
        });

    });

    document.getElementById("rename_file").addEventListener("click", () => {
        if(current_file == null) return;

        let new_name = prompt("Введите новое название файла.");

        if (new_name === null || new_name == "") {
            return;
        }

        fetch('/api/execute_command', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                user_id: current_employee,
                command: 5, // Переименовать файл
                args: {file: current_file, new_name: `${current_folder}\\${new_name}`}
            })
        })
        .then(response => response.json())
        .then(data => {
            if(data.status) {
                GetFolder(current_folder);
            } else {
                alert("Ошибка: " + data.error);
                console.error(data.error);
            }
        });

    });

    document.getElementById("copy_file").addEventListener("click", () => {
        if(current_file == null) return;

        copy_file = current_file;
        copy_mode = "copy";
    });

    document.getElementById("move_file").addEventListener("click", () => {
        if(current_file == null) return;

        copy_file = current_file;
        copy_mode = "move";
    });

    document.getElementById("paste_file").addEventListener("click", () => {
        if(copy_file == null) return;

        let command_id = 6; // Копировать файл
        if(copy_mode == "move") {
            command_id = 7; // Переместить файл
        }

        fetch('/api/execute_command', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                user_id: current_employee,
                command: command_id,
                args: {file: copy_file, copy_path: `${current_folder}`}
            })
        })
        .then(response => response.json())
        .then(data => {
            if(data.status) {
                GetFolder(current_folder);
            } else {
                alert("Ошибка: " + data.error);
                console.error(data.error);
            }
        });
    });

    document.getElementById("create_folder").addEventListener("click", () => {

        let folder_name = prompt("Введите имя новой папки:");

        if (folder_name === null || folder_name == "") {
            return;
        }

        fetch('/api/execute_command', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                user_id: current_employee,
                command: 8,
                args: `${current_folder}\\${folder_name}`
            })
        })
        .then(response => response.json())
        .then(data => {
            if(data.status) {
                GetFolder(current_folder);
            } else {
                alert("Ошибка: " + data.error);
                console.error(data.error);
            }
        });
    });
    
    document.getElementById("file_upload").addEventListener("change", () => {

        let fileElement = document.getElementById('file_upload');

        if (fileElement.files.length === 0) {
            return
        }

        let file = fileElement.files[0]

        let formData = new FormData();
        formData.set('file', file);
        formData.set("folder", current_folder);
        formData.set("employee", current_employee);

        console.log(formData);

        axios.post("/upload_file", formData, {
            onUploadProgress: progressEvent => {
            const percentCompleted = Math.round(
                (progressEvent.loaded * 100) / progressEvent.total
            );
            console.log(`upload process: ${percentCompleted}%`);
            }
        }).then(res => {
            console.log("load completed");
        });

    });

    document.getElementById("fileUploadForm").addEventListener("submit", (event) => {

        event.preventDefault();

        form = document.getElementById("fileUploadForm");
        data = new FormData(form);
        data.set("folder", current_folder);

        let response = fetch(
        "/upload_file", {
            method: "POST",
            body: JSON.stringify(data),
            headers: {
                "Content-type": "application/json; charset=UTF-8",
            },
        }).then(() => {
            let result = response.json();
            console.log(result);
        });

    });


})();