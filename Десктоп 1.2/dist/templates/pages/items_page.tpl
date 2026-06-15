<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Web Desktop</title>
    <!-- Подключаем Font Awesome для иконок (полумесяц, солнце, стрелка) -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    <link rel="stylesheet" href="/style.css">
</head>
<body>

    % include('templates/objects/header.tpl')

    <main>

        <div id="descriptionText" class="description-block show reg_box" style="display: block;">
            <section class="hero reg_box_buttons">
                <form action="/new_item" method="post" class="card_form_1">
                    <div>
                        <p>Товар: </p><input required name='item' value="{{ item["name"] if defined('item') else '' }}">
                    </div>
                    <div>
                        <p>Количество: </p><input required name='count' value="{{ item["count"] if defined('item') else '' }}">
                    </div>
                    <div>
                        <p>Сырьё/количество: </p>
                        
                        <div id="materials_block">
                            
                            % if defined('item_materials'):
                                % # start=1
                                % for i, item_material in enumerate(item_materials, start=1):
                                    <div class="material_block">
                                        <input type="text" id="material_{{i}}" name="material_{{i}}" list="materials" value="{{item_material["material"]}}" required>
                                        <input type="number" id="material_{{i}}_count" name="material_{{i}}_count" step="any" value="{{item_material["count"]}}" required>
                                    </div>
                                % end
                            % else:
                                <div class="material_block">
                                    <input type="text" id="material_1" name="material_1" list="materials" required>
                                    <input type="number" id="material_1_count" name="material_1_count" step="any" required>
                                </div>
                            % end
                        </div>

                        <datalist id="materials">
                            % for material in materials:
                                <option value="{{material["name"]}}"</option>
                            % end
                        </datalist>
                    </div>

                    <button class="company-btn">Сохранить</button>
                </form>
                <form action="#" id="add_material" class="card_form_2">
                    <button class="company-btn">Добавить ещё сырьё...</button>
                </form>
                <form action="/item_list" class="card_form_2">
                    <button class="company-btn">Открыть полный список</button>
                </form>
                <form action="/" class="card_form_2">
                    <button class="company-btn">Назад</button>
                </form>
            </section>
        </div>
    </main>

    % include('templates/objects/footer.tpl')

    <script src="/script.js"></script>
    <script src="/items.js"></script>
</body>
</html>