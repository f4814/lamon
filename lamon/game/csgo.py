from game.source import source

class csgo(source):
    """ CS:GO game obejct """
    def __init__(self, config):
        self.name = "Counter Strike: Global Offensive"
        super().__init__(config)
