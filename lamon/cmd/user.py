import click
from flask import current_app
from flask.cli import AppGroup

from lamon.models import User, Role, Game
from lamon import db

user_cli = AppGroup('user')

@user_cli.command('create')
@click.argument('name')
@click.argument('password')
@click.option('--roles', help='Roles of the new user. Comma seperated.')
def create_user(name, password, roles=None):
    user = User(username=name, password=current_app.user_manager.hash_password(password))

    if roles:
        for role in roles.split(','):
            user.roles.append(Role(name=role))

    db.session.add(user)
    db.session.commit()

@user_cli.command('remove')
@click.argument('name')
def remove_user(name):
    query = db.session.query(User).filter(User.username == name)
    user = query.one()
    db.session.delete(user)
    db.session.commit()

@user_cli.command('change_username')
@click.argument('old_name')
@click.argument('new_name')
def change_user(old_name, new_name):
    query = db.session.query(User).filter(User.username == old_name)
    user = query.one()
    user.username = new_name
    db.session.commit()

@user_cli.command('add_role')
@click.argument('name')
@click.argument('role')
def add_role_user(name, role):
    queryUser = db.session.query(User).filter(User.username == name)
    queryRole = db.session.query(Role).filter(Role.name == role)

    user = queryUser.one()
    role = queryRole.one()

    user.roles.append(role)
    db.session.commit()

@user_cli.command('remove_role')
@click.argument('name')
@click.argument('role')
def remove_role_user(name, role):
    queryUser = db.session.query(User).filter(User.username == name)
    queryRole = db.session.query(Role).filter(Role.name == role)

    user = queryUser.one()
    role = queryRole.one()

    user.roles.remove(role)
    db.session.commit()

