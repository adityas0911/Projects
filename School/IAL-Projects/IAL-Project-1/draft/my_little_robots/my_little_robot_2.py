import pygame, random as rd, math, heapq, csv, os
from collections import defaultdict


def create_ship(d):
  #     # = Blocked
  #     $ = Fire
  #     O = Open
  ship_layout = [["#" for x in range(d)] for x in range(d)]  # Fill array with blocked 
  x1,y1 = rd.randint(1, d-2), rd.randint(1, d-2)               # Choose random coordinates in interior
  ship_layout[x1][y1] = 'O'
  one_open_neighbor = []
    
  while True:  # "Iteratively do the following" part
      one_open_neighbor.clear()
      for x in range(1,d-1):
          for y in range(1,d-1):
              if ship_layout[x][y] == '#':
                      count = 0
                      if ship_layout[x-1][y]=='O':
                          count+=1
                      if ship_layout[x+1][y]=='O':
                          count+=1
                      if ship_layout[x][y-1]=='O':
                          count+=1
                      if ship_layout[x][y+1]=='O': count+=1
                      if count==1 and (x!=x1 or y!=y1):
                          one_open_neighbor.append((x,y))
                      
      if len(one_open_neighbor)==0:
                        break
      x,y = one_open_neighbor[rd.randint(0,len(one_open_neighbor)-1)] 
      ship_layout[x][y] = 'O'
  # Open half of dead-ends - final part
  closed_neighbors_dict = {}
  one_open_neighbor.clear()
  for x in range(1,d-1):
          for y in range(1,d-1):
              if ship_layout[x][y] == 'O':
                      temp_closed_neighbors = []
                      count = 0
                      if ship_layout[x-1][y]=='O':
                          count+=1
                      elif x!=1:
                           temp_closed_neighbors.append((x-1,y))  
                      if ship_layout[x+1][y]=='O':
                          count+=1
                      elif x!= d-2:
                           temp_closed_neighbors.append((x+1,y))  
                      if ship_layout[x][y-1]=='O':
                          count+=1
                      elif y!=1:
                           temp_closed_neighbors.append((x,y-1))    
                      if ship_layout[x][y+1]=='O': 
                           count+=1
                      elif y!= d-2:
                           temp_closed_neighbors.append((x,y+1))  
                      if count==1 and (x!=x1 or y!=y1):
                          one_open_neighbor.append((x,y))
                          closed_neighbors_dict[(x,y)] = closed_neighbors_dict.get((x,y), []) + temp_closed_neighbors

  rd.shuffle(one_open_neighbor) # Randomize the list of dead ends
  one_open_neighbor = one_open_neighbor[:len(one_open_neighbor)//2] # Split the list in half
  for x,y in one_open_neighbor:   # Open them
       neighbors_to_open = closed_neighbors_dict[(x,y)]      
       r = rd.randint(0, len(neighbors_to_open)-1)
       x2, y2 = neighbors_to_open[r]
       ship_layout[x2][y2] = 'O'
   
  return ship_layout

def robot_two_shortest_path(ship, start, goal):
    ## Find all possible neighbors for a given coordinate
    def get_neighbors(curr_position):
         neighbors = []
         x, y = curr_position
         if x!=0 and (ship[x-1][y] == 'O' or ship[x-1][y] == 'B'):
              neighbors.append((x-1,y))
         if x!=len(ship)-1 and (ship[x+1][y] == 'O' or ship[x+1][y] == 'B'):
              neighbors.append((x+1,y))
         if y!=len(ship)-1 and (ship[x][y+1] == 'O' or ship[x][y+1]== 'B'):
              neighbors.append((x,y+1))
         if y!=0 and (ship[x][y-1] == 'O' or ship[x][y-1] == 'B'):
              neighbors.append((x,y-1))
         return neighbors

    # Shortest path
    fringe = [(0,start)]
    heapq.heapify(fringe)
    parent = {}
    dist = defaultdict(lambda:float('inf'))
    dist[start] = 0 

    while len(fringe)!=0:        
        curr_dist, curr_position = heapq.heappop(fringe)
        if curr_position == goal:
            path = []
            while curr_position in parent:
                   path.append(curr_position)
                   curr_position = parent[curr_position] 
            path.reverse()               
            return path

        neighbors = get_neighbors(curr_position)
        for n in neighbors:
            dist_to_child = dist[curr_position] + 1
            if dist[n] > dist_to_child:
                 dist[n] = dist_to_child 
                 heapq.heappush(fringe, (dist_to_child, n))
                 parent[n] = curr_position
    

     # If there's no path return false
    return False
                   
         
         
    

def fire_spread(ship, q=.3):
    # Spread fire probabilistically 
    # Count number of fire cells around an open cell. 
    # Use random function to determine it will spread.
    new_fire_positions = []
    for x in range(1, len(ship)):
         for y in range(1, len(ship)):
              if ship[x][y] in {'O','B','R'}:
                   k = 0 
                   if ship[x-1][y] == 'F':
                        k+=1
                   if ship[x][y-1] == 'F':
                        k+=1
                   if ship[x][y+1] == 'F':
                        k+=1
                   if ship[x+1][y] == 'F':
                        k+=1
                   fire_odds = (1 - (1-q)**k)
                   roll = rd.random()
                   if roll < fire_odds:
                        new_fire_positions.append((x,y))            
    return new_fire_positions
def search_button_increment(ship, robot_position, button_position, q=.3):
    # Find shortest path to button  
    path = robot_two_shortest_path(ship, robot_position, button_position)
    x, y = robot_position

    # If the path is empty, the robot has pressed the button.
    if path==False: # If we get false, there is no shortest path.
         return False, (0,0) 
    elif len(path)==0:
         return True, (0,0)
    else:          # Else, update the robot's new postiion.
         ship[x][y] = 'O'
         x,y = path[0]
         ship[x][y] = 'R'


    # Spread the fire 
    new_fire_positions = fire_spread(ship,q)
    
    return new_fire_positions, (x,y)
     

def main(): 
    pygame.init()

    robot_type = 2

    d = 80
    q = 1
    # rd.seed(25) # Set random seed (same result each run)
    # print(os.getcwd()) 


    SCREEN_WIDTH = 900
    SCREEN_HEIGHT = 900
    SURFACE_WIDTH = math.ceil(SCREEN_WIDTH / d) 
    SURFACE_HEIGHT = math.ceil(SCREEN_HEIGHT / d) 

    test_surface = pygame.Surface((SURFACE_WIDTH,SURFACE_HEIGHT)) # Surface object goes on top of display
    screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))

    pygame.display.set_caption("My little robot")

    clock = pygame.time.Clock() # Time object
    ship = create_ship(d)
    SPLIT = SCREEN_HEIGHT / len(ship)

    # Split screen into blocks 
    ship_surfaces_dict = {(y*SPLIT,x*SPLIT):ship[x][y] for x in range(len(ship)) for y in range(len(ship))}

    open_cells = []
    # Color in the blocks with respective colors
    for coordinates in ship_surfaces_dict: 
                color = "black" if ship_surfaces_dict[coordinates]=="#"  \
                else "orchid" if ship_surfaces_dict[coordinates]=="O" \
                else "orange" if ship_surfaces_dict[coordinates]=='F' else 'white'
          
                test_surface.fill(color)
                screen.blit(test_surface, coordinates[0:2])
                if color == "orchid":
                     open_cells.append(coordinates)

    # Initial Fire, Robot, and Button
    rd.shuffle(open_cells)
    fire_location = open_cells[0]
    robot_location = open_cells[1]
    button_location = open_cells[2]

    robot_position = (int(robot_location[1] // SPLIT), int(robot_location[0] // SPLIT))
    button_position = (int(button_location[1] // SPLIT), int(button_location[0] // SPLIT))

    test_surface.fill("orange")
    screen.blit(test_surface,fire_location[0:2])
    ship[int(fire_location[1]//SPLIT)][int(fire_location[0]//SPLIT)] = 'F'

    test_surface.fill("whitesmoke")
    screen.blit(test_surface,robot_location[0:2])
    ship[robot_position[0]][robot_position[1]] = 'R'

    test_surface.fill("cyan1")
    screen.blit(test_surface,button_location[0:2])
    ship[button_position[0]][button_position[1]] = 'B'
    #

    run =True
    step_counter = 0
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                # If user presses X, stop the program
                pygame.quit()

        pygame.display.update()

        # Increment, find new robot  
        new_fire_positions, new_robot_position = search_button_increment(ship, robot_position, button_position, q)

        # Robot has no path to the button, self-destruct. 
        if new_fire_positions == False or new_fire_positions == True:
             pygame.quit()  
             # For data processing, write data to csv file
#<<<<<<< HEAD:Project 1/David/my_little_robot_2.py
          #    with open(r'C:\Users\vsh00\OneDrive - Rutgers University\python\AI-Project\IAL-Projects\Project 1\DataFiles\robot_data.csv', 'a', newline='') as file:
          #         writer = csv.writer(file)
          #         writer.writerows([[robot_type, d, q, step_counter, new_fire_positions]])
          #         print("written", new_fire_positions)
          #    run = False
# =======
#              with open(r'AI-Project\IAL-Projects\Project 1\David\DataFiles\robot2_data.csv', 'a', newline='') as file:
#                   writer = csv.writer(file)
#                   writer.writerows([[robot_type, d, q, step_counter, new_fire_positions]])
#                   print("written", new_fire_positions)
#              run = False
# >>>>>>> e961f76b2838192afd0faee76036cc45441c2dc5:Project 1/David/my_little_robots/my_little_robot_2.py
             break


        for x, y in new_fire_positions:
                ship_surfaces_dict[(y*SPLIT,x*SPLIT)] = 'F'
                ship[x][y] = 'F'
                test_surface.fill("orange")
                screen.blit(test_surface,(y*SPLIT,x*SPLIT))

        x,y = robot_position
        ship_surfaces_dict[(y*SPLIT,x*SPLIT)]
        ship[x][y] = 'O'
        test_surface.fill("orchid")
        screen.blit(test_surface,(y*SPLIT,x*SPLIT))

        x,y = new_robot_position
        ship_surfaces_dict[(y*SPLIT,x*SPLIT)]
        ship[x][y] = 'R'
        test_surface.fill("whitesmoke")
        screen.blit(test_surface,(y*SPLIT,x*SPLIT))
        robot_position = new_robot_position
        pygame.time.wait(50)
        step_counter+=1

        clock.tick(60) # Set framerate
    pygame.quit()

if __name__ == "__main__":
  main()
