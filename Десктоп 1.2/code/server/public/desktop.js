let current_employee = null;
let canvas, ctx;
let socket = null;

let current_time = Date.now();

const img = new Image();

function GetWorkers() {

    document.getElementById("desktop_block").innerHTML = ``;

    fetch('/api/get_workers', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'}
    })
    .then(response => response.json())
    .then(data => {
        if(!data.error) {
            data.workers.forEach(worker => {
                
                document.getElementById("desktop_block").innerHTML += `
                <div class="worker_block" data-id="${worker['id']}">${worker['name']}</div>
                `;

            });

        } else {
            alert("Ошибка: " + data.error);
        }
    });
}

function sendKeyEvent(endpoint, event) {
    if (event.key.startsWith('F') && !isNaN(event.key.substring(1))) return;
    event.preventDefault();
    socket.send(JSON.stringify({"type": endpoint, "user_id": employee_id, "key": event.key}));
}

function ConnectToEmployee(employee_id) {
    fetch('/api/execute_command', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            user_id: employee_id,
            command: 10, // Получить размер монитора
            args: "" 
        })
    })
    .then(response => response.json())
    .then(data => {
        if(data.status) {

            canvas = document.getElementById("canvas");
            ctx = canvas.getContext("2d");

            document.getElementById("remote_block").style.display = "block";
            document.getElementById("header").remove();
            document.getElementById("main").remove();
            document.getElementById("footer").remove();
            
            canvas.width = data.width;
            canvas.height = data.height;

            socket = new WebSocket(`ws://${window.location.hostname}:3000/remote`);
            socket.onopen = function() {

                canvas.addEventListener('mousemove', (event) => {
                    if(Date.now() - current_time < 100) return;

                    const rect = canvas.getBoundingClientRect();
                    
                    const x = event.clientX - rect.left;
                    const y = event.clientY - rect.top;

                    socket.send(JSON.stringify({"type": "mouse_move", "user_id": employee_id, "x": x, "y": y}));

                    current_time = Date.now();
                });

                canvas.addEventListener('click', (event) => {
                    const rect = canvas.getBoundingClientRect();
                    
                    const x = event.clientX - rect.left;
                    const y = event.clientY - rect.top;

                    socket.send(JSON.stringify({"type": "mouse_click", "user_id": employee_id, "x": x, "y": y, "button": "left"}));
                });

                canvas.addEventListener('contextmenu', (event) => {
                    event.preventDefault();
                    
                    const rect = canvas.getBoundingClientRect();
                    
                    const x = event.clientX - rect.left;
                    const y = event.clientY - rect.top;

                    socket.send(JSON.stringify({"type": "mouse_click", "user_id": employee_id, "x": x, "y": y, "button": "right"}));
                    
                });

                canvas.addEventListener('auxclick', (event) => {
                    if (event.button === 1) {
                        event.preventDefault();
                    
                        const rect = canvas.getBoundingClientRect();
                        
                        const x = event.clientX - rect.left;
                        const y = event.clientY - rect.top;

                        socket.send(JSON.stringify({"type": "mouse_click", "user_id": employee_id, "x": x, "y": y, "button": "middle"}));
                    }
                });

                /*window.addEventListener('keydown', (event) => {
                    socket.send(JSON.stringify({"type": "key", "user_id": employee_id, "key": event.key}));
                });*/

                window.addEventListener('keydown', function(event) {
                    sendKeyEvent('keydown', event);
                });

                window.addEventListener('keyup', function(event) {
                    sendKeyEvent('keyup', event);
                });

                canvas.addEventListener('dblclick', (event) => {
                    const rect = canvas.getBoundingClientRect();
                    
                    const x = event.clientX - rect.left;
                    const y = event.clientY - rect.top;

                    socket.send(JSON.stringify({"type": "dbl_mouse_click", "user_id": employee_id, "x": x, "y": y}));
                });

                socket.send(JSON.stringify({"type": "worker_select", "user_id": employee_id}));
            };
            socket.onmessage = function (event) {
                socket_data = JSON.parse(event.data);

                if(socket_data["type"] == "screen") {
                    const binaryString = atob(socket_data["frame"]);

                    const len = binaryString.length;
                    const bytes = new Uint8Array(len);
                    for (let i = 0; i < len; i++) {
                        bytes[i] = binaryString.charCodeAt(i);
                    }

                    const blob = new Blob([bytes], { type: 'image/jpeg' });
                    const imageUrl = URL.createObjectURL(blob);
                    img.src = imageUrl;
                }

            };


        } else {
            alert("Ошибка: " + data.error);
            console.error(data.error);
        }
    });
}

(function() {

    GetWorkers();

    document.getElementById("desktop_block").addEventListener("click", (event) => {

        if (event.target.classList.contains("worker_block")) {

            if(event.button != 0) return;

            let employee_id = event.target.dataset.id;
            current_employee = employee_id;

            ConnectToEmployee(employee_id);

        }

    });


})();

img.onload = function() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(img, 0, 0, canvas.width, canvas.height); 
};