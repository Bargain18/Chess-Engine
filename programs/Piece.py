from itertools import product, count
import ChessSet
from Move import Move
                
class Piece:
    def __init__(self, color, piece):
        self.color = color
        self.piece = piece
        #creates attribute to check whether pawn, rook, or king has been moved or not.
        if self.piece in ["p", "k", "r"]:
            self.moved = False
            #records at which move the pawn moved two squares
            #and seeing if all other conditions are met for the second to be true
            if self.piece == "p":
                self.two_squares = 0
        
        self.moves = []

    def find_available_pos(self, x, y, board, num_moves = None):
        grid = board.grid
        #print(grid)
        self.moves = []
        if self.piece == "b" or self.piece == "q":
            self.find_lines(x, y, grid, [(-1, -1), (1, 1), (1, -1), (-1, 1)])
        if self.piece == "r" or self.piece == "q":
            self.find_lines(x, y, grid, [(0, -1), (0, 1), (1, 0), (-1, 0)])
        elif self.piece == "n":
            self.find_l(x, y, grid)
        elif self.piece == "k":
            self.find_king_moves(x, y, grid, board)
        elif self.piece == "p":
            self.find_pawn_moves(x, y, grid, num_moves)

        #print(self.coords, self.attack_squares)
        return self.moves
            
    def find_lines(self, x, y, grid, directions):
        enemyColor = "B" if grid[y][x].color == "W" else "W"

        for direction in directions: 
            for j in range(1, 8):
                endRow = y + direction[1] * j
                endCol = x + direction[0] * j

                if endRow < 8 and endRow >= 0 and endCol < 8 and endCol >= 0:
                    if grid[endRow][endCol]:
                        if grid[endRow][endCol].color == enemyColor:
                            self.moves.append(Move((x, y), (endCol, endRow), grid))
                        break
                    else: 
                        self.moves.append(Move((x, y), (endCol, endRow), grid))
                else:
                    break


    def find_l(self, x, y, grid):
        enemyColor = "B" if grid[y][x].color == "W" else "W"
        #finds all permutations of 2s and 1s for knight
        j = list(product([x + 1, x - 1], [y + 2, y - 2])) + list(product([x + 2, x - 2], [y + 1, y - 1]))
        #removes all out of bounds
        j = [i for i in j if all(map(lambda x: x < 8 and x >= 0, i))]
        for move in j:
            if not grid[move[1]][move[0]] or grid[move[1]][move[0]].color == enemyColor:
                self.moves.append(Move((x, y), (move[0], move[1]), grid))

    def find_king_moves(self, x, y, grid, board):
        enemyColor = "B" if grid[y][x].color == "W" else "W"
        j = list(product([x - 1, x, x + 1], [y - 1, y, y + 1]))
        j = [i for i in j if all(map(lambda x: x < 8 and x >= 0, i))]
        #Removes the one you're already on
        j.remove((x,y))
        for move in j:
            if not grid[move[1]][move[0]] or grid[move[1]][move[0]].color == enemyColor:
                self.moves.append(Move((x, y), (move[0], move[1]), grid))
            
        king = grid[y][x]
        if king.moved or board.check_check(king.color): return
           
        for rook_x, rook_y in [(0, y), (7, y)]:
            rook = grid[rook_y][rook_x]
            if not (rook and rook.piece == "r" and rook.color != enemyColor and not rook.moved): return

            castle_possible = True
            arr = range(x+1, 7) if rook_x == 7 else range(1, x)
            for i in arr:
                if grid[y][i]:
                    castle_possible = False
                    break
                elif board.check_check(grid[y][x].color, king_coords = (i, y)):
                    castle_possible = False
                    break

            if castle_possible:
                j = 2 if rook_x == 7 else -2
                self.moves.append(Move((x, y), (x + j, y), grid, "C"))
                            

    def find_pawn_moves(self, x, y, grid, num_moves):
        enemyColor = ""
        pawnMoves = []
        #Checks to see what color. Assigns enemy color and the first move.
        #if it has not moved yet, then it attaches second move
        enemyColor = "B" if self.color == "W" else "W"
        dir = -1 if self.color == "W" else 1
        pawnMoves = [(x + 1, y + dir), (x - 1, y + dir), (x, y + dir)]
        if not self.moved: pawnMoves.append((x, y + 2*dir))

        #if any of the forward moves have pieces on them, remove them.
        for move in pawnMoves:
            if not(move[0] in range(8) and move[1] in range(8)): continue
            end_piece = grid[move[1]][move[0]]
            if (not end_piece and move[0] == x) or (end_piece and end_piece.color == enemyColor and move[0] != x):
                move_obj = Move((x, y), (move[0], move[1]), grid)
                self.moves.append(move_obj)
                if move[1] in [0, 7]: move_obj.flag = "P"
            elif end_piece and move[0] == x:
                break

        #en passant attack option
        #creates attack options
        en_passant_moves = [x for x in [(x - 1, y), (x + 1, y)] if all(map(lambda s: s < 8 and s >= 0, x))]
        for j in en_passant_moves:
            i = grid[j[1]][j[0]]
            #checks to see if there is a pawn of the opposite color that moved two squares on the move before
            if i and i.color == enemyColor and i.piece == "p" and num_moves == i.two_squares:
                self.moves.append(Move((x, y), (j[0], j[1]+dir), grid, "EP"))









    
            
