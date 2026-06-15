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
            <section id="material_list_block" class="hero">
                
            </section>
        </div>
    </main>

    </div>

    % include('templates/objects/footer.tpl')

    <script src="axios.min.js"></script>
    <script src="script.js"></script>
    <script src="material_list.js"></script>
</body>
</html>