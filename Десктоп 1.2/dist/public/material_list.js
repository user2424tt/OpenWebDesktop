(function() {

    document.getElementById("material_list_block").innerHTML = ``;

    fetch('/api/get_materials', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'}
    })
    .then(response => response.json())
    .then(data => {


        if(!data.error) {

            final_html = `<table>
            <tr>
                <td>ID</td>
                <td>Сырьё</td>
                <td>Количество</td>
                <td>Цена за единицу</td>
                <td>Стоимость</td>
            </tr>`;

            data.materials.forEach(material => {
                
                final_html += `
                <tr>
                    <td>${material["id"]}</td>
                    <td>${material["name"]}</td>
                    <td>${material["count"]} ${material["unit"]}</td>
                    <td>${material["unit_price"]}</td>
                    <td>${material["unit_price"] * material["count"]}</td>
                </tr>`;

            });

            document.getElementById("material_list_block").innerHTML = final_html + "</table>";

        } else {
            alert("Ошибка: " + data.error);
        }
    });


})();