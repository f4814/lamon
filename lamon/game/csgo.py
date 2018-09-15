from .source import Source

class CSGO(Source):
    """ CS:GO game obejct """
    def __init__(self, players, config):
        super().__init__(players, config)
        self.name = "CSGO"
        self.internalName = "Counter Strike: Global Offensive"
