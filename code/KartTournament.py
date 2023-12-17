from operator import attrgetter
from random import randrange

RM_PMX='PMX'
RM_OX1='OX1'

FIT_WEIGHT_SKILLDIFF=20

class KartTournament:
    """Object to represent a tournament, calculate its fitness and recombine it"""
    def __init__(self, playerproperties,parentTournament_A=None,parentTournament_B=None,recombinationMode=RM_PMX):
        self._playerproperties = playerproperties
        self._seatinglist=[]
        self._pairsize=[4,4,3] #todo determine pairsize from playerproperties
        self._pairings=[]
        self._fitness=999999
        if parentTournament_A == None or parentTournament_B == None:
            self.build_gene_from_scratch()
        elif recombinationMode==RM_PMX:
            self.build_from_PMX_crossover(parentTournament_A,parentTournament_B)
        elif recombinationMode==RM_OX1:
            self.build_from_OX1_crossover(parentTournament_A,parentTournament_B)

        self.determineFitness()


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
        """Fills the _pairings list with the tournament structure
                pairing {'teams':[] , pairing properties}
                    team: {'members':[], team properties}
                       member:{player_index}
                    """
        members=[]
        teams=[]
        for player_index in self._seatinglist:
            if len(members)>= self._pairsize[len(self._pairings)]: # current team is complete
                team = {'members': members}
                self.determine_team_skill(team)
                teams.append(team)
                members=[]
                if len(teams)>=2: # the pairing has two members
                    pairing={'teams':teams}
                    self.determine_pairing_skill_releation(pairing)
                    self._pairings.append(pairing)
                    teams=[]
            # place member in the current team
            team_member={'player_index':player_index}
            members.append(team_member)
        team = {'members': members}
        self.determine_team_skill(team)
        teams.append(team)
        pairing = {'teams': teams}
        self.determine_pairing_skill_releation(pairing)
        self._pairings.append(pairing)


    def determine_team_skill(self,team):
        skillsum=0
        for member in team['members']:
            playerproperty = self._playerproperties[member['player_index']]
            skillsum += playerproperty['skill']
        team['skillsum']=skillsum

    def determine_pairing_skill_releation(self,pairing):
        teams=pairing['teams']
        skilldiff=abs(teams[0]['skillsum']-teams[1]['skillsum'])
        pairing['skilldiff']=skilldiff

    def determineFitness(self):
        """Evaluates the tournament against all criteria and determines a fitness value
            the lower, the better"""
        pairingdiffsum=0
        for pairing in self._pairings:
            pairingdiffsum+=pairing['skilldiff']
        self._fitness=round(FIT_WEIGHT_SKILLDIFF/(1+pairingdiffsum),4)

    def print_pairings(self):
        for pairing in self._pairings:
            print ("vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv")
            teams=pairing['teams']
            for team_index,team in enumerate(pairing['teams']):
                if team_index>0:
                    print(f" --- ( {teams[0]['skillsum']}  )  [{pairing['skilldiff']}  ]  ({teams[1]['skillsum']})  ---")
                for team_member in team['members']:
                    playerproperty = self._playerproperties[team_member['player_index']]
                    print(f"{playerproperty['name']} ({playerproperty['skill']})")
            print ("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")

    def print_statistics(self):
        print("--------------------------------")
        print (f"Fitness {self._fitness}")
        for pairing in self._pairings:
            teams=pairing['teams']
            print(f"{len(teams[0]['members'])}({teams[0]['skillsum']})  \t[{pairing['skilldiff']}] \t{len(teams[1]['members'])}({teams[1]['skillsum']})")

# end of class KartTournament

g_playerproperties = [
    {'name':'Mario',          'skill': 1.25, 'location':'D'}
   ,{'name':'Luigi'         , 'skill': 1.25, 'location':'B'}
   ,{'name':'Bowser',         'skill': 1.25, 'location':'D'}
   ,{'name':'Princess Peach', 'skill': 1.25, 'location':'F'}
   ,{'name':'Rosalina',       'skill': 1.25, 'location':'B'}
   ,{'name':'Toad'          , 'skill': 1.00, 'location':'D'}
   ,{'name':'Daisy',          'skill': 1.00, 'location':'F'}
   ,{'name':'Link'          , 'skill': 1.00, 'location':'D'}
   ,{'name':'Wario',          'skill': 1.00, 'location':'B'}
   ,{'name':'Waluigi'       , 'skill': 1.00, 'location':'D'}
   ,{'name':'Bowser Jr',      'skill': 0.75, 'location':'F'}
   ,{'name':'Donkey Kong'   , 'skill': 0.75, 'location':'B'}
   ,{'name':'Diddy Kong',     'skill': 0.75, 'location':'D'}
   ,{'name':'Baby Mario'    , 'skill': 0.75, 'location':'B'}
   ,{'name':'Baby Daisy',     'skill': 0.75, 'location':'B'}
   ,{'name':'Baby Luigi'    , 'skill': 0.75, 'location':'B'}
   ,{'name':'Wiggler',        'skill': 1.25, 'location':'D'}
   ,{'name': 'Baby Peach',    'skill': 1.00, 'location':'F'}
   ,{'name':'King Boo',       'skill': 1.25, 'location':'B'}
   ,{'name': 'Baby Rosalina', 'skill': 1.00, 'location':'D'}
   ,{'name': 'Lakitu',        'skill': 1.00, 'location':'F'}
     ]

def singleTest():
    myFirstGame=KartTournament(g_playerproperties)
    myFirstGame.print_pairings()
    print(f"Fitness is {myFirstGame.getFitness()}")

def searchForOptimum():
    # create the initial population
    POPULATION_SIZE=100
    population=[]
    for tournament_index in range(0,POPULATION_SIZE):
        population.append(KartTournament(g_playerproperties))

    population.sort(key=attrgetter('_fitness'),reverse=True)
    for placing_index, tournament in enumerate (population) :
        tournament.print_statistics()



if __name__ == '__main__':
    #singleTest()
    searchForOptimum()

