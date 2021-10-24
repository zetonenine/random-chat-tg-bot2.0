import logging
from lunchtime.db.models import Database
from lunchtime.db.cache import Cache

logging.basicConfig(level=logging.INFO)


class DataInterface(Database, Cache):

    def count_users(self):
        return self.count_users_row()

    def check_user(self, user_id):
        return self.user_exists(user_id)

    def add_user(self, user_id):
        return self.add_user_to_users(user_id)

    def add_connects(self, user_id):
        return self.add_user_to_connects(user_id)

    def add_connects2(self, user_id):
        return self.find_free_user(user_id)

    def start_room_chat(self, user_id):
        partner_id = self.connect_users(user_id)
        if partner_id is not None:
            self.add_connects_cache(user_id, partner_id)
        return partner_id

    def start_room_chat2(self, user_id, partner_id):
        self.add_connects_cache(user_id, partner_id)
        return partner_id

    def stop_room_chat(self, user_id):
        partner_id = self.disconnect_users(user_id)
        self.rem_connects_cache(user_id, partner_id)
        return partner_id

    def stop_room_chat2(self, user_id, partner_id):
        self.rem_connects_cache(user_id, partner_id)
        return partner_id

    def stop_searching(self, user_id):
        return self.remove_user_from_connects(user_id)

    def stop_searching2(self, user_id):
        return self.rem_user_from_order(user_id)

    def login_check(self, login):
        return self.get_role_by_login(login)

    def get_login_name_by_user_id(self, user_id):
        return self.get_role_login_by_user_id(user_id)

    def get_banner(self):
        return self.get_random_text_from_commercial()

    def get_partner_user_id(self, user_id):
        return self.get_partner_id(user_id)

    def get_all_commercial(self):
        return self.show_commercial()

    def add_new_commercial_text(self, text):
        return self.add_new_commercial(text)

    def remove_commercial_text(self, id):
        return self.del_commercial(id)

    def add_new_role(self, login, password, role, user_id):
        return self.insert_into_Roles(login, password, role, user_id)

    def show_roles(self):
        return self.get_roles_from_Roles()

    def del_role(self, role_id):
        return self.del_role_from_Roles(role_id)

    def most_reports_users(self):
        return self.get_users_order_by_amount_reports()

    def get_reports_messages(self, reports_id):
        return self.get_report_by_id(reports_id)

    def get_login_from_role(self, user_id):
        return self.get_login_from_Role(user_id)

    def add_report(self, attrs):
        return self.insert_report_into_Reports(attrs)

    def get_report(self, report_id):
        return self.get_report_by_id2(report_id)

    def get_last_report(self):
        return self.get_last_report_order_by_date()

    def remove_Report(self, report_id):
        return self.remove_report_from_Report(report_id)

    def add_Ban(self, user, user_id, reason, message, terms):
        return self.insert_into_Ban(user, user_id, reason, message, terms)

    def get_last_bans(self):
        return self.get_bans_order_by_date()

    def get_ban_by_id(self, ban_id):
        return self.get_ban_by_id_from_Ban(ban_id)

    def get_ban_by_date(self, date):
        return self.get_ban_by_date_from_Ban(date)

    def remove_ban(self, ban_id):
        return self.remove_ban_from_Ban(ban_id)
