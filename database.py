import sqlite3

class Database:
    def __init__(self, database_file):
        """Конструктор, инициализирует соединение с базой данных."""
        self.connection = sqlite3.connect(database_file)
        self.cursor = self.connection.cursor()

    def create_tables(self):
        """Создает необходимые таблицы в базе данных, если их нет."""
        self.cursor.executescript('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                first_name TEXT,
                last_name TEXT,
                username TEXT,
                progress INTEGER DEFAULT 0,
                score INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS test_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                document TEXT,
                correct_answers INTEGER,
                total_questions INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            );

            CREATE TABLE IF NOT EXISTS user_progress (
                user_id INTEGER,
                section_id TEXT,
                completed BOOLEAN,
                PRIMARY KEY(user_id, section_id),
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            );

            CREATE TABLE IF NOT EXISTS admins (
                user_id INTEGER PRIMARY KEY,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            );
        ''')
        self.connection.commit()

    def add_user(self, user_id, first_name, last_name, username):
        """Добавляет нового пользователя в базу данных."""
        with self.connection:
            self.cursor.execute('''
                INSERT OR IGNORE INTO users (user_id, first_name, last_name, username)
                VALUES (?, ?, ?, ?)
            ''', (user_id, first_name, last_name, username))

    def get_user(self, user_id):
        """Возвращает данные пользователя по его ID."""
        with self.connection:
            return self.cursor.execute('''
                SELECT * FROM users WHERE user_id = ?
            ''', (user_id,)).fetchone()

    def save_test_result(self, user_id, document, correct_answers, total_questions):
        with self.connection:
            self.cursor.execute('''
                INSERT INTO test_results (user_id, document, correct_answers, total_questions)
                VALUES (?, ?, ?, ?)
            ''', (user_id, document, correct_answers, total_questions))

    def get_test_results(self, user_id):
        with self.connection:
            return self.cursor.execute('''
                SELECT document, correct_answers, total_questions, timestamp
                FROM test_results WHERE user_id = ? ORDER BY timestamp DESC
            ''', (user_id,)).fetchall()

    def get_all_test_results(self):
        with self.connection:
            return self.cursor.execute('''
                SELECT users.username, test_results.document, test_results.correct_answers, test_results.total_questions, test_results.timestamp
                FROM test_results
                JOIN users ON test_results.user_id = users.user_id
                ORDER BY test_results.timestamp DESC
            ''').fetchall()

    def add_admin(self, user_id):
        """Добавляет администратора в базу данных."""
        with self.connection:
            self.cursor.execute('''
                INSERT OR IGNORE INTO admins (user_id)
                VALUES (?)
            ''', (user_id,))
            self.connection.commit()

    def remove_admin(self, user_id):
        """Удаляет администратора из базы данных."""
        with self.connection:
            self.cursor.execute('''
                DELETE FROM admins WHERE user_id = ?
            ''', (user_id,))
            self.connection.commit()

    def is_admin(self, user_id):
        """Проверяет, является ли пользователь администратором."""
        with self.connection:
            return self.cursor.execute('''
                SELECT 1 FROM admins WHERE user_id = ?
            ''', (user_id,)).fetchone() is not None

    def get_all_admins(self):
        """Возвращает список всех администраторов."""
        with self.connection:
            return self.cursor.execute('SELECT user_id FROM admins').fetchall()

    def get_test_results_for_user(self, user_id):
        with self.connection:
            return self.cursor.execute('''
                SELECT test_results.document, test_results.correct_answers, test_results.total_questions, test_results.timestamp
                FROM test_results
                WHERE test_results.user_id = ?
                ORDER BY test_results.timestamp DESC
            ''', (user_id,)).fetchall()

    def get_all_users(self):
        """Возвращает список всех пользователей, которые проходили тесты."""
        with self.connection:
            return self.cursor.execute('SELECT DISTINCT user_id, username FROM users WHERE user_id IN (SELECT DISTINCT user_id FROM test_results)').fetchall()

    def update_progress(self, user_id, section_id, completed=True):
        """Обновляет прогресс пользователя по теме."""
        with self.connection:
            self.cursor.execute('''
                INSERT OR REPLACE INTO user_progress (user_id, section_id, completed)
                VALUES (?, ?, ?)
            ''', (user_id, section_id, completed))
            self.connection.commit()

    def get_progress(self, user_id):
        """Возвращает прогресс пользователя по всем темам."""
        with self.connection:
            return self.cursor.execute('''
                SELECT section_id, completed
                FROM user_progress
                WHERE user_id = ?
            ''', (user_id,)).fetchall()

    def get_all_admins_views(self):
        """Возвращает список всех администраторов с информацией о пользователях."""
        with self.connection:
            return self.cursor.execute('''
                SELECT admins.user_id, users.username 
                FROM admins
                JOIN users ON admins.user_id = users.user_id
            ''').fetchall()

db = Database('database.db')
