from pypokerengine.players import BasePokerPlayer
from pypokerengine.utils.card_utils import gen_cards, estimate_hole_card_win_rate
import random as rand
import pprint

class ZacciPlayer(BasePokerPlayer):

  # def __init__(self):
  #   BasePokerPlayer.__init__(self)
  #   self.round_count = 0

  def get_tree(self, round_state):
    hist = round_state['action_histories']
    game_string = "#"
    #pprint.pprint(round_state)
    for i in hist['preflop']:
      game_string = game_string + i['action'][0]
    game_string = game_string + '/'
    if "flop" in hist and len(hist['flop']) > 0:
      for i in hist['flop']:
        game_string = game_string + i['action'][0]
      game_string = game_string + '/'
    if "turn" in hist and len(hist['turn']) > 0:
      for i in hist['turn']:
        game_string = game_string + i['action'][0]
      game_string = game_string + '/'
    if "river" in hist and len(hist['river']) > 0:
      for i in hist['river']:
        game_string = game_string + i['action'][0]
      game_string = game_string + '/'      
    return game_string
  
  def evaluate_hs(self,game_state):
    hole_cards = gen_cards(self._getcards(game_state))
    community_cards = self._getboard(game_state)
    hs = estimate_hole_card_win_rate(100,2, hole_cards,community_cards)
    percentile = self._myround(hs*100)
    return percentile

  def declare_action(self, valid_actions, hole_card, round_state):
    
    pprint.pprint(round_state)
    tree = self.get_tree(round_state)
    sigma = pickle.load(open("strategy.pickle", "rb"))
    r = rand.random()
    plist = []
    for action in valid_actions:
      plist.append
      
    return action  # action returned here is sent to the poker engine

  def receive_game_start_message(self, game_info):
    # print("\n\n")
    # pprint.pprint(game_info)
    # print("---------------------------------------------------------------------")
    pass

  def receive_round_start_message(self, round_count, hole_card, seats):
    # print("My ID : "+self.uuid+", round count : "+str(round_count)+", hole card : "+str(hole_card))
    # pprint.pprint(seats)
    pass

  def receive_street_start_message(self, street, round_state):
    pass

  def receive_game_update_message(self, action, round_state):
    pass

  def receive_round_result_message(self, winners, hand_info, round_state):
    # print("My ID (round result) : "+self.uuid)
    # pprint.pprint(round_state)
    # print("\n\n")
    # self.round_count = self.round_count + 1
    print("Zacci Player")
    pass

def setup_ai():
  return ZacciPlayer()
