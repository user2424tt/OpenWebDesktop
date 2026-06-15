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
            <section id="file_system_block" class="hero">
                
            </section>
        </div>
    </main>

    <div id="context_menu">
        <div id="download_file">Скачать файл...</div>
        <div id="delete_file">Удалить файл</div>
        <div id="rename_file">Переименовать файл</div>
        <div id="copy_file">Копировать файл</div>
        <div id="move_file">Переместить файл</div>
    </div>
    <div id="outer_context_menu">
        <div>
            <form id="fileUploadForm">
                <input name="file" type="file" id="file_upload">
                <label for="file_upload" id="upload_file">Загрузить файл...</label>
            </form>
        </div>
        <div id="paste_file">Вставить файл</div>
        <div id="create_folder">Создать папку</div>
    </div>
    <div id="context_menu_background">

    </div>

    % include('templates/objects/footer.tpl')

    <script src="axios.min.js"></script>
    <script src="script.js"></script>
    <script src="filesystem.js"></script>
</body>
</html>