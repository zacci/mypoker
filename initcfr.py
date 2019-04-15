from pypokerengine.api.emulator import Emulator
from pypokerengine.utils.card_utils import gen_cards, estimate_hole_card_win_rate
from pypokerengine.utils.game_state_utils import restore_game_state, attach_hole_card_from_deck
from randomplayer import RandomPlayer
from cfrminimizer import CFRBase

import pprint

cfr = CFRBase()
cfr.run()

cfr.game_state = cfr.emulator.apply_action(cfr.game_state[0], 'call', 0)
pprint.pprint(cfr.game_state)

hole_cards = []
next_player_pos = cfr.game_state[0]["next_player"]
hole_cards.append(cfr.game_state[0]['table'].seats.players[next_player_pos].hole_card[0].__str__())
hole_cards.append(cfr.game_state[0]['table'].seats.players[next_player_pos].hole_card[1].__str__())
