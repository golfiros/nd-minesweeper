import numpy as np 
import sys
from termcolor import colored

# GLOBAL VARS: N, dim, density, board
N = 10  # board size
dim = 2 
density = .25

usr = input('enter the board size N and density (in the format 10 .1): ')
try: 
  usr_parsed = usr.split(' ')
  N = int(usr_parsed[0])
  usr_density = float(usr_parsed[1])
  if usr_density < 1: 
    density = usr_density
  else: 
    print('fuck u, using default density')
except: 
  print('fuck u, using defaults')

###############################################################
#####################  GENERATE A BOARD   #####################
###############################################################

board_shape = tuple([N for d in range(dim)])
board = np.random.rand(*board_shape)
board = np.array(board < density, dtype=int)
print('%%%%%%%%%%%% N-d TORUS MINESWEEPER %%%%%%%%%%%%')
print('N =', N, 'd =', dim, 'number of bombs:', np.sum(board))
print('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
print("some instructions bc you're a noob: 'enter your move' takes 4 possible options")
print("  o [row #] [column #] : open coordinate")
print("  f [row #] [column #] : flag coordinate")
print("  u [row #] [column #] : unflag coordinate")
print("  s [row #] [column #] : shift torus to the right by [row #] and bottom by [column #]")
print('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')

def get_bombs_coords(): 
  # returns list of tuples with coordinates of flags
  return list(map(tuple, np.array(np.where(board > 0)).T))

def get_neighbours_coords(coordinate): 
  # returns list of coordinate tuples. coordinate must be a tuple.
  linspaces = []
  for i in range(dim):
    linspaces.append(np.array([(coordinate[i]-1) % N, coordinate[i], (coordinate[i]+1) % N,]))
  neighbours_coords = np.array(np.meshgrid(*linspaces),dtype=int).T.reshape(-1,dim)
  neighbours_coords = list(map(tuple,neighbours_coords))
  return list(set(neighbours_coords) - {coordinate})

def get_marked_board(bomb_coords): 
  markers = board * - 10 * N ** dim  # 3**dim should be enough
  for flag_coord in bomb_coords:
    neighbours_coords = get_neighbours_coords(flag_coord)
    for nbr in neighbours_coords:
      markers[nbr] += 1
  return markers

###############################################################
#####################     AESTHETICS      #####################
###############################################################

colors = { 
  1: 'blue', 2: 'green', 3: 'red', 4: 'magenta', 5: 'yellow', 6: 'cyan', 7: 'blue', 8: 'green'
}

def prettify_helper(char, p = 1, f = 0, d = 0): 
  # only for dim = 2
  if f == 1: return '⚑'  # '⚐' not saved in player known
  elif p == 0: return '■'
  elif char < 0 and d == 1: return '☠' 
  elif char < 0: return '⚑'
  elif char == 0 and p != 0: return colored('☐', 'grey')
  else: return colored(str(char), colors[char])

def prettify(markers, player = None, flags = None, shift = None, died = None): 
  # status: start game 0, during 1, end -1 
  # only for dim = 2
  if player is None: 
    player = np.ones_like(markers)
  if flags is None: 
    flags = np.zeros_like(markers)
  if shift is None: 
    shift = (0,0)
  d = 1
  if died is None: 
    died = (0,0)
    d = 0
  print('      '+' '.join(map(lambda i: str(i+1).ljust(2), list(range(N)))))
  print('   ┌'+'-'*(N * 3+2)+'┐')
  for i in range(len(markers)):
    i_shift = (i - shift[0]) % N
    m_ln = markers[i_shift]
    p_ln = player[i_shift]
    f_ln = flags[i_shift]
    pretty_line = []
    for j in range(len(m_ln)): 
      j_shift = (j-shift[1]) % N
      d_pass = int(d and (i_shift == died[0]) and (j_shift == died[1]))
      pretty_line.append(prettify_helper(m_ln[j_shift], p_ln[j_shift], f_ln[j_shift],d_pass))
    print(str(i+1).rjust(2)+' |  '+' '.join(map(lambda i: str(i)+' ', pretty_line))+' |')
  print('   └'+'-'*(N * 3+2)+'┘')

###############################################################
#####################   GAME PLAY TIME    #####################
###############################################################

def open_zero(coordinate, player, markers):
  # return current player board w all 
  zeros_queue = [coordinate]
  visited = set(list(map(tuple, np.array(np.where(player == 1)).T )))
  # empty if starting board w player=np.zeroes()
  new_player = player
  while len(zeros_queue) > 0:
    coord = tuple(zeros_queue.pop())
    new_player[coord] = 1
    visited.add(coord)
    neighbours_coords = get_neighbours_coords(coord)
    # add neighbours that are zero to the queue
    unvisited_coords = list(set(neighbours_coords) - visited)
    unvisited_vals = np.array(list(map(lambda coord: markers[coord], unvisited_coords)))
    zero_neighbours_indices = np.array(np.where(unvisited_vals == 0)).T.flatten()
    zero_neighbours_coords = list(np.array(unvisited_coords)[zero_neighbours_indices])
    zero_neighbours_coords = map(lambda coord: tuple(coord), zero_neighbours_coords)
    zeros_queue += zero_neighbours_coords
    # open the non-zero neighbours 
    nonzero_neighbours = list(set(unvisited_coords) - set(zero_neighbours_coords))
    for coord in nonzero_neighbours: 
      new_player[coord] = 1
  return new_player

def get_player_board(markers):
  # player board: known / unknown array. return array w random zero opened fully
  player = np.zeros_like(board)
  zero_coords = list(map(tuple, np.array(np.where(markers == 0)).T))
  ch = np.random.choice(len(zero_coords), 1)[0]
  rand_zero_coord = zero_coords[ch]
  return open_zero(rand_zero_coord, player, markers)

bomb_coords = get_bombs_coords()
markers = get_marked_board(bomb_coords)
# prettify(markers)

flags = np.zeros_like(markers)
player = get_player_board(markers)

# print('-'*int(N*1.5) + ' begin '+ '-'*int(N*1.5))
prettify(markers, player, flags)

alive = True
shift = (0,0)

def update_player_move(alive, coordinate, player, bomb_coords, flags):
  new_player = player 
  zero_coords = list(map(tuple, np.array(np.where(markers == 0)).T))
  
  if flags[coordinate] == 1: 
    return alive, new_player

  player[coordinate] = 1

  if coordinate in bomb_coords: 
    print('>   u died')
    if dim == 2:  # 2D ONLY
      prettify(markers, None, None, shift, died=coordinate)
    return not alive, new_player

  # win condition: found all bombs
  elif np.size(player) - np.sum(player) == np.sum(board): 
    print('>   wow u won!! crazy')
    if dim == 2:  # 2D ONLY
      prettify(markers, None, None, shift)
    return not alive, new_player
  
  elif coordinate in zero_coords: 
    new_player = open_zero(coordinate, player, markers)
    return alive, new_player

  else:
    return alive, new_player

def flag_coord(coordinate, player): 
  known_coords = list(map(tuple, np.array(np.where(player == 1)).T))
  if coordinate not in known_coords: 
    flags[coordinate] = 1
    return 0
  else: 
    return 1

while(alive): 
  move_str = input("enter your move (in the format: row #  column #): ")
  move_list = move_str.split(' ')
  try: 
    command = move_list[0]
    move = tuple(map(lambda i: int(i) - 1, move_list[1:3]))
    shifted_move = ((move[0] - shift[0]) % N, (move[1] - shift[1]) % N)
    if command == 'f':  # flag
      was_known = flag_coord(shifted_move, player)
    elif command == 'u':  # unflag
      flags[shifted_move] = 0 
    elif command == 'o':  # open
      alive, player = update_player_move(alive, shifted_move, player, bomb_coords, flags)
    elif command == 's': # shift 
      shift = (shift[0] + move[0] + 1, shift[1] + move[1] + 1)

    if alive:
      for _ in range(len(markers) + 4):
        sys.stdout.write("\x1b[1A\x1b[2K")
      # move snarky comments here bc otherwise they get erased
      if command == 'f' and was_known:
        print('>   bro u already know this')
      elif command not in {'f', 'u', 'o', 's'}: 
        print('>   bad command')
      prettify(markers,player,flags,shift)

  except:
    print(' >   u fucked up somehow try again')