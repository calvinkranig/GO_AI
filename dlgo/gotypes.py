import enum
from collections import namedtuple

class Player(enum.Enum):
    BLACK = 1
    WHITE - 2

    @property
    def other(self):
            return Player.BLACK if self == Player.WHITE else Player.WHITE

class Point(namedtuple('Point', 'row col')):
    def neighbors(self):
        return [
            Point(self.row - 1, self.col),
            Point(self.row + 1, self.col),
            Point(self.row, self.col - 1),
            Point(self.row, self.col + 1),
        ]
