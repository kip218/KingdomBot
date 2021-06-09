from copy import deepcopy
from random import choice
from .. import units
UNITS = units.MAP


class Army():
    def __init__(self, army):
        self.army = army
        self.full_army = []
        if self.army:
            for unit in self.army:
                unit_name = unit[0]
                unit_count = int(unit[1])
                for i in range(unit_count):
                    self.full_army.append(deepcopy(UNITS[unit_name]))

    def list_army(self):
        res = ''
        for unit in self.army:
            unit_name = unit[0]
            unit_count = int(unit[1])
            unit_emoji = UNITS[unit_name].get_emoji()
            res += f'{unit_emoji}`{unit_name}`   x {unit_count}\n'
        return res

    def army_state(self):
        res = ''
        for unit in self.full_army:
            name = unit.get_name()
            emoji = unit.get_emoji()
            health = unit.get_health()
            max_hp = unit.get_max_hp()
            res += f'{emoji}`{name}`   {health}/{max_hp}HP\n'
        if res:
            return res
        else:
            return ':skull::skull::skull::skull::skull:'

    def get_full_army(self):
        return self.full_army

    def army_empty(self):
        return not bool(self.full_army)

    def remove_dead(self):
        for i in range(len(self.full_army)-1,-1,-1):
            unit = self.full_army[i]
            if unit.get_health() <= 0:
                self.full_army.remove(unit)

    def attack(self, army):
        for unit in self.full_army:
            if unit.gauge_full():
                unit.use_gauge()
                target = choice(army.full_army)
                target.take_dmg(unit.get_dmg())

    def fill_gauge(self):
        for unit in self.full_army:
            unit.fill_gauge()
