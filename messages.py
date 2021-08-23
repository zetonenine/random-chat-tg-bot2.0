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
                "/help  —  всё что нужно знать о боте\n" \
                "/howto  —  правила использовавния\n" \
                "/find  —  найти своего собеседника"

help_message = "Что важно знать:\n\n" \
               "1. Бот сделан для практики английского языка и преодоления разговорного барьера.\n" \
               "2. Бот соединяет тебя со случайным пользователем, " \
               "и вы анонимно общаетесь с помощью голосовых сообщений.\n" \
               "3. Общение происходит ТОЛЬКО на английском языке, " \
               "если собеседник не соблюдает это правило, советую сменить собеседника.\n" \
               "4. Чтобы узнать как практиковаться максимально эффективно нажми на команду - /howto.\n"

howto_message = "Несколько правил для эффективности:\n\n" \
                "1. Если твой уровень английского ниже intermediate, то бот для тебя будет бесполезным. Увы :(\n" \
                "2. Общаясь, забудь про русский язык.\n" \
                "3. Задавай больше вопросов собеседнику.\n" \
                "4. Будь краток.\n" \
                "5. Не помнишь слово на английском, ищи синонимы или изложи мысль другим способом.\n" \
                "6. Не понимаешь что сказал собеседник, попроси повторить или объяснить.\n" \
                "7. Совсем-совсем забудь про русский язык.\n" \
                "8. Нажми /get, чтобы воспользоваться шпаргалкой.\n\n" \
                "Нажми /find, для поиска собеседника"

get_phrases_message = "Переспросить:\n" \
                      "What was that? / (Sorry,) say it again / What is ..(слово)? / I didn’t catch that " \
                      "/ I can’t hear you very well \n\n" \
                      "Выразить непонимание:\n" \
                      "I didn’t get that / (Sorry,) I've lost you\n\n" \
                      "Еще фразы:"

current_state_message = 'Текущее состояние - "{current_state}", что удовлетворяет условию "один из {states}"'

match_1st_message = ('Match! Your partner is <b>{0}</b>\nWho will speak first? :)'.format(random.choice(NAMES)))

match_2nd_message = 'Match! Your partner is <b>{0}</b>\nWho will speak first? :)'.format(random.choice(NAMES))

no_partner_message = 'Unfortunately, all users are already busy. Try again'

sure_stop_chat = 'Are you sure you want to end the conversation? Write <b>yep</b> to the chat'

stop_1st_message = 'You had stopped the conversation..\nDo you want to /find new partner?'

stop_2nd_message = 'Partner has stopped the conversation..\nDo you want to /find new partner?'

editor_mode_main = 'Enter login and password:'

editor_menu = 'You entered editor mode. What are you going to do?\n/show_banners\n/add_new_banner\n/del_banner\n/quit'

log_in_success = 'Welcome home!'

log_in_unsuccess = "Wrong login or password"

stop_editor_mode = 'You logged out from editor mode'

empty_banners = "There is no commercials"

send_new_banner = "Send new commercial text"

banner_was_added = "New commercial was added successfully"

banner_was_not_added = "New commercial wasn't added"

choose_banner_to_del = 'Write banners id to remove'

error_id = "An error occurred when specifying an identifier. Try again: write just ID"

banner_was_delete = "Commercial was removed successfully. ID "

banner_was_not_delete = "No commercial with ID "

MESSAGES = {
    "start": start_message,
    "help": help_message,
    "howto": howto_message,
    'current_state': current_state_message,
    'get': get_phrases_message,
    'match_1': match_1st_message,
    'match_2': match_2nd_message,
    'no_partner_message': no_partner_message,
    'stop_1': stop_1st_message,
    'stop_2': stop_2nd_message,
    'sure_stop_chat': sure_stop_chat,
    'editor_mode': editor_mode_main,
    'editor_menu': editor_menu,
    'log_in_success': log_in_success,
    'log_in_unsuccess': log_in_unsuccess,
    'empty_banners': empty_banners,
    'stop_editor_mode': stop_editor_mode,
    'choose_banner_to_del': choose_banner_to_del,
    'error_id': error_id,
    'banner_was_added': banner_was_added,
    'banner_was_not_added': banner_was_not_added,
    'banner_was_delete': banner_was_delete,
    'banner_was_not_delete': banner_was_not_delete,
    'send_new_banner': send_new_banner,

}



