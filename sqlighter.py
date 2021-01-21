import sqlite3


class SQLighter:

    def __init__(self, tables):
        self.connection = sqlite3.connect(tables)
        self.cursor = self.connection.cursor()

    def add_user(self, chatID, status=False):
        """Добавляем нового юзера в бд (неуверен)"""

        with self.connection:
            return self.cursor.execute("INSERT or IGNORE into 'users' ('chatID', 'status') VALUES(?,?)",
                                       (chatID, status))

    def add_user_2(self, chatID, state):
        with self.connection:
            return self.cursor.execute("INSERT or IGNORE into 'users_states' ('chatID', 'state') VALUES(?,?)",
                                       (chatID, state))

    def user_exists(self, chatID):
        """Проверяем есть ли юзер в базе (неуверен)"""
        with self.connection:
            return bool(len(self.cursor.execute('SELECT * FROM "users" WHERE "chatID" = ?', (chatID,)).fetchall()))

    def status_true(self, status, chatID):
        """Меняем status юзера на False"""
        with self.connection:
            return self.cursor.execute('UPDATE "users" SET "status" = ? WHERE "chatID" = ?', (status, chatID))

    def finding_free_chat(self, chatID, partner_chatID, status=False):
        """Ищем юзера с условием: status = 1, partner_chatID = Null/None
        Добавляем его chatID в partner_chatID и наоборот. У обоих сбрасываем status"""
        try:
            with self.connection:
                free_user = self.cursor.execute('SELECT chatID FROM "users" WHERE "chatID" !=? AND "status" = 1 '
                                                'AND "partner_chatID" IS NULL LIMIT 1', (chatID,)).fetchall()
                free_user = free_user[0][0]
                # Получаем переменную partner_chatID
                self.cursor.execute('UPDATE "users" SET "partner_chatID" = ? WHERE "chatID" = ?',
                                                                                        (free_user, chatID)).fetchall()
                self.cursor.execute('UPDATE "users" SET "partner_chatID" = ? WHERE "chatID" = ?', (chatID, free_user))
                self.cursor.execute('UPDATE "users" SET "status" = ? WHERE "chatID" = ?', (status, chatID))
                self.cursor.execute('UPDATE "users" SET "status" = ? WHERE "chatID" = ?', (status, free_user))

                # me_pcID и par_pcID - Добавляет id собеседников друг другу в partner_chatID
                # me_status и par_status - Сбрасывает status на 0
                return free_user
        except:
            return None

    def status_false_and_clear_partner(self, status, chatID, partner_chatID):
        """Меняем status юзера на False"""
        with self.connection:
            partner = self.cursor.execute('SELECT partner_chatID FROM "users" WHERE "chatID" = ?', (chatID,)).fetchall()
            partner = partner[0][0]
            self.cursor.execute('UPDATE "users" SET "status" = ? WHERE "chatID" = ?', (status, chatID))
            self.cursor.execute('UPDATE "users" SET "partner_chatID" = ? WHERE "chatID" = ?', (partner_chatID, chatID))
            self.cursor.execute('UPDATE "users" SET "partner_chatID" = ? WHERE "chatID" = ?', (partner_chatID, partner))
            return partner

    def pcID_checker(self, chatID):
        with self.connection:
            pcID = self.cursor.execute('SELECT partner_chatID FROM "users" WHERE "chatID" = ?', (chatID,)).fetchall()
            return pcID[0][0]

    def user_deleting(self, chatID):
        """Удаляем из базы данных"""
        with self.connection:
            return self.cursor.execute('DELETE FROM "users" WHERE "chatID" = ?', (chatID,))