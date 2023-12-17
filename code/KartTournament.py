import random
from math import ceil
from operator import attrgetter
from random import randrange

RM_PMX='PMX'
RM_OX1='OX1'
RM_COPY='COPY'

FIT_WEIGHT_SKILLDIFF=20
POPULATION_SIZE = 300

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

        pairingdiffsum=0
        for pairing in self._pairings:
            pairingdiffsum+=pairing['skilldiff']

        self._fitness=round(FIT_WEIGHT_SKILLDIFF/(1+pairingdiffsum),4)

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
                    print(f"{playerproperty['location']}-{playerproperty['name']} ({playerproperty['skill']})")
            print ("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")

    def print_statistics(self):
        print (f"Fitness {self._fitness}")
        for pairing in self._pairings:
            teams=pairing['teams']
            print(f"{len(teams[0]['members'])}({round(teams[0]['skillsum'],2)})  \t[{round(pairing['skilldiff'],2)}] \t{len(teams[1]['members'])}({round(teams[1]['skillsum'],2)})")

# end of class KartTournament

g_playerproperties = [
    {'name':'(A) Thomas J.'    , 'skill': 1.35, 'location':'D'}
   ,{'name':'(A) Robert'       , 'skill': 1.35, 'location':'B'}
   ,{'name':'(A) Alexander'    , 'skill': 1.35, 'location':'D'}
   ,{'name':'(A) Oliver S'     , 'skill': 1.35, 'location':'F'}
   ,{'name':'(A) Luca'         , 'skill': 1.35, 'location':'B'}
   ,{'name':'(B) TvA'          , 'skill': 1.00, 'location':'D'}
   ,{'name':'(B) Marc He.'     , 'skill': 1.00, 'location':'F'}
   ,{'name':'(B) Christian K.' , 'skill': 1.00, 'location':'D'}
   ,{'name':'(B) Maria'        , 'skill': 1.00, 'location':'B'}
   ,{'name':'(B) Florian'      , 'skill': 1.00, 'location':'D'}
   ,{'name':'(C) Marc Hü.'     , 'skill': 0.55, 'location':'F'}
   ,{'name':'(C) Christian H.' , 'skill': 0.55, 'location':'B'}
   ,{'name':'(C) Marcel'       , 'skill': 0.55, 'location':'D'}
   ,{'name':'(C) John'         , 'skill': 0.55, 'location':'B'}
   ,{'name':'(C) Sankalita'    , 'skill': 0.55, 'location':'B'}
   ,{'name':'(C) Thomas P.'    , 'skill': 0.55, 'location':'B'}
   ,{'name':'(A) Christina'    , 'skill': 1.35, 'location':'D'}
   ,{'name':'(B) Ulrich K.'    , 'skill': 1.00, 'location':'F'}
   ,{'name':'(A) Claudia'      , 'skill': 1.35, 'location':'B'}
   ,{'name':'(B) Tarik'        , 'skill': 1.00, 'location':'D'}
   ,{'name':'(B) Michael'      , 'skill': 1.00, 'location':'F'}
     ]

g_location_properties ={
    "B":{"console_count":3},
    "D": {"console_count": 2},
    "F": {"console_count": 1},
    "HH": {"console_count": 2},
}

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


def searchForOptimum():
    # create the initial population
    population=[]
    # initial random seed
    for tournament_index in range(0,POPULATION_SIZE):
        population.append(KartTournament(playerproperties= g_playerproperties,locationproperties=g_location_properties))

    for generation in range(0,50):
        print(f">>>>>>>>>>> GEN {generation} <<<<<<<<<<<")
        population = create_successor_population(population)
        #population.sort(key=attrgetter('_fitness'), reverse=True)
        #print_populationTournamentStatisticsMain(population)
        #print_populationTournamentStatisticsVerboose(population)


    print("")
    print("######################################### Result ###########################################")
    population.sort(key=attrgetter('_fitness'), reverse=True)
    print_populationTournamentStatisticsVerboose(population,limit=10)
    for pair_index in range(0,3):
        print(f"******************************************** {pair_index} ({population[pair_index].getFitness()}) **********")
        population[pair_index].print_pairings()


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





if __name__ == '__main__':
    #singleTest()
    searchForOptimum()
    #for i in range(0,10):
    #    print(random.triangular(0.0,100.0,0.0))


