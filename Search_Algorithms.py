from itertools import filterfalse
from queue import PriorityQueue
import pygame
import random
import networkx as nx
import matplotlib.pyplot as plt
import time
import copy
import cProfile
import pstats

def random_direction(): #pick a random cardical direction for maze gen
    x = random.randint(0,3)
    if x == 0:
        return (0,1)
    elif x == 1:
        return (1,0)
    elif x == 2:
        return (0,-1)
    else:
        return (-1,0)

def heuristic(a, b):
   # Manhattan distance on a square grid
   return (abs(a[0] - b[0]) + abs(a[1] - b[1]))

maze_size_x = int(input("Enter X Size: "))
maze_size_y = int(input("Enter Y Size: "))

maze_Graph = nx.Graph()
maze_subGraph = nx.DiGraph()
maze_node_constructor = []
maze_sGraph = nx.Graph()  

#create a node for each coordinate x,y. No edges currently connect the nodes
for i in range(maze_size_x):
    for j in range(maze_size_y):
        maze_node_constructor.append((i,j))


seed_node_index = random.randint(0,(len(maze_node_constructor) - 1))
seed_node = maze_node_constructor[seed_node_index]
del maze_node_constructor[seed_node_index]
maze_Graph.add_node(seed_node)

print("Generating maze graph")
while True:
    if not maze_node_constructor:
        break

    prev_node_index = random.randint(0,(len(maze_node_constructor) - 1))
    prev_node = maze_node_constructor[prev_node_index]
    del maze_node_constructor[prev_node_index]
    maze_subGraph.add_node(prev_node)

    start_node = prev_node

    while True:
        r_dir = random_direction()
        next_node = tuple(map(lambda i, j: i + j, prev_node, r_dir))
        #if the next node is out of bounds then continue
        if next_node[0] >= maze_size_x or next_node[0] < 0 or next_node[1] >= maze_size_y or next_node[1] < 0: 
            continue

        if maze_subGraph.has_node(next_node) != True:
            maze_subGraph.add_edge(next_node, prev_node)

        if maze_Graph.has_node(next_node):
            current_temp_node = next_node
            while current_temp_node != start_node:
                current_temp_node = tuple(maze_subGraph.edges(current_temp_node))
                maze_Graph.add_edge(current_temp_node[0][1], current_temp_node[0][0])       
                current_temp_node = current_temp_node[0][1]
                if current_temp_node in maze_node_constructor:
                    maze_node_constructor.remove(current_temp_node)
            
            maze_subGraph.clear()
            break


        prev_node = next_node


print("Enter coordinate for start node. From: (0,0) To: ", ((maze_size_x - 1), maze_size_y - 1))                
start_node_x = int(input("X: "))
start_node_y = int(input("Y: "))
start_node = (start_node_x, start_node_y)

print("Enter coordinate for end node. From: (0,0) To: ", ((maze_size_x - 1), maze_size_y - 1))                
end_node_x = int(input("X: "))
end_node_y = int(input("Y: "))
end_node = (end_node_x, end_node_y)

#compute simplified graph for A* to search. Removes nodes of order 2
print("Pruning maze graph")
maze_sGraph = copy.deepcopy(maze_Graph)
while True:
    s_graph_nodes = list(maze_sGraph.nodes)
    to_remove = []
    for i in s_graph_nodes:
        neighbors = list(maze_sGraph.neighbors(i))
        if len(neighbors) == 2:
            if neighbors[0][0] == neighbors[1][0] or neighbors[0][1] == neighbors[1][1]: 
                if i != start_node and i != end_node:
                    maze_sGraph.add_edge(neighbors[0],  neighbors[1], cost=(abs(neighbors[0][0] - neighbors[1][0]) + abs(neighbors[0][1] - neighbors[1][1])))
                    to_remove.append(i)

    if len(to_remove) == 0:
        break

    for i in to_remove:
        maze_sGraph.remove_node(i)

    print("Removed ", len(to_remove), " nodes")


# pygame setup
pygame.init()
res_x = 1000
res_y = 600
screen = pygame.display.set_mode((res_x, res_y))
maze_wall_surface = pygame.Surface((res_x, res_y))
clock = pygame.time.Clock()
global running
running = True

cell_size_x = res_x/maze_size_x
cell_size_y = res_y/maze_size_y

#helper dict to convert graph coords to screen space
maze_to_screen_coords_lookup = dict()
for i in range(maze_size_x):
    for j in range(maze_size_y):
        maze_to_screen_coords_lookup[(i,j)] = ((cell_size_x*i),(cell_size_y*j))


#precompute wall coordinates
print("Precomputing wall coordiantes")
wall_coords = []
draw_nodes = list(maze_Graph.nodes)
for i in range(maze_size_x):
    for j in range(maze_size_y):
        if ((i,j)) in draw_nodes:
            temp = list(maze_Graph.edges((i,j)))
            edges_to_draw = []
            for k in temp:
                edges_to_draw.append(k[1])

            if (i,(j + 1)) not in edges_to_draw: #draw north walls
                draw_coord_1 = (maze_to_screen_coords_lookup[(i,j)][0], (maze_to_screen_coords_lookup[(i,j)][1] + cell_size_y))
                draw_coord_2 = ((maze_to_screen_coords_lookup[(i,j)][0] + cell_size_x), (maze_to_screen_coords_lookup[(i,j)][1] + cell_size_y))
                wall_coords.append([draw_coord_1, draw_coord_2])

            if ((i + 1),j) not in edges_to_draw: #draw east walls
                draw_coord_1 = ((maze_to_screen_coords_lookup[(i,j)][0] + cell_size_x), maze_to_screen_coords_lookup[(i,j)][1])
                draw_coord_2 = ((maze_to_screen_coords_lookup[(i,j)][0] + cell_size_x), (maze_to_screen_coords_lookup[(i,j)][1] + cell_size_y))
                wall_coords.append([draw_coord_1, draw_coord_2])                      
 
            if (i,(j - 1)) not in edges_to_draw: #draw south walls
                draw_coord_1 = maze_to_screen_coords_lookup[(i,j)]
                draw_coord_2 = ((maze_to_screen_coords_lookup[(i,j)][0] + cell_size_x), maze_to_screen_coords_lookup[(i,j)][1])
                wall_coords.append([draw_coord_1, draw_coord_2])                  

            if ((i - 1),j) not in edges_to_draw: #draw west walls
                draw_coord_1 = maze_to_screen_coords_lookup[(i,j)]
                draw_coord_2 = (maze_to_screen_coords_lookup[(i,j)][0], (maze_to_screen_coords_lookup[(i,j)][1] + cell_size_y))
                wall_coords.append([draw_coord_1, draw_coord_2])     

for i in wall_coords:
    pygame.draw.line(maze_wall_surface, "white", i[0], i[1], 1)   

found = False
frontier = PriorityQueue()
frontier.put(start_node, 0)
came_from = dict()
cost_so_far = dict()
came_from[start_node] = None
cost_so_far[start_node] = 0

cost_dict = nx.get_edge_attributes(maze_sGraph, "cost", default=1)

start_time = time.time()
end_time = None

def main():
    running = True
    state = 0
    while running:
        update_rects = []

        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # fill the screen with a color to wipe away anything from last frame
        screen.fill("black")

        #Draw maze walls
        screen.blit(maze_wall_surface, (0,0))
        
        if state == 0:
            if not frontier.empty():
                current = frontier.get()
                for i in frontier.queue:
                    pygame.draw.rect(screen, "blue", (maze_to_screen_coords_lookup[i], (cell_size_x, cell_size_y)))
                pygame.draw.rect(screen, "red", (maze_to_screen_coords_lookup[current], (cell_size_x, cell_size_y)))

                if (current == end_node):
                    found == True
                    end_time = time.time()
                for next in list(maze_sGraph.neighbors(current)):
                    if (current, next) in cost_dict:
                        new_cost = cost_so_far[current] + cost_dict[(current, next)]
                    else:
                        new_cost = cost_so_far[current] + 1
                    if next not in cost_so_far or new_cost < cost_so_far[next]:
                        cost_so_far[next] = new_cost
                        #priority = new_cost + (heuristic(next, end_node) * 100)
                        priority = new_cost + (abs(next[0] - end_node[0]) + abs(next[1] - end_node[1]))
                        frontier.put(next, priority)
                        came_from[next] = current
            else:
                found = True
                end_time = time.time()
        else:
            print("Finished in:", (end_time - start_time) / 60, " minutes")
            temp_coord = end_node
            #draw the path from start to end node
            while True:
                if temp_coord == start_node:
                    break

                last_coord = temp_coord
                temp_coord = came_from[temp_coord]
                pygame.draw.line(screen, "green", (maze_to_screen_coords_lookup[last_coord][0] + (cell_size_x/2), maze_to_screen_coords_lookup[last_coord][1] + (cell_size_y/2)), (maze_to_screen_coords_lookup[temp_coord][0] + (cell_size_x/2), maze_to_screen_coords_lookup[temp_coord][1] + (cell_size_y/2)), 1)
                n = list(maze_Graph.neighbors(last_coord))
                if temp_coord not in n:
                    print("  ")
                    
                else:




        # flip() the display to put your work on screen
        pygame.display.flip()

        clock.tick()  

    pygame.quit()

cProfile.run('main()', filename='profile_output.txt')

profiler = pstats.Stats("profile_output.txt")
# Print the profiling statistics
profiler.print_stats()

