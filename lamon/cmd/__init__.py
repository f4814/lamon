from .user import user_cli
from .role import role_cli
from .nick import nick_cli
from .game import game_cli

def register_cmds(app):
    app.cli.add_command(user_cli)
    app.cli.add_command(role_cli)
    app.cli.add_command(game_cli)
    app.cli.add_command(nick_cli)
