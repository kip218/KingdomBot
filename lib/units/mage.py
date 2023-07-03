from .unit import Unit


class Mage(Unit):
    def __init__(self):
        self.name = "Mage"
        self.emoji = ":crystal_ball:"
        self.cost = 300
        self.dmg = 150
        self.max_hp = 150
        self.health = self.max_hp
        self.speed = 0.3
        self.gauge = 0
