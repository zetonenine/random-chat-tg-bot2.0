import logging
from models import Database, initdb


logging.basicConfig(level=logging.INFO)


class DataInterface(Database):

    def count_users(self):
        return self.count_users_row()

    def check_user(self, user_id):
        return self.user_exists(user_id)

    def add_user(self, user_id):
        return self.add_user_to_users(user_id)

    def add_connects(self, user_id):
        return self.add_user_to_connects(user_id)

    def start_room_chat(self, user_id):
        return self.connect_users(user_id)

    def stop_room_chat(self, user_id):
        return self.disconnect_users(user_id)

    def stop_searching(self, user_id):
        return self.remove_user_from_connects(user_id)

    def get_banner(self):
        return self.get_random_text_from_commercial()

    def get_partner_id(self, user_id):
        return self.get_partner_user_id(user_id)

    def get_all_commercial(self):
        return self.show_commercial()

    def add_new_commercial_text(self, text):
        return self.add_new_commercial(text)

    def remove_commercial_text(self, id):
        return self.del_commercial(id)
