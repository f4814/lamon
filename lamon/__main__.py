from time import sleep

from .core import Core

def printPlayers(p):
    for i in p:
        print(i.name + ' ' + str(i.getScore()))

if __name__ == "__main__":
    c = Core("config.yml")
    print("initialized")
    while True:
        sleep(10)
        with c.context.lock:
            printPlayers(c.context.players)
