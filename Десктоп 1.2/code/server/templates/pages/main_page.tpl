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
        <!-- Секция с большой надписью и стрелкой -->
        <section class="hero">
            <h1 class="big-title">Web Desktop</h1>

            <!-- Прыгающая стрелочка вниз (по клику открывает описание) -->
            <div class="arrow-down" id="toggleDescriptionBtn">
                <i class="fas fa-chevron-circle-down"></i>
            </div>

            <!-- Плавно появляющаяся надпись (описание) -->
            <div id="descriptionText" class="description-block">
                <strong>Web_Desktop</strong> — Лучший сервис для управления вашей фирмой в виртуальном пространстве.
                Web_Desktop предоставляет назначенным администраторам своей фирмы удаленный рабочий стол
                для прямого вмешательства в рабочий стол и рабочий процесс, а так же удаленную файловую систему.
            </div>

            <!-- Небольшой триггер для отслеживания прокрутки (невидимый) -->
            <div id="scroll-trigger"></div>

            <!-- Контейнер для кнопки регистрации (появится при скролле) -->
            <div class="register-section">
                <button class="company-btn" id="registerBtn">📝 Зарегистрировать компанию</button>
            </div>
        </section>
    </main>

    % include('templates/objects/footer.tpl')

    <script src="script.js"></script>
</body>
</html>