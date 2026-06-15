from bottle import Bottle, route, static_file, request, response, template

import database

import json

from gevent import monkey; monkey.patch_all()

main_routes = Bottle()

# Названия маршрутов
reg_page_route = "/reg_page"
auth_page_route = "/enter_page"
material_page_route = "/material_page"
material_list_route = "/material_list"
items_page_route = "/items_page"
items_list_route = "/item_list"
orders_page_route = "/orders"
orders_list_route = "/orders_list"
create_page_route = "/create"

@main_routes.route('/', method='GET')
def index():
    return template('templates/pages/main_page', root='.')

@main_routes.route(reg_page_route, method='GET')
def reg_page():
    return template('templates/pages/reg_page', root='.')

@main_routes.route('/reg_simple', method="GET")
def reg_simple_page():
    return template('templates/pages/reg_simple_page', root='.')

@main_routes.route('/file_page', method="GET")
def file_page():
    return template('templates/pages/filesystem', root='.')

@main_routes.route('/desktop', method="GET")
def desktop():
    return template('templates/pages/desktop', root='.')
    
@main_routes.route(material_page_route, method="GET")
def material_page():
    return template('templates/pages/material_page', root='.')

@main_routes.route(material_list_route, method="GET")
def material_list():
    return template('templates/pages/material_list', root='.')

@main_routes.route(items_page_route, method="GET")
def items_page():
    current_user = database.db.check_jwt_token(request.cookies.get('jwt'))
    if not current_user:
        return

    try:

        company = database.db.get_company_by_owner_id(current_user["id"])
        if not company:
            return

        materials = database.db.get_materials_by_company(company["id"])

        return template('templates/pages/items_page', root='.', materials = materials)
    except Exception as e:
        return template('templates/error')
    
@main_routes.route(f'''{items_page_route}/<id>''', method="GET")
def items_page_id(id):
    current_user = database.db.check_jwt_token(request.cookies.get('jwt'))
    if not current_user:
        return

    try:

        company = database.db.get_company_by_owner_id(current_user["id"])
        if not company:
            return

        materials = database.db.get_materials_by_company(company["id"])
        item = database.db.get_item_by_id(id, company["id"])
        if item:
            return template('templates/pages/items_page', root='.', materials = materials, item = item, item_materials=json.loads(item["materials"]))
        else:
            return template('templates/redirect', root='.', text=f'''Такого сырья нет, либо он не принадлежит Вашей компании.''', url=items_page_route)
    except Exception as e:
        return template('templates/error')

@main_routes.route(items_list_route, method="GET")
def items_list():
    return template('templates/pages/items_list', root='.')


@main_routes.route(orders_page_route, method="GET")
def orders_page():

    current_user = database.db.check_jwt_token(request.cookies.get('jwt'))
    if not current_user:
        return

    try:

        company = database.db.get_company_by_owner_id(current_user["id"])
        if not company:
            return

        items = database.db.get_items_by_company(company["id"])

        return template('templates/pages/orders_page', root='.', items = items)
    except Exception as e:
        return template('templates/error')

@main_routes.route(orders_list_route, method="GET")
def orders_list():
    return template('templates/pages/orders_list', root='.')

@main_routes.route('/register', method='POST')
def register():
    login = request.forms.getunicode('email')
    password = request.forms.getunicode('password')
    name = request.forms.getunicode('name')
    post = request.forms.getunicode('position')
    tel = request.forms.getunicode('tel')

    company_name = request.forms.getunicode('company_name')
    company_address = request.forms.getunicode('address')
    company_city = request.forms.getunicode('city')
    company_post = request.forms.getunicode('post_index')
    
    # User registration
    result = database.db.register_user(login, password, name, post, tel)
    
    if not result['success']:
        return template('templates/redirect', root='.', text=f'''Произошла ошибка регистрации: {result['error']}''', url=reg_page_route)

    result = database.db.register_company(result['id'], company_name, company_address, company_city, company_post)
    if not result['success']:
        return template('templates/redirect', root='.', text=f'''Произошла ошибка регистрации: {result['error']}''', url=reg_page_route)
    
    return template('templates/redirect', root='.', text="Регистрация успешна!", url=auth_page_route)

@main_routes.route('/register_simple', method='POST')
def register_simple():
    login = request.forms.getunicode('email')
    password = request.forms.getunicode('password')
    name = request.forms.getunicode('name')
    post = request.forms.getunicode('position')
    tel = request.forms.getunicode('tel')
    company_name = request.forms.getunicode('company_name')

    company = database.db.get_company_by_name(company_name)
    if not company:
        return template('templates/redirect', root='.', text=f'''Произошла ошибка регистрации: Ваша компания не найдена.''', url="/reg_simple")
    
    # User registration
    result = database.db.register_user(login, password, name, post, tel, company["id"])
    
    if not result['success']:
        return template('templates/redirect', root='.', text=f'''Произошла ошибка регистрации: {result['error']}''', url="/reg_simple")
    
    return template('templates/redirect', root='.', text="Регистрация успешна!", url=auth_page_route)

@main_routes.route(auth_page_route, method='GET')
def enter_page():
    return template('templates/pages/enter_page', root='.')

@main_routes.route('/enter', method='POST')
def enter():
    login = request.forms.getunicode('login')
    password = request.forms.getunicode('password')
    
    # Authentication
    jwt_token = database.db.authenticate_user(login, password)
    
    if jwt_token:
        response.set_cookie('jwt', jwt_token)
        return template('templates/redirect', root='.', text="Вы успешно авторизовались!", url="/")
    else:
        return template('templates/redirect', root='.', text="Неверный логин/пароль!", url=auth_page_route)

@main_routes.route('/new_material', method='POST')
def new_material():
    current_user = database.db.check_jwt_token(request.cookies.get('jwt'))
    if not current_user:
        return template('templates/redirect', root='.', text="Вы не авторизованы!", url=auth_page_route)

    try:

        company = database.db.get_company_by_owner_id(current_user["id"])
        if not company:
            return template('templates/redirect', root='.', text="У Вас нет своей компании!", url=material_page_route)
        
        material = request.forms.getunicode('material')
        count = float(request.forms.get('count').replace(",", '.'))
        count_unit = request.forms.getunicode('count_unit')
        unit_price = float(request.forms.get('unit_price'))

        result = database.db.get_material_by_name(material, company["id"])
        if not result:
            result = database.db.register_material(company["id"], material, count, count_unit, unit_price)
        else:
            result = database.db.update_material(company["id"], material, count, count_unit, unit_price)
        
        if not result['success']:
            return template('templates/redirect', root='.', text=f'''Произошла ошибка добавления/обновления материала: {result['error']}''', url=material_page_route)
    
        return template('templates/redirect', root='.', text="Добавление/обновление материала успешно!", url=material_page_route)
    except ValueError as ve:
        return template('templates/redirect', root='.', text=f'''Не удалось преобразовать количество товара или его цену.''', url=material_page_route)
    except Exception as e:
        return template('templates/redirect', root='.', text=f'''Произошла ошибка добавления/обновления материала: {str(e)}''', url=material_page_route)
    
@main_routes.route('/new_order', method='POST')
def new_order():
    current_user = database.db.check_jwt_token(request.cookies.get('jwt'))
    if not current_user:
        return template('templates/redirect', root='.', text="Вы не авторизованы!", url=auth_page_route)

    try:

        company = database.db.get_company_by_owner_id(current_user["id"])
        if not company:
            return template('templates/redirect', root='.', text="У Вас нет своей компании!", url=orders_page_route)
        
        client = request.forms.getunicode('client')
        item = request.forms.getunicode('item')
        count = float(request.forms.get('count').replace(",", '.'))
        information = request.forms.getunicode('information')
        weight = float(request.forms.get('weight'))
        paid = request.forms.get("paid")

        if paid == True:
            order_res = add_order(item, count, company["id"])
            if order_res == False:
                return template('templates/redirect', root='.', text=f'''Ошибка при обработке заказа: такого товара нет, либо его не хватает для выполнения заказа.''', url=orders_page_route)

        result = database.db.register_order(company["id"], client, item, count, information, weight, paid)
        
        if not result['success']:
            return template('templates/redirect', root='.', text=f'''Произошла ошибка добавления заказа: {result['error']}''', url=orders_page_route)
    
        return template('templates/redirect', root='.', text="Добавление заказа успешно!", url=orders_page_route)
    except ValueError as ve:
        return template('templates/redirect', root='.', text=f'''Не удалось преобразовать количество товаров заказа.''', url=orders_page_route)
    except Exception as e:
        return template('templates/redirect', root='.', text=f'''Произошла ошибка добавления заказа: {str(e)}''', url=orders_page_route)
    
@main_routes.route('/order_set/<id>', method="GET")
def order_set(id):
    current_user = database.db.check_jwt_token(request.cookies.get('jwt'))
    if not current_user:
        return

    try:

        company = database.db.get_company_by_owner_id(current_user["id"])
        if not company:
            return

        order = database.db.get_order_by_id(id, company["id"])
        if order:

            order["paid"] = not order["paid"]

            status = False

            if order["paid"] == False:
                status = refuse_order(order["item"], order["count"], company["id"])
            else:
                status = add_order(order["item"], order["count"], company["id"])

            if status == False:
                return template('templates/redirect', root='.', text=f'''Ошибка при обработке заказа: такого товара нет, либо его не хватает для выполнения заказа.''', url=orders_page_route)

            result = database.db.update_order(id, company["id"], order["paid"])
            if result["success"] == True:
                return template('templates/redirect', root='.', text=f'''Статус обновлён!''', url=orders_page_route)
            else:
                return template('templates/redirect', root='.', text=f'''Не удалось обновить статус заказа.''', url=orders_page_route)
        else:
            return template('templates/redirect', root='.', text=f'''Такого заказа нет, либо он не принадлежит Вашей компании.''', url=orders_page_route)
    except Exception as e:
        return template('templates/error')

@main_routes.route('/new_item', method='POST')
def new_item():
    current_user = database.db.check_jwt_token(request.cookies.get('jwt'))
    if not current_user:
        return template('templates/redirect', root='.', text="Вы не авторизованы!", url=auth_page_route)

    try:

        company = database.db.get_company_by_owner_id(current_user["id"])
        if not company:
            return template('templates/redirect', root='.', text="У Вас нет своей компании!", url=items_page_route)
        
        item = request.forms.getunicode('item')
        count = float(request.forms.get('count').replace(",", '.'))

        materials = []
        unit_price = 0.0

        i = 1
        while True:
            material_text = request.forms.getunicode('material_' + str(i))
            if material_text:

                material_count = float(request.forms.getunicode('material_' + str(i) + '_count').replace(",", '.'))

                if(material_count < 0.0):
                    return template('templates/redirect', root='.', text=f'''Количество материала не может быть отрицательным!''', url=items_page_route)
                
                if material_count == 0.0:
                    i += 1
                    continue

                material = database.db.get_material_by_name(material_text, company["id"])
                if material:
                    materials.append({"index": i, "material": material_text, "count": material_count})
                    unit_price += material["unit_price"] * material_count
                else:
                    return template('templates/redirect', root='.', text=f'''Вы не владеете одним из материалов.''', url=items_page_route)
            else:
                break
            i += 1  # Увеличиваем счетчик

        result = database.db.get_item_by_name(item, company["id"])
        if not result:
            result = database.db.register_item(company["id"], item, count, unit_price, json.dumps(materials))
        else:
            result = database.db.update_item(company["id"], item, count, unit_price, json.dumps(materials))

        if not result['success']:
            return template('templates/redirect', root='.', text=f'''Произошла ошибка добавления/обновления товара: {result['error']}''', url=items_page_route)
    
        return template('templates/redirect', root='.', text="Добавление/обновление товара успешно!", url=items_page_route)
    except ValueError as ve:
        return template('templates/redirect', root='.', text=f'''Не удалось преобразовать количество товара или другие параметры.''', url=items_page_route)
    except Exception as e:
        return template('templates/redirect', root='.', text=f'''Произошла ошибка добавления/обновления товара: {str(e)}''', url=items_page_route)

# Catch-all for other static files
@main_routes.route('/<filename:path>')
def serve_static(filename):
    return static_file("public/" + filename, root='.')

def add_order(item, count, company_id):
    item = database.db.get_item_by_name(item, company_id)
    if not item:
        return False
    
    new_count = item["count"] - count
    if(new_count < 0.0):
        return False

    result = database.db.update_item(company_id, item["name"], new_count, item["unit_price"], item["materials"])

    if result["success"] == False:
        return False
    return True

def refuse_order(item, count, company_id):
    item = database.db.get_item_by_name(item, company_id)
    if not item:
        return False
    
    if count <= 0.0:
        return False
    
    result = database.db.update_item(company_id, item["name"], item["count"] + count, item["unit_price"], item["materials"])

    if result["success"] == False:
        return False
    
    return True