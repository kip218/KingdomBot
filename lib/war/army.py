# from .. import units
# UNITS = units.MAP

UNITS = {
         'Scout' : Scout(),
         'Knight' : Knight(),
         'Archer' : Archer(),
         'Mage' : Mage(),
        }


class Army():
    def __init__(self, army):
        self.army = army


    def list_army(self):
        res = ''
        for unit in self.army:
            unit_name = unit[0]
            unit_count = int(unit[1])
            unit_emoji = UNITS[unit_name].get_emoji()
            res += f'{unit_emoji}`{unit_name}`       x {unit_count}\n'
        return res


a = Army([['Scout','2'], ['Mage','4']])
print(a.list_army())