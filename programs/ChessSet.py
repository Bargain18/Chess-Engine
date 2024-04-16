import pygame
from Piece import Piece
from copy import deepcopy
import sys
import os
from PickleableSurface import PickleableSurface

pygame.Surface = PickleableSurface
pygame.surface.Surface = PickleableSurface

class ChessSet:
    def __init__(self):
        self.pieces = {}
        self.legal_moves = {}
        self.flattened = []
        self.no_moves = ""
        self.grid = [["" for y in range(8)] for x in range(8)]
        #Used to print and maintain move notation lines
        self.line = ""
        self.captured_pieces = {"W" : [], "B" : []}
        self.init_set()
        #this is to add to number of moves after two squares for en passant
        #self.pawns = [x for y in self.grid for x in y if x and x.piece == "p"] 

    def init_set(self):
        #Moves from 8th to 1st rank in rows, then a to h in columns
        #perspective of white
        row = ["r", "n", "b", "q", "k", "b", "n", "r"]
        for x in range(8):
            self.grid[0][x] = Piece("B", row[x])
            
            self.grid[7][x] = Piece("W", row[x])
            
            self.grid[1][x] = Piece(*"Bp")
            self.grid[6][x] = Piece(*"Wp")
            
        # self.w_king_loc = (4, 7)
        # self.b_king_loc = (4, 0)


    def create_piece(self, color, piece, x, y):
        self.grid[y][x] = Piece(*self.pieces[color + piece])

    """def return_piece(self, color, piece):    
        return Piece(*self.pieces[color + piece])"""

    def check_check(self, color, king_coords = ()):
        #arg is used for castle to check if any spaces are attacked
        if king_coords:
            king_x, king_y = king_coords
        else:
            king_x, king_y = self.findKing("W") if color == "W" else self.findKing("B")

        #print(king_x, king_y)

        #all queen movements
        directions = ((-1, -1), (1, 1), (-1, 1), (1, -1), (1, 0), (0, 1), (0, -1), (-1, 0))
        bishop = ((-1, -1), (1, 1), (-1, 1), (1, -1))
        rook = ((1, 0), (0, 1), (0, -1), (-1, 0))

        for direction in directions:
            for i in range(1, 8):
                endCol = king_x + direction[0] * i
                endRow = king_y + direction[1] * i

                if not(endRow in range(8) and endCol in range(8)): break
                endPiece = self.grid[endRow][endCol]
                if not endPiece: continue
                if endPiece.color == color: break
                if endPiece.piece == "k" and i == 1:
                    return True
                
                if direction in bishop:
                    if endPiece.piece in ["b", "q"]: 
                        return True
                    elif endPiece.piece == "p":
                        pawn_moves = ((-1, 1), (1, 1)) if color == "B" else ((-1, -1), (1, -1))
                        if direction in pawn_moves and i == 1:
                            return True
                    break
                        
                elif direction in rook:
                    if endPiece.piece in ["r", "q"]:
                        return True
                    break
                
        knight_directions = ((2, -1), (2, 1), (-2, -1), (-2, 1), (1, 2), (-1, 2), (1, -2), (-1, -2))
        #print(knight_directions)
        #print(king_x, king_y)

        for direction in knight_directions:
            #print(direction)
            endCol = king_x + direction[0]
            endRow = king_y + direction[1]
            if not(endRow in range(8) and endCol in range(8)): continue
            endPiece = self.grid[endRow][endCol]
            if endPiece and endPiece.color != color and endPiece.piece == "n":
                return True
        return False

    def generate_pseudo_legal_moves(self, color, num_moves):
        pseudo = {}
        for y, row in enumerate(self.grid):
            for x, square in enumerate(row):
                #if there is a piece on that square
                if square and square.color == color:
                    #print(square)
                    #stores moves and flags in a dictionary by coordinates
                    pseudo[(x, y)] = square.find_available_pos(x, y, self, num_moves)

        return pseudo

    def generate_legal_moves(self, color, num_moves):
        self.legal_moves = {}
        self.flattened = []
        pseudo_legal_moves = self.generate_pseudo_legal_moves(color, num_moves)
        for coord in pseudo_legal_moves:
            legal_piece_moves = []
            moves = pseudo_legal_moves[coord]
            for move in moves:
                if move.flag == "C":                  
                    legal_piece_moves.append(move)
                    continue

                move.do(num_moves)
                if not self.check_check(color):
                    legal_piece_moves.append(move)
                move.undo()

            self.legal_moves[coord] = legal_piece_moves
            self.flattened.extend(legal_piece_moves)

        self.no_moves = not any(self.legal_moves.values())
        #print(self.legal_moves)
        return self.legal_moves

        #print(self.grid)
        #print(self.legal_moves)
        #self.pseudo_legal_moves = pseudo_legal_moves
    
    def retrieve_move(self, piece, move):
        for i in self.legal_moves[piece]:
            if (i.end_x, i.end_y) == move:
                return i
        return False
    
    def move(self, move, num_moves):
        capture = move.do(num_moves)
        if capture:
            self.captured_pieces[move.piece.color].append(capture.piece)
            return True
        return False
    
    def set_captured(self, captured):
        self.captured_pieces = captured

    # def doCopyMove(self, square_x, square_y, move_x, move_y, flag):
    #     copy_grid = deepcopy(self.grid)
    #     self.move_piece(square_y, square_x, move_y, move_x, used_grid = copy_grid)
    #     if flag:
    #         if flag == "C":
    #             #The rook is to the right
    #             if move_y > square_y:
    #                 self.set.move_piece(7, square_y, 5, square_y, game = self, used_grid = copy_grid)
    #             else:
    #                 self.set.move_piece(0, square_y, 3, square_y, game = self, used_grid = copy_grid)
    #         elif flag == "P":
    #             self.create_piece(copy_grid[move_y][move_x].color, "q", move_y, move_x, used_grid = copy_grid)
    #         elif flag == "EP":
    #             direction = 1 if copy_grid[move_y][move_x] == "W" else -1
    #             copy_grid[move_y + direction][move_x] = ""
    #     return copy_grid

    def findKing(self, color):
        for y in range(len(self.grid)):
            for x in range(len(self.grid[y])):
                if not self.grid[y][x]: continue
                piece = self.grid[y][x]
                if piece.color == color and piece.piece == "k":
                    return (x, y) 


    def find_legal_moves(self, x, y):
        return self.legal_moves[(x, y)]

    def write_move_notation(self, x, y, move_x, move_y, check, mate, flag, capture, previous_legal_moves, num_moves):
        #print(flag)
        moved_piece = self.grid[move_y][move_x]

        if num_moves % 2 == 1 and flag != "P":
            var = str(int((num_moves + 1) / 2)) + "."
            print(f"{ var : <4}", end = "")
            self.line += var.ljust(4)
        
        files = "abcdefgh"
        mate_n = ""
        if mate == 1:
            mate_n = "#"
        elif check:
            mate_n = "+"
            
        if flag == "C":
            if move_x == 6:
                print("O-O", end = " ", flush = True)
                self.line += "O-O "
            else:
                print("O-O-O", end = " ", flush = True)
                self.line += "O-O-O "
                
        elif flag == "P":
            #Uses ANSI escape sequences to go back one line and erase the question of which piece
            os.system("")
            CURSOR_UP_ONE = '\x1b[1A' 
            ERASE_LINE = '\x1b[2K'
            sys.stdout.write(CURSOR_UP_ONE) 
            sys.stdout.write(ERASE_LINE)
            
            if moved_piece.color == "B":
                sys.stdout.write(CURSOR_UP_ONE)
                sys.stdout.write(ERASE_LINE)
                sys.stdout.write(CURSOR_UP_ONE)
                sys.stdout.write(self.line)
                
            else:
                var = str(int((num_moves + 1) / 2)) + "."
                self.line += var.ljust(4)
                
                print(f"{ var : <4}", end = "")



            #If there was a capture, add file and x to beginning
            #capture: fxe4 = Q
            #move: e4 = Q
            if capture:
                self.line += files[x] + "x"
                
                print(files[x] + "x", end = "")


            self.line += files[move_x] + str(8 - move_y) + " = " + moved_piece.piece.upper() + mate_n + " "
            #Either way, print "e4" If the opposite king is put into check afterwards, write + or #
            print(files[move_x] + str(8 - move_y) + " = " + moved_piece.piece.upper() + mate_n, end = " ", flush = True)


        elif flag == "EP":
            print(files[x] + "x" + files[move_x] + str(8 - move_y) + mate_n, end = " ", flush = True)
            self.line += files[x] + "x" + files[move_x] + str(8 - move_y) + mate_n + " "
            
            
        else:
            piece = moved_piece.piece.upper() if moved_piece.piece != "p" else ""
            #added the conditional bc if no piece, then piece is pawn
            #pawns can never move to the same square as another pawn unless capturing, and they can always be distinguished
            if piece:
                print(piece, end = "")
                self.line += piece


                #file and rank hold bools which see if there is a piece of that type which can move to that square on the same file or rank or both
                file = False
                rank = False
                #detail = False
                
                #Gets all other pieces on the board which are the same type as the one moved (doesn't include moved_piece)
                same_type_pieces = [(x, y) for y in range(8) for x in range(8) if (self.grid[y][x] and self.grid[y][x].piece == moved_piece.piece
                                    and self.grid[y][x].color == moved_piece.color and self.grid[y][x] != moved_piece)]

                
                
                for same_x, same_y in same_type_pieces:
                    same_all = previous_legal_moves[(same_x, same_y)]
                    same_moves = [x for x in same_all if not x.flag]

                    #If this piece can move to designated square, add it to list
                    if (move_x, move_y) in same_moves:
                        #same_move_pieces.append((same_x, same_y))
                        if same_x == x:
                            file = True
                        elif same_y == y:
                            rank = True

                #print(rank, file, detail)

                if file and rank:
                    self.line += files[x] + str(8 - y)
                    print(files[x] + str(8 - y), end = "")
                elif file:
                    self.line += str(8 - y)
                    print(str(8 - y), end = "")
                elif rank:
                    self.line += files[x]
                    print(files[x], end = "")




                if capture:
                    print("x", end = "")
                    self.line += "x"

                self.line += files[move_x] + str(8 - move_y) + mate_n + " "
                print(files[move_x] + str(8 - move_y) + mate_n, end = " ", flush = True)
                    
            else:
                if capture:
                    print(files[x] + "x" + files[move_x] + str(8 - move_y) + mate_n, end = " ", flush = True)
                    self.line += files[x] + "x" + files[move_x] + str(8 - move_y) + mate_n + " "

                else:
                    print(files[move_x] + str(8 - move_y) + mate_n, end = " ", flush = True)
                    self.line += files[move_x] + str(8 - move_y) + mate_n + " "

        if num_moves % 2 == 0:
            print("")
            self.line = ""
                

    #Future Reference
    """q = self.return_piece(color, "q")
    n = self.return_piece(color, "n")
    
    #gets attack_squares
    line_atk_squares = q.find_available_pos(king_x, king_y, self)[1]

    for square in line_atk_squares:
        #checking whether the square is on the same line as the king
        if (square[0] == king_x or square[1] == king_y) and grid[square[1]][square[0]].piece in ["r", "q"]:
            return True
        #if the attack_square came from a diagonal move
        else:
            if grid[square[1]][square[0]].piece == "b":
                return True
            
    knight_atk_squares = n.find_available_pos(king_x, king_y, self)[1]

    for square in knight_atk_squares:
        if square.piece == "n":
            return True

    if color == "b":
        direction = 1
    else:
        direction = -1

    for j in [1, -1]:
        if grid[y + direction][x + j]:
            if grid[y + direction][x + j].color != color and grid[y + direction][x + j].piece == "p":
                return True"""


"""def maybe_generate_legal_moves(self, color, num_moves):
        pseudo_legal_moves = self.generate_pseudo_legal_moves(color, num_moves)
        #This is the list of all legal moves. It is organized in the same way as the pseudo-legal
        #move list except that attack_squares is another element
        self.legal_moves = {}

        for coord in pseudo_legal_moves:
            x, y = coord
            moves, full_flag = pseudo_legal_moves[coord]
            if full_flag:
                flag, flag_moves = full_flag

            legal_moves = []
            legal_flags = []
            legal_attack_squares = []

            for move in moves:
                copy_grid = deepcopy(self.grid)
                self.move_piece(x, y, *move, used_grid = copy_grid)

                if self.grid[y][x].piece == "k" and move == (4, 5):
                    print("this move has check:", self.check_check(color, used_grid = copy_grid))

                if self.grid[y][x].piece == "k":
                    check_check = self.check_check(color, king_coords = move, used_grid = copy_grid)
                else:
                    check_check = self.check_check(color, used_grid = copy_grid)

                if not check_check:
                    new_x, new_y = move

                    if self.grid[new_y][new_x]:
                        legal_attack_squares.append(move)
                    else:
                        legal_moves.append(move)


            self.legal_moves[coord] = (legal_moves, legal_attack_squares, legal_flags)"""
        
