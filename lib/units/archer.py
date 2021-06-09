from .unit import Unit

class Archer(Unit):
    def __init__(self):
        self.name = 'Archer'
        self.emoji = ':bow_and_arrow:'
        self.cost = 150
        self.dmg = 100
        self.max_hp =50
        self.health = self.max_hp
        self.speed = 0.5
        self.gauge = 0