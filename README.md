
# KartTeamBuilder

## Idea
When organizing a Mario Kart Tournament for many people with different skills (e.g. as part of a company event), it can be hard to assemble fair teams and pairings. There are so many parameters to consider, that pure permutation search will take to long. This python searches for a solution by using a genetic algorithm approach. 

## Criterias, checked:
- skill class of participants
- Location of participants, for allowing to play together from multiple locations
- Number of Switch Consoles available on every location
- Previous pairings as team member or opponent
- target number of teammates (must be less or equal to number of places at each location)

The evaluation weight of the criterias is configurable to allow different 

## Integration into event management tool
The script reads the player pool and environment properties from a json file and presents the result also as json file.

This allows an easy integration into a workflow or UI process, that provides functions to configure the player pool and location device pool, guides the execution by displaying the team pairings, track selection and console assignments and retrieving the result.