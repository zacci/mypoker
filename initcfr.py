from pypokerengine.api.emulator import Emulator
from pypokerengine.utils.card_utils import gen_cards, estimate_hole_card_win_rate
from pypokerengine.utils.game_state_utils import restore_game_state, attach_hole_card_from_deck
from randomplayer import RandomPlayer
from cfrminimizer import CFRBase

import pprint



cfr = CFRBase()
cfr._utility_recursive()
