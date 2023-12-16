from random import randrange

RM_PMX='PMX'
RM_OX1='OX1'

class KartTournament:
    """Object to represent a tournament, calculate its fitness and recombine it"""
    def __init__(self, playerproperties,parentTournament_A=None,parentTournament_B=None,recombinationMode=RM_PMX):
        self._playerproperties = playerproperties
        self._seatinglist=[]
        self._pairsize=[4,4,3] #todo determine pairsize from playerproperties
        self._pairings=[]
        if parentTournament_A == None or parentTournament_B == None:
            self.build_gene_from_scratch()
        elif recombinationMode==RM_PMX:
            self.build_from_PMX_crossover(parentTournament_A,parentTournament_B)
        elif recombinationMode==RM_OX1:
            self.build_from_OX1_crossover(parentTournament_A,parentTournament_B)

    def build_gene_from_scratch(self):
        drawBowl=[]
        number_of_players = len(self._playerproperties)
        # seed the drawing bowl with all player numbers
        for player_index in range(0,number_of_players):
            drawBowl.append(player_index)

        # draw all players randomly from bowl to the seating
        while len(drawBowl)>0:
            lady_luck=randrange(0,len(drawBowl))
            self._seatinglist.append(drawBowl[lady_luck])
            drawBowl.pop(lady_luck)
        self.deriveTournamentStructure()

    def deriveTournamentStructure(self):
        paired_teams=[]
        team_seats = []
        for player_index in self._seatinglist:
            if len(team_seats)>= self._pairsize[len(self._pairings)]: # current team is complete
                paired_teams.append(team_seats)
                team_seats=[]
                if len(paired_teams)>=2: # the pairing has two members
                    self._pairings.append(paired_teams)
                    paired_teams=[]
            # place member in the current team
            team_member={'player_index':player_index}
            team_seats.append(team_member)
        paired_teams.append(team_seats)
        self._pairings.append(paired_teams)

    def print_pairings(self):
        for paired_teams in self._pairings:
            print (">>>>>>>>>>>>>>>>>>>>>>>>>>>")
            for team_index,team_seats in enumerate(paired_teams):
                if team_index>0:
                    print("       vs             ")
                for team_member in team_seats:
                    playerproperty = self._playerproperties[team_member['player_index']]
                    print(f"{playerproperty['name']} ({playerproperty['skill']})")
            print ("<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
# end of class KartTournament

playerproperties = [{'name':'Mario',      'skill':1.25},{'name':'Luigi'         , 'skill':1.25}
                    ,{'name':'Bowser',    'skill':1.25},{'name':'Princess Peach', 'skill':1.25}
                    ,{'name':'Rosalina',  'skill':1.25},{'name':'Toad'          , 'skill':1.00}
                    ,{'name':'Daisy',     'skill':1.00},{'name':'Link'          , 'skill':1.00}
                    ,{'name':'Wario',     'skill':1.00},{'name':'Waluigi'       , 'skill':1.00}
                    ,{'name':'Bowser Jr', 'skill':0.75},{'name':'Donkey Kong'   , 'skill':0.75}
                    ,{'name':'Diddy Kong','skill':0.75},{'name':'Baby Mario'    , 'skill':0.75}
                    ,{'name':'Baby Daisy','skill':0.75},{'name':'Baby Luigi'    , 'skill':0.75}
                    ,{'name':'Wiggler','skill': 1.25}, {'name': 'Baby Peach', 'skill': 1.00}
                    ,{'name':'King Boo','skill': 1.25}, {'name': 'Baby Rosalina', 'skill': 1.00}
                    , {'name': 'Lakitu', 'skill': 1.00}
                    ]

if __name__ == '__main__':
    myFirstGame=KartTournament(playerproperties)
    myFirstGame.print_pairings()

