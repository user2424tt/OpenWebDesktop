<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Web Desktop</title>
    <!-- Подключаем Font Awesome для иконок (полумесяц, солнце, стрелка) -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    <link rel="stylesheet" href="style.css">
</head>
<body>

    % include('templates/objects/header.tpl')

    <main>

        <div id="descriptionText" class="description-block show reg_box" style="display: block;">
            <section class="hero reg_box_buttons">
                <form action="/new_order" method="post" class="card_form_1">
                    <div>
                        <p>Клиент: </p><input required name='client'>
                    </div>
                    <div>
                        <p>Товар: </p><input required name='item' list="items">
                    </div>
                    <div>
                        <p>Количество: </p><input required name='count'>
                    </div>
                    <div>
                        <p>Информация : </p><input required name='information'>
                    </div>
                    <div>
                        <p>Вес: </p><input required name='weight'>
                    </div>
                    <div>
                        <p>Закан оплачен?: </p><input type="checkbox" name='paid'>
                    </div>

                    <datalist id="items">
                        % for item in items:
                            <option value="{{item["name"]}}"</option>
                        % end
                    </datalist>

                    <button class="company-btn">Сохранить</button>
                </form>
                <form action="/orders_list" class="card_form_2">
                    <button class="company-btn">Открыть полный список</button>
                </form>
                <form action="/" class="card_form_2">
                    <button class="company-btn">Назад</button>
                </form>
            </section>
        </div>
    </main>

    % include('templates/objects/footer.tpl')

    <script src="script.js"></script>
</body>
</html>