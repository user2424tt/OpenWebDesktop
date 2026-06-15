import sqlite3
import hashlib
import base64
import bcrypt
import jwt
import datetime

from gevent import monkey; monkey.patch_all()

jwt_secret = "BRYWuWLuzmU8Ni5D-JZgmN1EFKZ3pZ_e"
jwt_token_weeks_limit = 5
db_file_name = "database.db"

# Database initialization
def init_database():
    """Creates database and tables if they don't exist"""
    conn = sqlite3.connect(db_file_name)
    cursor = conn.cursor()
    
    # Create tables with updated structure
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
        id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
        login STRING UNIQUE NOT NULL,
        password STRING NOT NULL,
        name STRING NOT NULL,
        post STRING NOT NULL,
        tel STRING NOT NULL,
        company_id INTEGER
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Companies (
        id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
        owner_id INTEGER REFERENCES Users (id) NOT NULL,
        name STRING UNIQUE NOT NULL,
        address STRING NOT NULL,
        city STRING NOT NULL,
        post STRING NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Materials (
        id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
        company_id INTEGER REFERENCES Companies (id) NOT NULL,
        name STRING NOT NULL,
        count DOUBLE,
        unit STRING NOT NULL,
        unit_price DOUBLE,
        UNIQUE (company_id, name)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Items (
        id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
        company_id INTEGER REFERENCES Companies (id) NOT NULL,
        name STRING NOT NULL,
        materials STRING NOT NULL,
        count DOUBLE,
        unit_price DOUBLE,
        UNIQUE (company_id, name)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
        company_id INTEGER REFERENCES Companies (id) NOT NULL,
        client STRING NOT NULL,
        item STRING NOT NULL,
        count DOUBLE,
        information STRING NOT NULL,
        weight DOUBLE,
        paid BOOLEAN,
        date DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()
    conn.close()

class DatabaseManager:
    def __init__(self, db_name=db_file_name):
        self.db_name = db_name
        init_database()

    def check_jwt_token(self, token):
        try:
            decoded = jwt.decode(token, jwt_secret, algorithms=["HS256"])

            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT id, login FROM Users WHERE id=? AND login=?",
                (decoded["id"], decoded["login"],)
            )
            
            user = cursor.fetchone()
            conn.close()
            
            if user:
                return decoded
            else:
                return None
        except jwt.ExpiredSignatureError:
            print("Срок действия токена истёк")
            return None
        except jwt.InvalidSignatureError:
            print("Недействительная подпись токена")
            return None
        except jwt.InvalidTokenError:
            print("Недействительный токен")
            return None
    
    def authenticate_user(self, login, password):
        """Authenticate user"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT id, login, password FROM Users WHERE login=?",
                (login,)
            )
            
            user = cursor.fetchone()
            conn.close()
            
            if user:
                if bcrypt.checkpw(base64.b64encode(hashlib.sha256(password.encode()).digest()), user[2]):
                    payload = {"id": user[0], "login": user[1], "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(weeks=jwt_token_weeks_limit)}
                    return jwt.encode(payload, jwt_secret, algorithm="HS256")
                else:
                    return None
            return None
        except Exception as e:
            print(f"Authentication error: {e}")
            return None
    
    def register_user(self, login, password, name, post, tel, company_id=-1):
        """Register new user"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # Check if user exists
            cursor.execute("SELECT id FROM Users WHERE login=?", (login,))
            if cursor.fetchone():
                conn.close()
                return {'success': False, 'error': 'Пользователь уже существует'}

            hashed = bcrypt.hashpw(
                base64.b64encode(hashlib.sha256(password.encode()).digest()),
                bcrypt.gensalt()
            )
            
            # Add new user
            cursor.execute(
                "INSERT INTO Users (login, password, name, post, tel, company_id) VALUES (?, ?, ?, ?, ?, ?) RETURNING id",
                (login, hashed, name, post, tel, company_id)
            )

            id = cursor.fetchone()[0]
            
            conn.commit()
            conn.close()
            return {'success': True, 'id': id, 'message': 'Регистрация успешна!'}
        except Exception as e:
            print(f"Registration error: {e}")
            return {'success': False, 'error': str(e)}
        
    def register_company(self, owner_id, name, address, city, post):
        """Register new company"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # Add new user
            cursor.execute(
                "INSERT INTO Companies (owner_id, name, address, city, post) VALUES (?, ?, ?, ?, ?)",
                (owner_id, name, address, city, post)
            )
            
            conn.commit()
            conn.close()
            return {'success': True, 'message': 'Регистрация успешна!'}
        except Exception as e:
            print(f"Registration error: {e}")
            return {'success': False, 'error': str(e)}
        
    def get_company_by_name(self, company_name):
        """Get company by name"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, owner_id, name, address, city, post FROM Companies WHERE name=?",
                (company_name,)
            )

            company = cursor.fetchone()
            conn.close()
            
            if company:
                return {
                    'id': company[0],
                    'owner_id': company[1],
                    'name': company[2],
                    'address': company[3],
                    'city': company[4],
                    'post': company[5]
                }
            return None
        except Exception as e:
            print(f"Get company error: {e}")
            return None

    def get_company_by_owner_id(self, owner_id):
        """Get company by owner_id"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, owner_id, name, address, city, post FROM Companies WHERE owner_id=?",
                (owner_id,)
            )

            company = cursor.fetchone()
            conn.close()
            
            if company:
                return {
                    'id': company[0],
                    'owner_id': company[1],
                    'name': company[2],
                    'address': company[3],
                    'city': company[4],
                    'post': company[5]
                }
            return None
        except Exception as e:
            print(f"Get company error: {e}")
            return None

    def get_user_by_id(self, user_id):
        """Get company by user_id"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, login, name, post, tel, company_id FROM Users WHERE id = ?",
                (user_id,)
            )

            employee = cursor.fetchone()
            conn.close()
            
            if employee:
                return {
                    'id': employee[0],
                    'login': employee[1],
                    'name': employee[2],
                    'post': employee[3],
                    'tel': employee[4],
                    'company_id': employee[5]
                }
            return None
        except Exception as e:
            print(f"Get company error: {e}")
            return None
        
    def get_material_by_name(self, name, company_id):
        """Get material of company by name"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, name, company_id, unit_price FROM Materials WHERE name = ? AND company_id = ?",
                (name, company_id)
            )

            material = cursor.fetchone()
            conn.close()
            
            if material:
                return {
                    'id': material[0],
                    'name': material[1],
                    'company_id': material[2],
                    'unit_price': material[3],
                }
            return None
        except Exception as e:
            print(f"Get material error: {e}")
            return None

    def get_order_by_id(self, id, company_id):
        """Get order of company by id"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, item, company_id, client, count, information, weight, paid, date FROM Orders WHERE id = ? AND company_id = ?",
                (id, company_id)
            )

            order = cursor.fetchone()
            conn.close()
            
            if order:
                return {
                    'id': order[0],
                    'item': order[1],
                    'company_id': order[2],
                    'client': order[3],
                    'count': order[4],
                    'information': order[5],
                    'weight': order[6],
                    'paid': order[7],
                    'date': order[8],
                }
            return None
        except Exception as e:
            print(f"Get order error: {e}")
            return None
        
    def get_item_by_id(self, id, company_id):
        """Get item of company by name"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, name, company_id, materials, count, unit_price FROM Items WHERE id = ? AND company_id = ?",
                (id, company_id)
            )

            item = cursor.fetchone()
            conn.close()
            
            if item:
                return {
                    'id': item[0],
                    'name': item[1],
                    'company_id': item[2],
                    'materials': item[3],
                    'count': item[4],
                    'unit_price': item[5],
                }
            return None
        except Exception as e:
            print(f"Get item error: {e}")
            return None
        
    def get_item_by_name(self, name, company_id):
        """Get item of company by name"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, name, company_id, unit_price, count, materials FROM Items WHERE name = ? AND company_id = ?",
                (name, company_id)
            )

            item = cursor.fetchone()
            conn.close()
            
            if item:
                return {
                    'id': item[0],
                    'name': item[1],
                    'company_id': item[2],
                    'unit_price': item[3],
                    'count': item[4],
                    'materials': item[5]
                }
            return None
        except Exception as e:
            print(f"Get item error: {e}")
            return None
    
    def get_workers_by_company(self, company_id):
        """Get list of workers by company"""
        try:

            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("SELECT id, login, name, post, tel, company_id FROM Users WHERE company_id = ?", (company_id,))
            employees = cursor.fetchall()
            conn.close()
            
            return [
                {
                    'id': employee[0],
                    'login': employee[1],
                    'name': employee[2],
                    'post': employee[3],
                    'tel': employee[4],
                    'company_id': employee[5]
                }
                for employee in employees
            ]
        except Exception as e:
            print(f"Get workers error: {e}")
            return []
        
    def get_materials_by_company(self, company_id):
        """Get list of materials by company"""
        try:

            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("SELECT id, company_id, name, count, unit, unit_price FROM Materials WHERE company_id = ?", (company_id,))
            materials = cursor.fetchall()
            conn.close()
            
            return [
                {
                    'id': material[0],
                    'company_id': material[1],
                    'name': material[2],
                    'count': material[3],
                    'unit': material[4],
                    'unit_price': material[5]
                }
                for material in materials
            ]
        except Exception as e:
            print(f"Get materials error: {e}")
            return []
        
    def register_material(self, company_id, name, count, unit, unit_price):
        """Register new material for company"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # Add new user
            cursor.execute(
                "INSERT INTO Materials (company_id, name, count, unit, unit_price) VALUES (?, ?, ?, ?, ?)",
                (company_id, name, count, unit, unit_price)
            )
            
            conn.commit()
            conn.close()
            return {'success': True, 'message': 'Материал добавлен!'}
        except Exception as e:
            print(f"Registration of material error: {e}")
            return {'success': False, 'error': str(e)}
        
    def update_material(self, company_id, name, count, unit, unit_price):
        """Update material for company"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()

            print(count)

            if(count == 0.0):
                cursor.execute(
                    "DELETE FROM Materials WHERE `company_id` = ? AND `name` = ?",
                    (company_id, name)
                )
            else:
                cursor.execute(
                    "UPDATE Materials SET `count` = ?, `unit` = ?, `unit_price` = ? WHERE `company_id` = ? AND `name` = ?",
                    (count, unit, unit_price, company_id, name)
                )
            
            conn.commit()
            conn.close()
            return {'success': True, 'message': 'Материал обновлён!'}
        except Exception as e:
            print(f"Update of material error: {e}")
            return {'success': False, 'error': str(e)}
        

    def get_items_by_company(self, company_id):
        """Get list of items by company"""
        try:

            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("SELECT id, company_id, name, count, unit_price, materials FROM Items WHERE company_id = ?", (company_id,))
            items = cursor.fetchall()
            conn.close()
            
            return [
                {
                    'id': item[0],
                    'company_id': item[1],
                    'name': item[2],
                    'count': item[3],
                    'unit_price': item[4],
                    'materials': item[5]
                }
                for item in items
            ]
        except Exception as e:
            print(f"Get items error: {e}")
            return []
        
    def register_item(self, company_id, name, count, unit_price, materials):
        """Register new item for company"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # Add new user
            cursor.execute(
                "INSERT INTO Items (company_id, name, count, unit_price, materials) VALUES (?, ?, ?, ?, ?)",
                (company_id, name, count, unit_price, materials)
            )
            
            conn.commit()
            conn.close()
            return {'success': True, 'message': 'Товар добавлен!'}
        except Exception as e:
            print(f"Registration of item error: {e}")
            return {'success': False, 'error': str(e)}
        
    def register_order(self, company_id, client, item, count, information, weight, paid):
        """Register new order for company"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # Add new order
            cursor.execute(
                "INSERT INTO Orders (company_id, client, item, count, information, weight, paid) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (company_id, client, item, count, information, weight, paid)
            )
            
            conn.commit()
            conn.close()
            return {'success': True, 'message': 'Заказ добавлен!'}
        except Exception as e:
            print(f"Registration of order error: {e}")
            return {'success': False, 'error': str(e)}
        
    def update_item(self, company_id, name, count, unit_price, materials):
        """Update item for company"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()

            print(materials)

            if(count == 0.0):
                cursor.execute(
                    "DELETE FROM Items WHERE `company_id` = ? AND `name` = ?",
                    (company_id, name)
                )
            else:
                cursor.execute(
                    "UPDATE Items SET `count` = ?, `unit_price` = ?, `materials` = ? WHERE `company_id` = ? AND `name` = ?",
                    (count, unit_price, materials, company_id, name)
                )
            
            conn.commit()
            conn.close()
            return {'success': True, 'message': 'Товар обновлён!'}
        except Exception as e:
            print(f"Update of item error: {e}")
            return {'success': False, 'error': str(e)}
        
    def update_order(self, id, company_id, paid):
        """Update status of the order for company"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()

            cursor.execute(
                "UPDATE Orders SET `paid` = ? WHERE `company_id` = ? AND `id` = ?",
                (paid, company_id, id)
            )
            
            conn.commit()
            conn.close()
            return {'success': True, 'message': 'Заказ обновлён!'}
        except Exception as e:
            print(f"Update of item error: {e}")
            return {'success': False, 'error': str(e)}
        
    def get_orders_by_company(self, company_id):
        """Get list of orders by company"""
        try:

            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("SELECT id, company_id, client, item, count, information, weight, paid, date FROM Orders WHERE company_id = ?", (company_id,))
            orders = cursor.fetchall()
            conn.close()
            
            return [
                {
                    'id': order[0],
                    'company_id': order[1],
                    'client': order[2],
                    'item': order[3],
                    'count': order[4],
                    'information': order[5],
                    'weight': order[6],
                    'paid': order[7],
                    'date': order[8]
                }
                for order in orders
            ]
        except Exception as e:
            print(f"Get orders error: {e}")
            return []

# Create database instance
db = DatabaseManager()