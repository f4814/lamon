import click
from flask import current_app
from flask.cli import AppGroup

from lamon.models import Role
from lamon import db

role_cli = AppGroup('role')

@role_cli.command('create')
@click.argument('name')
def create_role(name):
    db.session.add(Role(name=name))
    db.session.commit()

@role_cli.command('remove')
@click.argument('name')
def remove_role(name):
    query = db.session.query(Role).filter(Role.name == name)
    role = query.one()
    db.session.delete(role)
    db.session.commit()

@role_cli.command('change')
@click.argument('old_name')
@click.argument('new_name')
def change_role(old_name, new_name):
    query = db.session.query(Role).filter(Role.name == old_name)
    role = query.one()
    role.name = new_name
    db.session.commit()
