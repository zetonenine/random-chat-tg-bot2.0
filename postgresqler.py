import psycopg2


class BD:

    def __init__(self, user="postgres", password="postgres", dbname="postgres", host="localhost"):
        self.connection = psycopg2.connect(
            user=user,
            password=password,
            dbname=dbname,
            host=host)
        self.cursor = self.connection.cursor()

    def create(self):
        commands = (
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER NOT NULL PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
                chat INTEGER NOT NULL,
                partner_chat INTEGER,
                status BOOLEAN DEFAULT FALSE
                )
            """
        )    
        with self.connection:
            return self.cursor.execute(commands)

    def count_user(self):
        with self.connection:
            return self.cursor.execute("SELECT COUNT(*) FROM users")

    def add_user(self, chatID, status=False):
        with self.connection:
            return self.cursor.execute("INSERT INTO users (chat, status) VALUES (%s, %s)", (chatID, status))

    def user_exists(self, chatID):
        with self.connection:
            self.cursor.execute("SELECT exists(SELECT 1 FROM users WHERE chat = (%s))", (chatID,))
            obj = self.cursor.fetchall()
            return obj[0][0]
    
    def status_true(self, chatID, status=True):
        with self.connection:
            return self.cursor.execute("UPDATE users SET status = (%s) WHERE chat = (%s)", (status, chatID))

    def finding_free_chat(self, chatID):

        try:
            with self.connection:
                self.cursor.execute("SELECT chat FROM users WHERE chat !=(%s) AND status = 'True' "
                                    "AND partner_chat IS NULL LIMIT 1", (chatID,))
                free = self.cursor.fetchall()
                free_user = free[0][0]

                self.cursor.execute("UPDATE users SET partner_chat = (%s) WHERE chat = (%s)", (free_user, chatID))
                self.cursor.execute("UPDATE users SET partner_chat = (%s) WHERE chat = (%s)", (chatID, free_user))
                self.cursor.execute("UPDATE users SET status = 'False' WHERE chat = (%s)", (chatID,))
                self.cursor.execute("UPDATE users SET status = 'False' WHERE chat = (%s)", (free_user,))

                return free_user

        except:
            return None

    def status_false_and_clear_partner(self, chatID):
        with self.connection:
            self.cursor.execute("SELECT partner_chat FROM users WHERE chat = (%s)", (chatID,))
            free = self.cursor.fetchall()
            partner = free[0][0]

            self.cursor.execute("UPDATE users SET status = 'False' WHERE chat = (%s)", (chatID,))
            self.cursor.execute("UPDATE users SET partner_chat = (%s) WHERE chat = (%s)", (None, chatID))
            self.cursor.execute("UPDATE users SET partner_chat = (%s) WHERE chat = (%s)", (None, partner))
            return partner

    def pcID_checker(self, chatID):
        with self.connection:
            self.cursor.execute("SELECT partner_chat FROM users WHERE chat = (%s)", (chatID,))
            pcID = self.cursor.fetchall()
            return pcID[0][0]

    def user_exists(self, id):
        pass
