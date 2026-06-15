(function() {

    document.getElementById("order_list_block").innerHTML = ``;

    fetch('/api/get_orders', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'}
    })
    .then(response => response.json())
    .then(data => {


        if(!data.error) {

            final_html = `<table>
            <tr>
                <td>№</td>
                <td>Клиент</td>
                <td>Товар</td>
                <td>Информация</td>
                <td>Дата</td>
                <td>Вес</td>
                <td>Кол-во</td>
                <td>Цена</td>
                <td>Сумма</td>
                <td>Статус</td>
                <td>Действия</td>
            </tr>`;

            data.orders.forEach(order => {
                
                status = "Не оплачен";
                if(order["paid"]) {
                    status = "Оплачен";
                }

                final_html += `
                <tr>
                    <td>${order["id"]}</td>
                    <td>${order["client"]}</td>
                    <td>${order["item"]}</td>
                    <td>${order["information"]}</td>
                    <td>${order["date"]}</td>
                    <td>${order["weight"]}</td>
                    <td>${order["count"]}</td>
                    <td>${order["price"]}</td>
                    <td>${order["sum"]}</td>
                    <td>${status}</td>
                    <td><button class="edit_button" data-id="${order["id"]}">Сменить статус</button></td>
                </tr>`;

            });

            document.getElementById("order_list_block").innerHTML = final_html + "</table>";

        } else {
            alert("Ошибка: " + data.error);
        }
    });

    document.getElementById('order_list_block').addEventListener("click", (event) => {
        if (event.target.classList.contains("edit_button")) {
            location.href=`/order_set/${event.target.dataset.id}`;
        }
    });


})();