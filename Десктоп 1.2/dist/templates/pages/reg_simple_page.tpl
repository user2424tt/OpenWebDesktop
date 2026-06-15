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
                <form action="/register_simple" method="post" class="card_form_1">
                    <div>
                        <p>Адрес электронной почты : </p><input required type="email" name='email'>
                    </div>
                    <div>
                        <p>Пароль: </p><input required type="password" name='password'>
                    </div>
                    <div>
                        <p>ФИО : </p><input required name='name'>
                    </div>
                    <div>
                        <p>Должность : </p><input required name='position'>
                    </div>
                    <div>
                        <p>Телефон : </p><input required type="tel" name='tel'>
                    </div>
                    <div>
                        <p>Имя компании : </p><input required name='company_name'>
                    </div>

                    <button class="company-btn">Регистрация</button>
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