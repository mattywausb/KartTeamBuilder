from random import randrange

RM_PMX='PMX'
RM_OX1='OX1'

class KartTournament:
    """Object to represent a tournament, calculate its fitness and recombine it"""
    def __init__(self, playerproperties,parentTournament_A=None,parentTournament_B=None,recombinationMode=RM_PMX):
        self._playerproperties = playerproperties
        self._seatinglist=[]
        self._seatstructure=[]
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
    def print_seating(self):
        for player_index in self._seatinglist:
            playerproperty = self._playerproperties[player_index]
            print(f"{playerproperty['name']} ({playerproperty['skill']})")
# end of class KartTournament

playerproperties = [{'name':'Mario',      'skill':1.25},{'name':'Luigi'         , 'skill':1.25}
                    ,{'name':'Bowser',    'skill':1.25},{'name':'Princess Peach', 'skill':1.25}
                    ,{'name':'Rosalina',  'skill':1.25},{'name':'Toad'          , 'skill':1.00}
                    ,{'name':'Daisy',     'skill':1.00},{'name':'Link'          , 'skill':1.00}
                    ,{'name':'Wario',     'skill':1.00},{'name':'Waluigi'       , 'skill':1.00}
                    ,{'name':'Bowser Jr', 'skill':0.75},{'name':'Donkey Kong'   , 'skill':0.75}
                    ,{'name':'Diddy Kong','skill':0.75},{'name':'Baby Mario'    , 'skill':0.75}
                    ,{'name':'Baby Daisy','skill':0.75},{'name':'Baby Luigi'    , 'skill':0.75}
]

if __name__ == '__main__':
    myFirstGame=KartTournament(playerproperties)
    myFirstGame.print_seating()

