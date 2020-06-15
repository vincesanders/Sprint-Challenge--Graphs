from room import Room
from player import Player
from world import World

import random
from ast import literal_eval

class Queue():
    def __init__(self):
        self.queue = []
    def enqueue(self, value):
        self.queue.append(value)
    def dequeue(self):
        if self.size() > 0:
            return self.queue.pop(0)
        else:
            return None
    def size(self):
        return len(self.queue)

# Load world
world = World()


# You may uncomment the smaller graphs for development and testing purposes.
# map_file = "maps/test_line.txt"
# map_file = "maps/test_cross.txt"
# map_file = "maps/test_loop.txt"
# map_file = "maps/test_loop_fork.txt"
map_file = "maps/main_maze.txt"

# Loads the map into a dictionary
room_graph=literal_eval(open(map_file, "r").read())
world.load_graph(room_graph)

# Print an ASCII map
world.print_rooms()

# start in room 0
player = Player(world.starting_room)

visited = {}
visited[player.current_room.id] = True

# Fill this out with directions to walk
# traversal_path = ['n', 'n']
traversal_path = []
rooms_to_visit = [] # used a normal array instead of a stack

'''
Traverses the maze till the player hits a dead end.
When confronted with multiple paths. The player will take the path that ends with a dead end, before others.
If a path with a dead end doesn't exist. The player has a strong bias for turning West and a weak bias for turning South.
'''
def traverse():
    found_exit = True
    # The traverse loop ends when we hit a dead end
    while found_exit:
        found_exit = False
        exits = player.current_room.get_exits()
        current = player.current_room
        possible_rooms = []
        # get a list of all rooms that haven't been visited yet
        for direction in exits:
            if current.get_room_in_direction(direction).id not in visited:
                possible_rooms.append((current.get_room_in_direction(direction), direction))
        # If this isn't a dead end
        if len(possible_rooms) > 0:
            # the first available room is chosen by default
            room_to_traverse = possible_rooms[0]
            for i in range(len(possible_rooms)):
                # if one room ends in an exit, take it instead
                if len(possible_rooms[i][0].get_exits()) < 2:
                    room_to_traverse = possible_rooms[i]
                    break
                # direction bias is weighted strongly to the west and weakly to the south
                if possible_rooms[i][1] is 'w':
                    room_to_traverse = possible_rooms[i]
                    break
                elif possible_rooms[i][1] is 's':
                    room_to_traverse = possible_rooms[i]
            # add other rooms to rooms_to_visit cache
            for room in possible_rooms:
                if room != room_to_traverse:
                    rooms_to_visit.append(room[0].id)
            room, direction = room_to_traverse
            # move the player to the chosen room
            player.travel(direction)
            traversal_path.append(direction)
            visited[room.id] = True # Add the chosen room to visited cache
            found_exit = True
        # loop until no unexplored direction

'''
Finds the shortest path to the unexplored node using breadth first search.
The player is searching his memory to pick the closest unexplored room.
'''
def find_shortest_path_to_unexplored(destination):
    visited_room = set()

    q = Queue() # queue to store paths as they are built
    q2 = Queue() # queue to store rooms as they are explored

    q.enqueue([])
    q2.enqueue(player.current_room)

    while q.size() > 0:
        path = q.dequeue()
        current = q2.dequeue()
        if current.id not in visited_room:
            visited_room.add(current.id)
            # If we reach our destination, return the path (the shortest path to our destination)
            if current.id == destination:
                return path
            exits = current.get_exits()
            for direction in exits:
                path_copy = list(path) # make a deep copy of the list
                path_copy.append(direction)
                q.enqueue(path_copy)
                q2.enqueue(current.get_room_in_direction(direction))
    return None # No path to the destination was found

'''
Traverses the path passed into parameters.
'''
def find_unexplored(path):
    # move player along path to unexplored
    for direction in path:
        player.travel(direction)
        traversal_path.append(direction)
    visited[player.current_room.id] = True

'''
Main loop.
The player will continue to explore the maze until all rooms are visited.
'''
while len(world.rooms) > len(visited):
    traverse()
    # If we've hit a dead end and the full maze hasn't been explored.
    if len(visited) != len(world.rooms):
        # Find the closest of the unexplored rooms
        paths = []
        # find the shortest path to each room that hasn't been explored yet.
        for unvisited in rooms_to_visit:
            paths.append(find_shortest_path_to_unexplored(unvisited))
        # iterate through all the paths to the remaining unvisited rooms
        shortest_path = None
        first_iter = True
        # fint the closest unexplored room
        for path in paths:
            if first_iter:
                shortest_path = path
                first_iter = False
                continue
            if len(path) <= len(shortest_path):
                shortest_path = path
        # travel to the closest one
        find_unexplored(shortest_path)
        # remove that room from rooms_to_visit cache
        rooms_to_visit.remove(player.current_room.id)



# TRAVERSAL TEST
visited_rooms = set()
player.current_room = world.starting_room
visited_rooms.add(player.current_room)

for move in traversal_path:
    player.travel(move)
    visited_rooms.add(player.current_room)

if len(visited_rooms) == len(room_graph):
    print(f"TESTS PASSED: {len(traversal_path)} moves, {len(visited_rooms)} rooms visited")
else:
    print("TESTS FAILED: INCOMPLETE TRAVERSAL")
    print(f"{len(room_graph) - len(visited_rooms)} unvisited rooms")



#######
# UNCOMMENT TO WALK AROUND
#######
# player.current_room.print_room_description(player)
# while True:
#     cmds = input("-> ").lower().split(" ")
#     if cmds[0] in ["n", "s", "e", "w"]:
#         player.travel(cmds[0], True)
#     elif cmds[0] == "q":
#         break
#     else:
#         print("I did not understand that command.")
