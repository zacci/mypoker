from pypokerengine.players import BasePokerPlayer
from pypokerengine.utils.card_utils import gen_cards, estimate_hole_card_win_rate
import random
import pprint
import pickle

class ZacciPlayer(BasePokerPlayer):

  # def __init__(self):
  #   BasePokerPlayer.__init__(self)
  #   self.round_count = 0
  debug = False
  
  def get_tree(self, round_state):
    hist = round_state['action_histories']
    game_string = "#"
    #pprint.pprint(round_state)
    for i in hist['preflop']:
      game_string = game_string + i['action'][0]
    if "flop" in hist and len(hist['flop']) > 0:
      for i in hist['flop']:
        game_string = game_string + i['action'][0]
    if "turn" in hist and len(hist['turn']) > 0:
      for i in hist['turn']:
        game_string = game_string + i['action'][0]
    if "river" in hist and len(hist['river']) > 0:
      for i in hist['river']:
        game_string = game_string + i['action'][0]
    return game_string
  
  def _myround(self,x, base=10):
    return int(base * round(float(x)/base))
  
  def evaluate_hs(self,round_state,hole_card):
    hole_cards = gen_cards(hole_card)
    community_cards = gen_cards(round_state['community_card'])
    hs = estimate_hole_card_win_rate(200,2, hole_cards,community_cards)
    percentile = self._myround(hs*100)
    return percentile

  def declare_action(self, valid_actions, hole_card, round_state):

    if (self.debug): print('------------DECLARING ACTION FOR ZACCI ---------------')
    if (self.debug): pprint.pprint(round_state)
    if (self.debug): pprint.pprint(valid_actions)
    tree = self.get_tree(round_state)
    sigma = pickle.load(open("strategy.pickle", "rb"))
    percentile = self.evaluate_hs(round_state, hole_card)
    if (self.debug): print("Percentile: " + str(percentile))
    if percentile not in sigma[tree]:
        if (min(100, percentile + 5) in sigma[tree]):
            percentile = (min(100, percentile + 5))
        elif (max(0, percentile - 5) in sigma[tree]):
            percentile = (max(0, percentile - 5))
        elif (min(100, percentile + 10) in sigma[tree]):
            percentile = (min(100, percentile + 10))
        elif (max(0, percentile - 10) in sigma[tree]):
            percentile = (max(0, percentile - 10))
        elif (min(100, percentile + 20) in sigma[tree]):
            percentile = (min(100, percentile + 20))
        elif (max(0, percentile - 20) in sigma[tree]):
            percentile = (max(0, percentile - 20))
        elif (min(100, percentile + 30) in sigma[tree]):
            percentile = (min(100, percentile + 30))
        elif (max(0, percentile - 30) in sigma[tree]):
            percentile = (max(0, percentile - 30))
        elif (min(100, percentile + 40) in sigma[tree]):
            percentile = (min(100, percentile + 40))
        elif (max(0, percentile - 40) in sigma[tree]):
            percentile = (max(0, percentile - 40))
        elif (min(100, percentile + 50) in sigma[tree]):
            percentile = (min(100, percentile + 50))
        elif (max(0, percentile - 50) in sigma[tree]):
            percentile = (max(0, percentile - 50))
    plist = []
    r = random.random()
    totalprob = 0.
    if (self.debug): print(str(r))
    for i in valid_actions:
      plist.append(sigma[tree][percentile][(i['action'])])
      if (self.debug): pprint.pprint(plist)
      totalprob += plist[-1]
      if (self.debug): print ("r = " + str(r) + ", total prob = " + str(totalprob))
      if r < totalprob:
        action = i['action']
        break
    if (self.debug): print("zacci taken action = " + action)
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
    if (self.debug): print("My ID (round result) : "+self.uuid)
    if (self.debug): pprint.pprint(round_state)
    if (self.debug): print("\n\n")
    # self.round_count = self.round_count + 1
    pass

def setup_ai():
  return ZacciPlayer()
