class Unit():
    def __init__(self):
        self.name
        self.emoji
        self.cost
        self.dmg
        self.health
        self.max_hp
        self.speed
        self.gauge = 0

    def get_name(self):
        return self.name

    def get_emoji(self):
        return self.emoji

    def get_cost(self):
        return self.cost

    def get_dmg(self):
        return self.dmg

    def get_health(self):
        return self.health

    def get_max_hp(self):
        return self.max_hp

    def get_speed(self):
        return self.speed

    def get_gauge(self):
        return self.gauge

    def take_dmg(self, dmg):
        self.health -= dmg

    def gauge_full(self):
        return self.gauge >= 1

    def use_gauge(self):
        self.gauge -= 1

    def fill_gauge(self):
        self.gauge += self.speed
