import click

@click.command()
@click.option('--host', default='127.0.0.1', help='Host to bind to')
@click.option('--port', default=5000, help='Webinterface port')
@click.option('--config', default='config.toml', help='Configuration file')
def main(host, port, config):
    from gevent.pywsgi import WSGIServer

    from lamon import create_app

    http_server = WSGIServer((host, port), create_app(config_file=config))
    http_server.serve_forever()
