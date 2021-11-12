import random

NAMES = (
    "Hedgehog 🦔",
    "Squirrel 🐿",
    "Raccoon 🦡",
    "Parrot 🦜",
    "Bunny 🐇",
    "Lama 🦙",
    "Kangaroo 🦘",
    "Whale 🐋",
    "Crayfish 🦞",
    "Owl 🦉",
    "Duck 🦆",
    "Ladybug 🐞",
    "Unicorn 🦄",
    "Eagle 🦅",
    "Bee 🐝",
    "Dino 🦖",
    "Boa 🐍",
    "Lizard 🦎",
    "Bug 🐛",
    "Turtle 🐢",
    "Snail 🐌",
    "Wolf 🐺",
    "Ant 🐜",
    "Dove 🐦",
    "Monkey 🐒",
    "Camel 🐫",
    "Zebra 🦓",
    "Gorilla 🦍",
    "Crab 🦀",
    "Goat 🐐",
    "Kitty 🐈",
    "Doggy 🐕",
)


start_message = "Привет-привет👋\nЭто бот для анонимного общения на английском языке\n\n" \
                "/what  —  всё что нужно знать о боте\n" \
                "/find  —  найти своего собеседника"

what_message = "Что важно знать:\n\n" \
               "1. Бот даёт практику разговорного английского языка и помогает преодолеть разговорный барьер.\n" \
               "2. Бот соединяет тебя со случайным пользователем, вы общаетесь только голосовыми сообщениями.\n" \
               "3. Общение полностью анонимно. Собеседник не знает тебя, ты ничего не знаешь про него.\n" \
               "4. Общение происходит ТОЛЬКО на английском языке, " \
               "если собеседник не следует правилу, советую сменить собеседника.\n" \
               "5. Относись с уважением к другим, и расскажи о неуважительном отношении с помощью report.\n" \
               "6. Полезные шпаргалки по команде /help.\n"

help_message = "Переспросить:\n" \
                  "What was that? / (Sorry,) say it again / What is ..(слово)? / I didn’t catch that " \
                  "/ I can’t hear you very well \n\n" \
                  "Выразить непонимание:\n" \
                  "I didn’t get that / (Sorry,) I've lost you\n\n" \
                  "Еще фразы:"

current_state_message = 'Текущее состояние - "{current_state}", что удовлетворяет условию "один из {states}"'

match_1st_message = 'Match! Your partner is <b>{0}</b>\nWho will speak first? :)'.format(random.choice(NAMES))

match_2nd_message = 'Match! Your partner is <b>{0}</b>\nWho will speak first? :)'.format(random.choice(NAMES))

no_partner_message = 'Unfortunately, all users are already busy 🤷‍♀️ Try again'

stop_searching = 'User search cancel. If you want try again, press /find'

sure_stop_chat = 'Are you sure you want to end the conversation? Write <b>yep</b> to the chat'

continue_chat = 'Cancel completion. You still have a companion 🤝'

report_accepted = 'Your report has been accepted. Thank you for making the community a better place.'

report_explain = 'To submit a report, select message,  text command /report.'

stop_1st_message = 'You had stopped the conversation..\nDo you want to /find new partner?'

stop_2nd_message = 'Partner has stopped the conversation..\nDo you want to /find new partner?'

editor_mode_main = 'Enter login and password:'

editor_menu = 'You entered editor mode. What are you going to do?\n' \
              '/show_banners\n/add_new_banner\n/del_banner\n/add_role\n' \
              '/del_role\n/last_bans\n/get_ban\n/quit'

log_in_success = 'Welcome home!'

log_in_unsuccess = "Wrong login or password"

stop_editor_mode = 'You logged out from editor mode'

stop_moderator_mode = 'You logged out from moderator mode'

empty_banners = "There is no commercials"

send_new_banner = "Send new commercial text"

banner_was_added = "New commercial was added successfully"

banner_was_not_added = "New commercial wasn't added"

choose_banner_to_del = 'Write banners id to remove'

error_id = "An error occurred when specifying an identifier. Try again: write just ID"

banner_was_delete = "Commercial was removed successfully. ID "

banner_was_not_delete = "No commercial with ID "

add_new_role = 'To add new role, send me: login, password, role'

role_was_added = 'New role was added'

role_wasnt_added = 'Something going wrong, try again'

choose_role_to_del = 'Choose role id to delete:'

no_roles_to_del = 'There is no roles to delete'

role_was_deleted = 'Role was deleted successfully'

role_wasnt_deleted = "Role wasn't deleted"

moderator_menu = 'You entered editor mode. What are you going to do?\n/reports\n/quit\n'

choose_messages_to_check = 'Choose reports messages to check:'

messages_of_reports = 'That report include messages:'

choose_punishment = 'Choose punishment or scroll up to check other reports'

ban_user_answer = 'You were banned for not following the rules for using the bot. Date of unban: '


MESSAGES = {
    "start": start_message,
    "what": what_message,
    "help": help_message,
    'current_state': current_state_message,
    'match_1': match_1st_message,
    'match_2': match_2nd_message,
    'no_partner_message': no_partner_message,
    'stop_searching': stop_searching,
    'report_accepted': report_accepted,
    'report_explain': report_explain,
    'stop_1': stop_1st_message,
    'stop_2': stop_2nd_message,
    'sure_stop_chat': sure_stop_chat,
    'continue_chat': continue_chat,
    'editor_mode': editor_mode_main,
    'editor_menu': editor_menu,
    'log_in_success': log_in_success,
    'log_in_unsuccess': log_in_unsuccess,
    'empty_banners': empty_banners,
    'stop_editor_mode': stop_editor_mode,
    'stop_moderator_mode': stop_moderator_mode,
    'choose_banner_to_del': choose_banner_to_del,
    'error_id': error_id,
    'banner_was_added': banner_was_added,
    'banner_was_not_added': banner_was_not_added,
    'banner_was_delete': banner_was_delete,
    'banner_was_not_delete': banner_was_not_delete,
    'send_new_banner': send_new_banner,
    'add_new_role': add_new_role,
    'role_was_added': role_was_added,
    'role_wasnt_added': role_wasnt_added,
    'choose_role_to_del': choose_role_to_del,
    'no_roles_to_del': no_roles_to_del,
    'role_was_deleted': role_was_deleted,
    'role_wasnt_deleted': role_wasnt_deleted,
    'moderator_menu': moderator_menu,
    'choose_messages_to_check': choose_messages_to_check,
    'messages_of_reports': messages_of_reports,
    'choose_punishment': choose_punishment,
    'ban_user_answer': ban_user_answer,
}



