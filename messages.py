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


start_message = "Привет👋\nЭто бот для анонимного общения на английском языке\n\n" \
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

stop_1st_message = 'You had stopped the conversation..\nDo you want to /find new partner?'

stop_2nd_message = 'Partner has stopped the conversation..\nDo you want to /find new partner?'


MESSAGES = {
    "start": start_message,
    "help": help_message,
    "howto": howto_message,
    'current_state': current_state_message,
    'get': get_phrases_message,
    'match_1': match_1st_message,
    'match_2': match_2nd_message,
    'stop_1': stop_1st_message,
    'stop_2': stop_2nd_message,

}


