from .unit import Unit


class Knight(Unit):
    def __init__(self):
        self.name = "Knight"
        self.emoji = ":crossed_swords:"
        self.cost = 150
        self.dmg = 50
        self.max_hp = 100
        self.health = self.max_hp
        self.speed = 0.5
        self.gauge = 0
