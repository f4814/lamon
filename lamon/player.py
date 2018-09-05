from datetime import datetime

class Player(object):
    """ A player and set of identities on the servers """
    def __init__(self, name):
        self.name = name
        self.scoreUpdates = []
        self.identities = {} # Key = gamename, val = nickname

    def addIdentity(self, identity):
        """
        Add a identity to the Player
        :param identity: Identity dict
        """
        self.identities.update(identity)

    def getName(self, gameName):
        """ Find the nickname in game """
        return self.identities[gameName]

    def getScore(self, gameNames=None):
        """
        Get the score of a player
        :param gameNames: List of games to read the score from. None is all
        :returns: Int score
        """
        if gameNames != None:
            relevant = filter(
                (lambda x: True if x.gameName in gameNames else False),
                gameNames)
        else:
            relevant = self.scoreUpdates

        score = 0
        for i in relevant:
            score += i.increase

        return score

    def addScore(self, points, gameName):
        """
        Add points to player.
        :param points: Int gained points
        :param gameName: Name of the game
        """
        update = ScoreUpdate(datetime.now(), gameName, points)
        self.scoreUpdates.append(update)

class ScoreUpdate(object):
    """ A player gaining or loosing points """
    def __init__(self, time, gameName, points):
        self.time = time
        self.gameName = gameName
        self.increase = points
