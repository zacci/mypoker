import pickle
import pprint
import datetime
from pypokerengine.utils.card_utils import gen_cards, estimate_hole_card_win_rate
from pypokerengine.utils.game_state_utils import restore_game_state, attach_hole_card_from_deck
from randomplayer import RandomPlayer
from pypokerengine.api.emulator import Emulator

class CFRBase:

    def __init__(self):
        self.emulator = Emulator()
        #try:
        self._sigma = pickle.load(open("strategy.pickle", "rb"))
        #except (OSError, IOError, EOFError) as e:
            #self._sigma = {}
            #pickle.dump(self._sigma, open("strategy.pickle", "wb"))

        self.cumulative_regrets = {}
        self.cumulative_sigma = {}


    def get_tree(self,game_state):
        if game_state[1][-1]['type'] != 'event_game_finish':
            hist = game_state[1][-1]['round_state']['action_histories']
            game_string = "#"
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
        else:
            hist = game_state[1][0]['round_state']['action_histories']
            game_string = "#"
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
        
    def is_terminal(self,game_state):
        return game_state[1][-1]['type'] == 'event_game_finish'

    def state_evaluation(self,game_state):
        return game_state[1][1]['players'][1]['stack'] - 1000

    def _available_actions(self,game_state):
        actions = []
        for i in game_state[1][-1]['valid_actions']:
            actions.append(i['action'])
        return actions

    def load_data(self):
        with open('strategy.pickle','rb') as handle:
            self._sigma = pickle.load(handle)

    def store_data(self):
        with open('strategy.pickle', 'wb') as handle:
            pickle.dump(self._sigma, handle, protocol=pickle.HIGHEST_PROTOCOL)

    def getsigma(self, game_state, percentile, action):
        tree = self.get_tree(game_state)
        available_actions = self._available_actions(game_state)
        if tree not in self._sigma:
            self._sigma[tree] = {percentile:{}}
            for i in available_actions:
                self._sigma[tree][percentile][i] = 1./len(available_actions)
        elif percentile not in self._sigma[tree]:
            self._sigma[tree][percentile] = {}
            for i in available_actions:
                self._sigma[tree][percentile][i] = 1./len(available_actions)
        return self._sigma[tree][percentile][action]

    def _statetomove(self,game_state):
        next_player_pos = game_state[0]["next_player"]
        if next_player_pos == 1:
            return 1
        else:
            return -1
        
    def _getcards(self,game_state):
        hole_cards = []
        next_player_pos = game_state[0]["next_player"]
        hole_cards.append(game_state[0]['table'].seats.players[next_player_pos].hole_card[0].__str__())
        hole_cards.append(game_state[0]['table'].seats.players[next_player_pos].hole_card[1].__str__())
        return hole_cards

    def _getboard(self,game_state):
        return game_state[0]['table']._community_card

    def _myround(self,x, base=10):
        return int(base * round(float(x)/base))

    def evaluate_hs(self,game_state):
        #print('evaluating hs')
        hole_cards = gen_cards(self._getcards(game_state))
        #print('hole cards = ' + str(self._getcards(game_state)))
        community_cards = self._getboard(game_state)
        #print('community = ' + str(self._getboard(game_state)))
        hs = estimate_hole_card_win_rate(100,2, hole_cards,community_cards)
        #print('hs = ' + str(hs))
        percentile = self._myround(hs*100)
        return percentile

    def _state_play(self, game_state, action):
        new_game_state = self.emulator.apply_action(game_state[0], action, 0)
        return new_game_state

    def utility_recursive(self):
        final_value = self._utility_recursive(self.game_state,1,1)
        #print("##################CUMULATIVE REGRETS#####################")
        #pprint.pprint(self.cumulative_regrets)
        #print("##################CUMULATIVE SIGMA#####################")
        #pprint.pprint(self.cumulative_sigma)
        return final_value

    def _cumulate_cfr_regret(self, game_state, percentile, action, regret):
        tree = self.get_tree(game_state)
        available_actions = self._available_actions(game_state)
        if tree not in self.cumulative_regrets:
            self.cumulative_regrets[tree] = {percentile:{}}
            for i in available_actions:
                self.cumulative_regrets[tree][percentile][i] = 0
        elif percentile not in self.cumulative_regrets[tree]:
            self.cumulative_regrets[tree][percentile] = {}
            for i in available_actions:
                self.cumulative_regrets[tree][percentile][i] = 0      
        self.cumulative_regrets[tree][percentile][action] += regret

    def _cumulate_sigma(self, game_state, percentile, action, prob):
        tree = self.get_tree(game_state)
        available_actions = self._available_actions(game_state)
        if tree not in self.cumulative_sigma:
            self.cumulative_sigma[tree] = {percentile:{}}
            for i in available_actions:
                self.cumulative_sigma[tree][percentile][i] = 0
        elif percentile not in self.cumulative_sigma[tree]:
            self.cumulative_sigma[tree][percentile] = {}
            for i in available_actions:
                self.cumulative_sigma[tree][percentile][i] = 0      
        self.cumulative_sigma[tree][percentile][action] += prob

    def __update_sigma_recursively(self, game_state):
        # stop traversal at terminal node
        if self.is_terminal(game_state):
            return
        percentile = self.evaluate_hs(game_state)
        self._update_sigma(game_state,percentile)
        # go to subtrees
        for action in self._available_actions(game_state):
            self.__update_sigma_recursively(self._state_play(game_state,action))

    def _update_sigma(self, game_state, percentile):
        tree = self.get_tree(game_state)
        #print("Current State--------")
        #print(self.get_tree(game_state))
        #print(percentile)
        #if percentile not in self._sigma[tree]:
        #    percentile = (min(100, percentile + 5)) if (min(100, percentile + 5) in self._sigma[tree]) else (max(0, percentile - 5))
        if percentile not in self.cumulative_regrets[tree]:
            #print('Enter unable to find percentile')
            if (min(100, percentile + 5) in self.cumulative_regrets[tree]):
                percentile = (min(100, percentile + 5))
            elif (max(0, percentile - 5) in self.cumulative_regrets[tree]):
                percentile = (max(0, percentile - 5))
            elif (min(100, percentile + 10) in self.cumulative_regrets[tree]):
                percentile = (min(100, percentile + 10))
            elif (max(0, percentile - 10) in self.cumulative_regrets[tree]):
                percentile = (max(0, percentile - 10))
            elif (min(100, percentile + 20) in self.cumulative_regrets[tree]):
                percentile = (min(100, percentile + 20))
            elif (max(0, percentile - 20) in self.cumulative_regrets[tree]):
                percentile = (max(0, percentile - 20))
            elif (min(100, percentile + 30) in self.cumulative_regrets[tree]):
                percentile = (min(100, percentile + 30))
            elif (max(0, percentile - 30) in self.cumulative_regrets[tree]):
                percentile = (max(0, percentile - 30))
            elif (min(100, percentile + 40) in self.cumulative_regrets[tree]):
                percentile = (min(100, percentile + 40))
            elif (max(0, percentile - 40) in self.cumulative_regrets[tree]):
                percentile = (max(0, percentile - 40))
            elif (min(100, percentile + 50) in self.cumulative_regrets[tree]):
                percentile = (min(100, percentile + 50))
            elif (max(0, percentile - 50) in self.cumulative_regrets[tree]):
                percentile = (max(0, percentile - 50))
        #print('New Percentile = ' + str(percentile))
        rgrt_sum = sum(filter(lambda x : x > 0, self.cumulative_regrets[tree][percentile].values()))
        nr_of_actions = len(self.cumulative_regrets[tree][percentile].keys())
        for a in self.cumulative_regrets[tree][percentile]:        
            self._sigma[tree][percentile][a] = max(self.cumulative_regrets[tree][percentile][a], 0.) / rgrt_sum if rgrt_sum > 0 else 1. / nr_of_actions        
        
    def _utility_recursive(self,game_state, reach_sb, reach_bb):


        children_states_utilities = {}
        if self.is_terminal(game_state):
            return self.state_evaluation(game_state)
        percentile = self.evaluate_hs(game_state)
        #print("Current State--------")
        #print(self.get_tree(game_state))
        #print(percentile)
        #pprint.pprint(game_state[1][-1]['round_state']['community_card'])
        value = 0.

        for action in self._available_actions(game_state):
            probability = self.getsigma(game_state,percentile,action)
            child_reach_sb = reach_sb * ( probability if self._statetomove(game_state) == 1 else 1)
            child_reach_bb = reach_bb * ( probability if self._statetomove(game_state) == -1 else 1)

            child_state_utility = self._utility_recursive(self._state_play(game_state,action),reach_sb,reach_bb)

            value +=  (probability * child_state_utility)
            
            children_states_utilities[action] = child_state_utility
            
        (cfr_reach, reach) = (reach_bb, reach_sb) if self._statetomove(game_state) == 1 else (reach_sb, reach_bb)

        for action in self._available_actions(game_state):

            action_cfr_regret = self._statetomove(game_state) * cfr_reach * (children_states_utilities[action] - value)

            self._cumulate_cfr_regret(game_state, percentile, action, action_cfr_regret)
            self._cumulate_sigma(game_state, percentile, action, reach * self.getsigma(game_state,percentile,action))
        return value

    def run(self, iterations = 1):
        print(datetime.datetime.now())
        for myiter in range(0, iterations):
            #initialize new game state with new hole cards
            self.emulator.set_game_rule(player_num=2, max_round=1, small_blind_amount=10, ante_amount=0)
            players_info = {
                "uuid-1": { "name": "player1", "stack": 1000 },
                "uuid-2": { "name": "player2", "stack": 1000 }
            }
            player1 = RandomPlayer()
            player2 = RandomPlayer()
            self.emulator.register_player('uuid-1',player1)
            self.emulator.register_player('uuid-2',player2)
            initial_state = self.emulator.generate_initial_game_state(players_info)
            self.game_state = self.emulator.start_new_round(initial_state)
            #goto later gamestate
            #self.game_state = self.emulator.apply_action(self.game_state[0], 'call', 0)



            
            self._utility_recursive(self.game_state, 1, 1)
            self.__update_sigma_recursively(self.game_state)

            
            self.store_data()
            print('data stored,  i = ' + str(myiter) )
            print(datetime.datetime.now())
        print(datetime.datetime.now())
