import argparse
from lunchtime.db.adapter import DataInterface
from lunchtime.db.models import initdb

db = DataInterface()

parser = argparse.ArgumentParser(description='Create user with role Admin')
parser.add_argument('-l', '--login', type=str, help='Login')
parser.add_argument('-p', '--password', type=str, help='Password')
parser.add_argument('-u', '--user_id', type=int, help='Telegram user ID')
args = parser.parse_args()


def create_db_and_admin(login, password, user_id):
    initdb()
    try:
        db.add_new_role(login, password, 'Admin', user_id)
    except:
        print("Error. Can't add role")


if __name__ == '__main__':
    if args.login and args.password and args.user_id:
        create_db_and_admin(args.login, args.password, args.user_id)
    else:
        print("There is no arguments")
