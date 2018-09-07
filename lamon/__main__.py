from time import sleep

import core

def printPlayers(p):
    for i in p:
        print(i.name + ' ' + str(i.getScore()))

if __name__ == "__main__":
    c = core.Core("config.yml")
    print("initialized")
    while True:
        sleep(10)
        with c.context.lock:
            printPlayers(c.context.players)
