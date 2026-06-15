(function() {

    document.getElementById("items_list_block").innerHTML = ``;

    fetch('/api/get_items', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'}
    })
    .then(response => response.json())
    .then(data => {


        if(!data.error) {

            final_html = `<table>
            <tr>
                <td>ID</td>
                <td>Товар</td>
                <td>Количество</td>
                <td>Цена за единицу</td>
                <td>Стоимость</td>
                <td></td>
            </tr>`;

            data.items.forEach(item => {
                
                final_html += `
                <tr>
                    <td>${item["id"]}</td>
                    <td>${item["name"]}</td>
                    <td>${item["count"]}</td>
                    <td>${item["unit_price"]}</td>
                    <td>${item["unit_price"] * item["count"]}</td>
                    <td><button class="edit_button" data-id="${item["id"]}">Изменить...</button></td>
                </tr>`;

            });

            document.getElementById("items_list_block").innerHTML = final_html + "</table>";

        } else {
            alert("Ошибка: " + data.error);
        }
    });

    document.getElementById('items_list_block').addEventListener("click", (event) => {
        if (event.target.classList.contains("edit_button")) {
            location.href=`/items_page/${event.target.dataset.id}`;
        }
    });


})();