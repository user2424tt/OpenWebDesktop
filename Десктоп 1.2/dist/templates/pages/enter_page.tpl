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
                <form action="/enter" method="post" class="card_form_1">
                    <div>
                        <p>Логин : </p><input name='login'>
                    </div>
                    <div>
                        <p>Пароль : </p><input type='password' name='password'>
                    </div>

                    <button class="company-btn">Вход в аккаунт</button>
                </form>
                <form action="/" class="card_form_2">
                    <button class="company-btn">Назад</button>
                </form>
                <form action="/reg_simple" class="card_form_3">
                    <button class="company-btn">Зарегистрироваться</button>
                </form>
            </section>
        </div>
    </main>

    % include('templates/objects/footer.tpl')

    <script src="script.js"></script>
</body>
</html>