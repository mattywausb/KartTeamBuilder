import json
import random
from math import ceil
from operator import attrgetter
from random import randrange

RM_PMX='PMX'
RM_OX1='OX1'
RM_COPY='COPY'

FIT_WEIGHT_SKILLDIFF=50
FIT_WEIGHT_MATESIMILARITY=20

POPULATION_SIZE = 700
MAX_GENERATIONS = 70

class KartTournament:
    """Object to represent a tournament, calculate its fitness and recombine it"""
    def __init__(self, playerproperties=None, locationproperties=None, ancestor_A=None, ancestor_B=None, recombinationMode=RM_PMX):
        if (playerproperties != None and locationproperties != None):
            self._playerproperties = playerproperties
            self._locationproperties = locationproperties
        else:
            if ancestor_A==None:
                raise Exception("Cant create KartTournement, Neither ancestor_A given, nor playerproperties and location")
            self._playerproperties = ancestor_A._playerproperties
            self._locationproperties = ancestor_A._locationproperties
        self._seatinglist=[]
        self._pairsize=[4,4,3] #todo determine pairsize from member count in playerproperties
        self._pairings=[]
        self._fitness=999999
        self._fitness_of_skill=999999
        self._fitness_of_player_history=999999
        if ancestor_A == None :
            self.build_gene_from_scratch()
        elif ancestor_B == None:
            if recombinationMode==RM_COPY:
                self.clone_ancestor(ancestor_A)
            else:
                self.build_gene_from_scratch()
        elif recombinationMode==RM_PMX:
            self.build_from_PMX_crossover(ancestor_A, ancestor_B)
        elif recombinationMode==RM_OX1:
            self.build_from_OX1_crossover(ancestor_A, ancestor_B)




    def build_gene_from_scratch(self):
        number_of_players = len(self._playerproperties)
        try_again=0
        while True:
            try_again += 1
            # seed the drawing bowl with all player numbers
            drawBowl=[]
            for player_index in range(0,number_of_players):
                drawBowl.append(player_index)

            # draw all players randomly from bowl to the seating
            self._seatinglist=[]
            while len(drawBowl)>0:
                lady_luck=randrange(0,len(drawBowl))
                self._seatinglist.append(drawBowl[lady_luck])
                drawBowl.pop(lady_luck)

            self.deriveTournamentStructure()
            self.calculate_fitness()

            if self.isValid():
                break
            if try_again>3000:
                raise Exception("Could not find a valid random gene")

    def clone_ancestor(self,ancestor_A):
        self._seatinglist=ancestor_A._seatinglist.copy()

    def deriveTournamentStructure(self):
        """Fills the _pairings list with the tournament structure
                pairing {'teams':[] , pairing properties}
                    team: {'members':[], team properties}
                       member:{player_index}
                    """
        members=[]
        teams=[]
        self._pairings = []
        self._fitness = 999999
        for player_index in self._seatinglist:
            if len(members)>= self._pairsize[len(self._pairings)]: # current team is complete
                team = {'members': members}
                self.determine_team_skill(team)
                teams.append(team)
                members=[]
                if len(teams)>=2: # the pairing has two members
                    pairing={'teams':teams}
                    self.determine_pairing_skill_relation(pairing)
                    self._pairings.append(pairing)
                    teams=[]
            # place member in the current team
            team_member={'player_index':player_index}
            members.append(team_member)
        team = {'members': members}
        self.determine_team_skill(team)
        teams.append(team)
        pairing = {'teams': teams}
        self.determine_pairing_skill_relation(pairing)
        self._pairings.append(pairing)

    def calculate_console_usage(self):
        """Collect the needed console seats and add it as properties to the pairing
            'location_console_counts': "<location name>": count
            'empty_seat_count'
            'total_console_count'
        """
        for pairing in self._pairings:
            consolusage= {}
            emtpy_seats=0
            consoltotalcount=0
            teams=pairing['teams']
            for team in teams:
                team_location_seats={}
                for team_member in team['members']: #collect location of every teammember
                    location=self._playerproperties[team_member['player_index']]['location']
                    if location in team_location_seats:
                        team_location_seats[location]+=1
                    else:
                        team_location_seats[location]=1
                for location,location_seats in  team_location_seats.items(): # determine console count and empty seats
                    number_of_consoles_for_team=ceil(location_seats/2)
                    consoltotalcount += number_of_consoles_for_team
                    if location in consolusage:
                        consolusage[location]+=number_of_consoles_for_team
                    else:
                        consolusage[location]=number_of_consoles_for_team

                    if location_seats%2==1:
                        emtpy_seats+=1
            # After counting consols for all teams in the pairing, add the result to the pairing
            pairing['location_console_counts']=consolusage
            pairing['empty_seat_count']=emtpy_seats
            pairing['total_console_count']=consoltotalcount


    def build_from_PMX_crossover(self,parent_A,parent_B):

        recombination_pattern=[]
        seatcount=len(parent_A._seatinglist)
        for seat_index in range(0,seatcount):
           recombination_pattern.append(random.randrange(0,2))

        compressed_parent_A=[]
        for seat_index in range(0,seatcount):
            if(recombination_pattern[seat_index])==0:
                compressed_parent_A.append(parent_A._seatinglist[seat_index])

        compressed_parent_B=[]
        for seat_index in range(0,seatcount):
            player=parent_A._seatinglist[seat_index]
            if player not in compressed_parent_A:
                compressed_parent_B.append(player)

        seat_B_index=0
        for seat_index in range(0,seatcount):
            if(recombination_pattern[seat_index])==0:
                self._seatinglist.append(parent_A._seatinglist[seat_index])
            else:
                self._seatinglist.append(compressed_parent_B[seat_B_index])
                seat_B_index+=1

        self.deriveTournamentStructure()
        self.calculate_fitness()

    def mutate(self):
        index_a = random.randrange(0, len(self._seatinglist))
        index_b = index_a
        try_again_determine_partner = 1
        while try_again_determine_partner > 0:
            try_again_determine_partner += 1
            if try_again_determine_partner > 1000:  # safety against endless search (mostly because of coding mistakes)
                raise Exception("could not leave search loop for mutation partner")
            index_b = random.randrange(0, len(self._seatinglist))
            if index_b != index_a:
                try_again_determine_partner = 0  # signal to leave search partner loop

        #swap places
        extra_seat=self._seatinglist[index_a]
        self._seatinglist[index_a]=self._seatinglist[index_b]
        self._seatinglist[index_b]=extra_seat

        self.deriveTournamentStructure()
        self.calculate_fitness()

    def determine_team_skill(self,team):
        """ add "skillsum" property to the team """
        skillsum=0
        for member in team['members']:
            playerproperty = self._playerproperties[member['player_index']]
            skillsum += playerproperty['skill']
        team['skillsum']=skillsum

    def determine_pairing_skill_relation(self,pairing):
        """ add "skilldiff" property to the pairing """
        teams=pairing['teams']
        skilldiff=abs(teams[0]['skillsum']-teams[1]['skillsum'])
        pairing['skilldiff']=skilldiff

    def calculate_fitness(self):
        """Evaluates the tournament against all criteria and determines a fitness value
            the lower, the better"""
        self.calculate_console_usage()

        skilldiffsum=0
        for pairing in self._pairings:
            skilldiffsum+=pairing['skilldiff']

        self._fitness_of_skill=round(FIT_WEIGHT_SKILLDIFF/(1+skilldiffsum),4)

        former_teammate_similarity=self.calculateFormerTeammateSimilarity()

        self._fitness_of_player_history=round(FIT_WEIGHT_MATESIMILARITY/(1+former_teammate_similarity),4)

        self._fitness=self._fitness_of_player_history+self._fitness_of_skill

    def calculateFormerTeammateSimilarity(self,print_hits=False):
        """Determines how often players are grouped with players, they already played with"""
        teammateSimilarity=0
        for pairing in self._pairings:
            for team in pairing['teams']:
                members=team['members']
                for member_index, member in enumerate(members): # note: members dict with player_index
                    if member_index+1 >= len(members): # nothing to compare for the last member
                        break
                    player_index=member['player_index']
                    former_teammates=self._playerproperties[player_index]['former_teammates']
                    for mate_index in range(member_index+1,len(members)): #only compare with members after current  in list
                        mate_player=self._playerproperties[members[mate_index]['player_index']]
                        mate_player_id=mate_player['player_id']
                        if mate_player_id in former_teammates:
                            teammateSimilarity += former_teammates[mate_player_id]
                            if print_hits:
                                print(f"Similar mate pairing {player_index} + {mate_player_id} : {former_teammates[mate_player_id]}")
        return teammateSimilarity

    def isValid(self):

        for pairing in self._pairings:
            # do we have enough consoles for the pairing ?
            for location,console_count in pairing['location_console_counts'].items():
                if self._locationproperties[location]['console_count']<console_count:
                    return False  # we need more consoles in the location, than we have

        for pairing in self._pairings:
            # are there parings with unequal size, where the larger group has less skill
            teams=pairing['teams']
            if len(teams[0]['members'])>len(teams[1]['members']): # seating roster will always have lager team first
                if teams[0]['skillsum']<teams[1]['skillsum']:
                    return False

        return True

    def getFitness(self):
        return self._fitness

    def is_equal_to(self,otherTournament):
        #todo extend comparison to swapped seats in same team
        #todo extend comprison to swapped teams in same pairing
        seatcount = len(self._seatinglist)
        for seat_index in range(0, seatcount):
            if self._seatinglist[seat_index] != otherTournament._seatinglist[seat_index]:
                return False
        return True

    def print_pairings(self):
        for pairing in self._pairings:
            print ("vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv")
            location_string=""
            for location,console_count in pairing['location_console_counts'].items():
                location_string+= f" {location}={console_count} "
            teams=pairing['teams']
            for team_index,team in enumerate(pairing['teams']):
                if team_index>0:
                    print(f" >> {round(teams[0]['skillsum'],2)} >> [{round(pairing['skilldiff'],2)}] << {round(teams[1]['skillsum'],2)} << | total consoles:{pairing['total_console_count']} [{location_string}] empty seats:{pairing['empty_seat_count']}")
                for team_member in team['members']:
                    playerproperty = self._playerproperties[team_member['player_index']]
                    print(f"[{playerproperty['player_id']}]{playerproperty['location']}-{playerproperty['name']} ({playerproperty['skill']})")
            print ("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")

    def print_statistics(self):
        print (f"Fitness {self._fitness}  (Skill:{self._fitness_of_skill}, History:{self._fitness_of_player_history})")
        for pairing in self._pairings:
            teams=pairing['teams']
            print(f"{len(teams[0]['members'])}({round(teams[0]['skillsum'],2)})  \t[{round(pairing['skilldiff'],2)}] \t{len(teams[1]['members'])}({round(teams[1]['skillsum'],2)})")

    def renderTournamentPlan(self):
        planGames=[]
        tournamentPlan={'games':planGames}
        #print(json.dumps(self._pairings,indent=4))
        for pairing in self._pairings:
            planTeams=[]
            planGame={'teams':planTeams,
                      'empty_seat_count':pairing['empty_seat_count'],
                      'total_console_count':pairing['total_console_count'],
                      'location_console_counts':pairing['location_console_counts'].copy()                      }
            planGames.append(planGame)
            for team in pairing['teams']:
                planMembers=[]
                planTeam={'team_skill':team['skillsum'], 'members':planMembers}
                planTeams.append(planTeam)
                for member in team['members']:
                    planMembers.append(self._playerproperties[member['player_index']]['player_id'])
        return tournamentPlan




#   for
#   'games': [{'teams': [{'team_id': 'andt4as', 'members': ['14', '03', '08', '06'], 'placement': 1}  # 1st place
#       , {'team_id': 'fdja029', 'members': ['00', '16', '07', '15'], 'placement': 2}]  # 2nd place
#              },
#             {'teams': [{'team_id': 'a423faa', 'members': ['13', '19', '01', '05'], 'placement': 0}
#                 , {'team_id': 'fdja029', 'members': ['20', '11', '17', '04'], 'placement': 0}]
#              # 0 = draw -1 = canceled
#              },
#             {'teams': [{'team_id': 'w35v1232', 'members': ['12', '02', '10'], 'placement': 2}
#                 , {'team_id': '534we5g', 'members': ['18', '09'], 'placement': 1}]
#              }
#             ]


# end of class KartTournament -------------------------------------------------------------

g_playerproperties = [
    {'player_id':'00', 'name':'(A) Thomas J.'    , 'skill': 1.35, 'location':'D'}
   ,{'player_id':'01', 'name':'(A) Robert'       , 'skill': 1.35, 'location':'B'}
   ,{'player_id':'02', 'name':'(A) Alexander'    , 'skill': 1.35, 'location':'D'}
   ,{'player_id':'03', 'name':'(A) Oliver S'     , 'skill': 1.35, 'location':'F'}
   ,{'player_id':'04', 'name':'(A) Luca'         , 'skill': 1.35, 'location':'B'}
   ,{'player_id':'05', 'name':'(B) TvA'          , 'skill': 1.00, 'location':'D'}
   ,{'player_id':'06', 'name':'(B) Marc He.'     , 'skill': 1.00, 'location':'F'}
   ,{'player_id':'07', 'name':'(B) Christian K.' , 'skill': 1.00, 'location':'D'}
   ,{'player_id':'08', 'name':'(B) Maria'        , 'skill': 1.00, 'location':'B'}
   ,{'player_id':'09', 'name':'(B) Florian'      , 'skill': 1.00, 'location':'D'}
   ,{'player_id':'10', 'name':'(C) Marc Hü.'     , 'skill': 0.55, 'location':'F'}
   ,{'player_id':'11', 'name':'(C) Christian H.' , 'skill': 0.55, 'location':'B'}
   ,{'player_id':'12', 'name':'(C) Marcel'       , 'skill': 0.55, 'location':'D'}
   ,{'player_id':'13', 'name':'(C) John'         , 'skill': 0.55, 'location':'B'}
   ,{'player_id':'14', 'name':'(C) Sankalita'    , 'skill': 0.55, 'location':'B'}
   ,{'player_id':'15', 'name':'(C) Thomas P.'    , 'skill': 0.55, 'location':'B'}
   ,{'player_id':'16', 'name':'(A) Christina'    , 'skill': 1.35, 'location':'D'}
   ,{'player_id':'17', 'name':'(B) Ulrich K.'    , 'skill': 1.00, 'location':'F'}
   ,{'player_id':'18', 'name':'(A) Claudia'      , 'skill': 1.35, 'location':'B'}
   ,{'player_id':'19', 'name':'(B) Tarik'        , 'skill': 1.00, 'location':'D'}
   ,{'player_id':'20', 'name':'(B) Michael'      , 'skill': 1.00, 'location':'F'}
     ]

g_location_properties ={
    "B":{"console_count":3},
    "D": {"console_count": 2},
    "F": {"console_count": 1},
    "HH": {"console_count": 2},
}

g_event_game_history = []
ga_event_game_history = [
    {'tournament_id':1,
                   'games': [{'teams':[{'team_id':'asj29as','members': ['20','01','15','03'],'placement':1} # 1st place
                                       ,{'team_id':'fdja029','members':['12','08','00','18'],'placement':2}] #2nd place
                              },
                            {'teams':[{'team_id':'a423faa','members':  ['04','14','16','19'],'placement':0}
                                       ,{'team_id':'fdja029','members':['02','13','07','17'],'placement':0}] # 0 = draw -1 = canceled
                              },
                            {'teams': [{'team_id': 'w35v1232', 'members': ['11','10','06'], 'placement': 2}
                                 , {'team_id': '534we5g', 'members': ['05','09'], 'placement': 1}]
                              }
                             ]
     },
    {'tournament_id': 2,
     'games': [{'teams': [{'team_id': 'andt4as', 'members': ['14', '03', '08', '06'], 'placement': 1}  # 1st place
         , {'team_id': 'fdja029', 'members': ['00', '16', '07', '15'], 'placement': 2}]  # 2nd place
                },
               {'teams': [{'team_id': 'a423faa', 'members': ['13', '19', '01', '05'], 'placement': 0}
                   , {'team_id': 'fdja029', 'members': ['20', '11', '17', '04'], 'placement': 0}]
                # 0 = draw -1 = canceled
                },
               {'teams': [{'team_id': 'w35v1232', 'members': ['12', '02', '10'], 'placement': 2}
                   , {'team_id': '534we5g', 'members': ['18', '09'], 'placement': 1}]
                }
               ]
     }
]

def transformEventGameHistoryIntoPlayerStats():
    """Calculate kpi and relation tables for every person from the game history """
    for player in g_playerproperties:
        # ensure, empty history elements are in the player dictionary
        player['former_teammates'] = {}
        player['former_opponents'] = {}

        # now gather the data from the history
        for tournament in g_event_game_history:
            for game in tournament['games']:
                addGameHistoryToPlayerStats(game,player)

def addGameHistoryToPlayerStats(game,player):
    player_id=player['player_id']
    own_team_index=-1

    #search for own tean
    for team_index, team in enumerate(game['teams']):
        if player_id in team['members']:
            own_team_index=team_index
            break

    if own_team_index == -1:
        return   # player was not participant in this game

    own_team=game['teams'][own_team_index]

    former_teammates=player['former_teammates']
    for member_id in own_team['members']:
        if member_id == player_id:
            continue
        if member_id not in former_teammates:
            former_teammates[member_id] = 1
        else:
            former_teammates[member_id] += 1


    former_opponents=player['former_opponents']
    for  team_index, opponent_team in enumerate(game['teams']):
        if team_index == own_team_index:
            continue
        for member_id in opponent_team['members']:
            if member_id not in former_opponents:
                former_opponents[member_id] = 1
            else:
                former_opponents[member_id] += 1


def singleTest():
    myFirstGame=KartTournament(playerproperties= g_playerproperties,locationproperties=g_location_properties)
    myFirstGame.print_pairings()
    print(f"Fitness is {myFirstGame.getFitness()}")


def print_populationTournamentStatisticsVerboose(population,limit=None):
    for tournament_index, tournament in enumerate (population) :
        print(f"------ Tournament Variation {tournament_index+1} ------")
        tournament.print_statistics()
        if limit!=None and tournament_index+1>=limit:
            break

def print_populationTournamentStatisticsMain(population):
    for tournament_index, tournament in enumerate (population) :
        print(f"{tournament_index}. {tournament.getFitness()} ")

def print_playerScores():
    for player in g_playerproperties:
        print(f"[{player['player_id']}] {player['name']}:{player['score']}")





def create_successor_population(ancestors):
    ancestors.sort(key=attrgetter('_fitness'),reverse=True)
    successors=[]
    while len(successors)<POPULATION_SIZE:
        try_again_recombination=1
        while True:
            try_again_recombination += 1
            index_a=int(random.triangular(0,POPULATION_SIZE,0))
            index_b=index_a
            try_again_determine_partner=1
            while try_again_determine_partner>0:
                try_again_determine_partner+=1
                if try_again_determine_partner>1000: # safety against endless search (mostly because of coding mistakes)
                    raise Exception("could not leave search loop for recombination partner")
                index_b=int(random.triangular(0,POPULATION_SIZE,0))
                if index_b != index_a:
                    try_again_determine_partner=0 # signal to leave search partner loop
            #print(f"trying {index_a},{index_b}")
            partner_a=ancestors[index_a]
            partner_b=ancestors[index_b]
            new_successor = KartTournament(ancestor_A= partner_a, ancestor_B= partner_b)
            ensure_uniquenes_by_mutation(new_successor, successors)
            if new_successor.isValid():
                successors.append(new_successor)
                break  # leave recombination loop
            if try_again_recombination > 20:  # safety against endless search (mostly because of coding mistakes)
                new_successor = KartTournament(ancestor_A=ancestors[index_a])
                successors.append(new_successor)
                print("added new random tournament, since all others converge to same result")
                break  #leave recombination loop
    return successors

def ensure_uniquenes_by_mutation(new_successor,successors):
    for tries in range (0,100):
        is_unique=True
        for established_tournament in successors:
            if new_successor.is_equal_to(established_tournament):
                is_unique=False
                break
        if is_unique:
            return
        else:
            new_successor.mutate()


def assembleTournament(print_trace=False):
    """Creates a tournament setupt, based on the current player and location """
    # create the initial population
    population=[]
    # initial random seed
    for tournament_index in range(0,POPULATION_SIZE):
        population.append(KartTournament(playerproperties= g_playerproperties,locationproperties=g_location_properties))

    for generation in range(0,MAX_GENERATIONS):
        print(f"{generation}.",end='')
        if (generation+1)%20==0:
            print("")
        population = create_successor_population(population)
        #population.sort(key=attrgetter('_fitness'), reverse=True)
        #print_populationTournamentStatisticsMain(population)
        #print_populationTournamentStatisticsVerboose(population)

    print("")
    if print_trace:
        print("")
        print("######################################### Result ###########################################")
        population.sort(key=attrgetter('_fitness'), reverse=True)
        print_populationTournamentStatisticsVerboose(population,limit=10)
        for pair_index in range(0,3):
            print(f"******************************************** {pair_index} ({population[pair_index].getFitness()}) ****************************************************************")
            population[pair_index].calculateFormerTeammateSimilarity(print_hits=True)
            population[pair_index].print_pairings()
    else:
        population[0].calculateFormerTeammateSimilarity(print_hits=True)
        population[0].print_pairings()

    return population[0].renderTournamentPlan()


def mockTournamentExecution(tournament_plan):
    for game in tournament_plan['games']:
        winner=random.randrange(0,2)
        draw=random.randrange(0,200)
        for team_index,team in enumerate(game['teams']):
            if draw==0:
                team['placement']=0
            elif team_index==winner:
                team['placement'] = 1
            else:
                team['placement'] = 2

def determineGameScores(tournament_plan,win_bonus=0):
    for game in tournament_plan['games']:
        for team_index,team in enumerate(game['teams']):
           if team_index == 0 :
               opponent_team= game['teams'] [1]
           else:
               opponent_team=game['teams'] [0]
           team['score']=0
           if team['placement']<opponent_team['placement']: # win
                team['score']=10+win_bonus
           elif team['placement']>opponent_team['placement']:
                if team['team_skill']<opponent_team['team_skill']-0.2:
                    team['score'] = -5
                else:
                    team['score'] = -10

def addTournamentToEventHistory(tournament_plan):
    histGames=[]
    histTournament={'games':histGames}
    g_event_game_history.append(histTournament)
    for game in tournament_plan['games']:
        histGame=game.copy()
        histGames.append(histGame)

def addGameScoresToPlayerProperties(tournament_plan):
    for player in g_playerproperties:
        player_id=player['player_id']
        if 'score' not in player:
            player['score']=0
        for game in tournament_plan['games']:
            for team in game['teams']:
                for member in team['members']:
                    if player_id == member:
                           player['score'] += team['score']

def simulateEvent(numberOfTournaments):
    for tournament in range (0,numberOfTournaments):
        print (f"######## Simulating Tournament {tournament+1} #############")
        transformEventGameHistoryIntoPlayerStats()
        tournament_plan=assembleTournament()
        mockTournamentExecution(tournament_plan)
        determineGameScores(tournament_plan,tournament)
        addGameScoresToPlayerProperties(tournament_plan)
        addTournamentToEventHistory(tournament_plan)
        ##print(json.dumps(tournament_plan, indent=4, sort_keys=True))
        #print_playerScores()
        addTournamentToEventHistory(tournament_plan)
        #print(json.dumps(g_event_game_history,indent=4, sort_keys=True ))

if __name__ == '__main__':
    #singleTest()
    simulateEvent(5)
    g_playerproperties.sort(key=lambda k: k['score'],reverse=True)
    print("")
    print(" ##############  Final event placement ##############")
    print_playerScores()





