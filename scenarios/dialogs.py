from dialogic import COMMANDS
from dialogic.cascade import DialogTurn

from dm import csc
from scenarios.synonym_finder import make_synonym_response

from my_data import data


def is_single_pass(turn: DialogTurn) -> bool:
    """ Check that a command is passed when the skill is activated """
    if not turn.ctx.yandex:
        return False
    if not turn.ctx.yandex.session.new:
        return False
    return bool(turn.ctx.yandex.request.command)


def is_new_session(turn: DialogTurn):
    return turn.ctx.session_is_new() or not turn.text


@csc.add_handler(priority=100, checker=is_single_pass)
def single_pass(turn: DialogTurn):
    make_synonym_response(turn)
    turn.commands.append(COMMANDS.EXIT)


@csc.add_handler(priority=10, regexp='(hello|hi|привет|здравствуй)')
@csc.add_handler(priority=3, checker=is_new_session)
@csc.add_handler(priority=0)  # use it as a fallback scenario
def hello(turn: DialogTurn):
    turn.response_text = 'Привет! Вы в навыке «Мой почтальон». Я могу отправлять сообщения в телеграмм определённому ' \
                         'контакту. Сообщение будет доставлять связанный с навыком бот, но для этого он должен ' \
                         'знать id (уникальный номер) чата с получателем сообщения. ' + data.help_text
    turn.suggests.append('выход')


@csc.add_handler(priority=10, intents=['help', 'Yandex.HELP', 'like_alice'])
def do_help(turn: DialogTurn):
    turn.response_text = data.help_text + 'Чтобы выйти, скажите "хватит".'
    turn.suggests.append('выход')


@csc.add_handler(priority=10, intents=['total_exit'])
def total_exit(turn: DialogTurn):
    turn.response_text = 'Было приятно пообщаться! ' \
                         'Чтобы обратиться ко мне снова, ' \
                         'запустите навык "Мой почтальон".'
    turn.commands.append(COMMANDS.EXIT)


@csc.add_handler(priority=1)
def find_synonym_fallback(turn: DialogTurn):
    if not turn.text:
        return
    make_synonym_response(turn)


@csc.add_handler(priority=10, intents=['send_message'])
def send_message(turn: DialogTurn):
