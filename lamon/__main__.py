import core
from time import sleep
from game.ttt import TTT
from player import Player

import yaml

def printPlayers(p):
    for i in p:
        print (i.name + ' ' + str(i.getScore()))

if __name__ == "__main__":
    with open("config.yml", 'r') as cfg:
        config = yaml.load(cfg)

    players = []
    for p in config['players']:
        player = Player(config['players'][p]['name'])
        for i in config['players'][p]['nicks']:
            nick = config['players'][p]['nicks'][i]
            game = i
            player.addIdentity({game: nick})
        players.append(player)

    g = TTT({'ip': 'lexodexo.de', 'port': 27015})
    g.connect()
    while True:
        try:
            g.updatePlayerScores(players)
        except:
            print ("Connection lost")
        printPlayers(players)
        sleep(10)
    g.close()

