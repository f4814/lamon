from time import sleep
import multiprocessing

from .core import Core

def printPlayers(p):
    for i in p:
        print(i.name + ' ' + str(i.getScore()))

if __name__ == "__main__":
    c = Core("config.yml")
    server = multiprocessing.Process(target=c.server.serve_forever,
                                     name='server',
                                     args=(('', 5000),))
    server.start()
    print("initialized")
    while True:
        sleep(10)
