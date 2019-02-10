from .user import user_cli
from .role import role_cli
from .nick import nick_cli
from .userwatcher import userwatcher_cli
from .game import game_cli
from .gamewatcher import gamewatcher_cli

def register_cmds(app):
    app.cli.add_command(user_cli)
    app.cli.add_command(userwatcher_cli)
    app.cli.add_command(role_cli)
    app.cli.add_command(game_cli)
    app.cli.add_command(gamewatcher_cli)
    app.cli.add_command(nick_cli)
