import copy
from dlgo.gotypes import Player

class Board():
  def __init__(self, num_rows, num_cols):
    self.num_rows = num_rows
    self.num_cols = num_cols
    self._grid = {}
    
  def _remove_string(self, string):
    for point in string.stones:
      for neighbor in point.neighbors():
        neighbor_str = self._grid.get(neighbor)
        if neighbor_str is not None and neighbor_str is not string:
          neighbor_str.add_liberty(point)
      self._grid[point] = None

  def is_on_grid(self, point):
    return (1 <= point.row <= self.num_rows
      and 1 <= point.col <= self.num_cols)
      
  def get(self, point):
    string = self._grid.get(point)
    if string is None:
      return None
    return string.color
  
  def get_go_string(self, point):
    string = self._grid.get(point)
    if string is None:
      return None
    return string
  
  def place_stone(self, player, point):
    assert self.is_on_grid(point)
    assert self._grid.get(point) is None
    adj_same_color = []
    adj_opposite_color = []
    liberties = []
    
    for neighbor in point.neighbors():
      if self.is_on_grid(neighbor):
        neighbor_str = self._grid.get(neighbor)
        if neighbor_str is None:
          liberties.append(neighbor)
        elif (neighbor_str.color == player
          and neighbor_str not in adj_same_color):
          adj_same_color.append(neighbor_str)
        elif neighbor_str not in adj_opposite_color:
        #neighbor_str is opposing color and not in list of opposite strings
          adj_opposite_color.append(neighbor_str)
            
    new_str = GoString(player, [point], liberties)
    
    for same_color_str in adj_same_color:
      new_str = new_str.merged_with(same_color_str)
    for new_str_point in new_str.stones:
      self._grid[new_str_point] = new_str
    for opposite_color_str in adj_opposite_color:
      opposite_color_str.remove_liberty(point)
      if opposite_color_str.num_liberties == 0:
        self._remove_string(opposite_color_str)

class GameState():
  def __init__(self, board, next_player, previous, move):
    self.board = board
    self.next_player = next_player
    self.previous_state = previous
    self.last_move = move
  
  @property
  def situation(self):
    return (self.next_player, self.board)
    
  @classmethod
  def new_game(cls, board_size):
    if isinstance(board_size, int):
      board_size = (board_size, board_size)
    board = Board(*board_size)
    return GameState(board, Player.BLACK, None, None)
    
  def apply_move(self, move):
    if move.is_play:
      next_board = copy.deepcopy(self.board)
      next_board.place_stone(self.next_player, move.point)
    else:
      next_board = self.board
    return GameState(next_board, self.next_player.other, self, move)
    
  def does_move_violate_ko(self, player, move):
    if not move.is_play:
      return False
    next_board = copy.deepcopy(self.board)
    next_board.place_stone(player, move.point)
    next_situation = (player.other, next_board)
    past_state = self.previous_state
    while past_state is not None:
      if past_state.situation == next_situation:
        return True
      past_state = past_state.previous_state
    return False
    
  def is_move_self_capture(self, player, move):
    if not move.is_play:
      return False
    next_board = copy.deepcopy(self.board)
    next_board.place_stone(player, move.point)
    new_string = next_board.get_go_string(move.point)
    return new_string.num_liberties == 0
    
  def is_over(self):
    if self.last_move is None or self.previous_state.last_move is None:
      return False
    if (self.last_move.is_resign 
      or (self.last_move.is_pass and self.previous_state.last_move.is_pass)):
      return True
      
  def is_valid_move(self, move):
    if self.is_over():
      return False
    if move.is_pass or move.is_resign:
      return True
    return (
      self.board.get(move.point) is None
      and not self.is_move_self_capture(self.next_player,move)
      and not self.does_move_violate_ko(self.next_player,move)
    )

class GoString():
  def __init__(self, color, stones, liberties):
    self.color = color
    self.stones = stones
    self.liberties = liberties

  def remove_liberty(self, point):
    self.liberties.remove(point)

  def add_liberty(self, point):
    self.liberties.add(point)

  def merged_with(self, go_string):
    assert go_string.color == self.color
    combined_stones = self.stones or go_string.stones
    return GoString(
      self.color,
      combined_stones,
      (self.liberties or go_string.liberties) - combined_stones
    )

  @property
  def num_liberties(self):
    return len(self.liberties)

  def __eq__(self,other):
    return isinstance(other, GoString) and \
    self.color == other.color and \
    self.stones == other.stones and \
    self.liberties == other.liberties

class Move():
  def __init__(self, point=None, is_pass=False, is_resign=False):
    assert (point is not None) ^ is_pass ^ is_resign
    self.point = point
    self.is_play = self.point is not None
    self.is_pass = is_pass
    self.is_resign = is_resign

  @classmethod
  def play(cls, point):
    return Move(point=point)

  @classmethod
  def pass_turn(cls):
    return Move(is_pass=True)

  @classmethod
  def resign(cls):
    return Move(is_resign=True)