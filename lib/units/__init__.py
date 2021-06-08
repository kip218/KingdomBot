from .scout import Scout
from .knight import Knight
from .archer import Archer
from .mage import Mage

MAP = {
         'Scout' : Scout(),
         'Knight' : Knight(),
         'Archer' : Archer(),
         'Mage' : Mage(),
        }
