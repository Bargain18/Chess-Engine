from itertools import product, count
import ChessSet
                
class Piece:
    def __init__(self, color, piece):
        self.color = color
        self.piece = piece
        #Flag used for special moves like promotion, castle, and en passant
        self.flag = []
        #creates attribute to check whether pawn, rook, or king has been moved or not.
        if self.piece in ["p", "k", "r"]:
            self.moved = False
            #records at which move the pawn moved two squares
            #and seeing if all other conditions are met for the second to be true
            if self.piece == "p":
                self.two_squares = 0
        

        self.coords = []
        self.attack_squares = []

    def find_available_pos(self, x, y, board, num_moves = None):
        grid = board.grid
        #print(grid)
        self.coords = []
        self.attack_squares = []
        self.flag = []
        if self.piece == "b" or self.piece == "q":
            self.find_diagonals(x, y, grid)
        if self.piece == "r" or self.piece == "q":
            self.find_rook_moves(x, y, grid)
        elif self.piece == "n":
            self.find_l(x, y, grid)
        elif self.piece == "k":
            self.find_king_moves(x, y, grid, board)
        elif self.piece == "p":
            self.find_pawn_moves(x, y, grid, num_moves)

        #print(self.coords, self.attack_squares)
        return self.coords, self.attack_squares, self.flag
            
    def find_diagonals(self, x, y, grid):
        directions = [(-1, -1), (1, 1), (1, -1), (-1, 1)]
        enemyColor = "B" if grid[y][x].color == "W" else "W"

        for direction in directions: 
            for j in range(1, 8):
                endRow = y + direction[1] * j
                endCol = x + direction[0] * j

                if endRow < 8 and endRow >= 0 and endCol < 8 and endCol >= 0:
                    endPiece = grid[endRow][endCol]
                    if endPiece:
                        if endPiece.color == enemyColor:
                            self.attack_squares.append((endCol, endRow))
                            break
                        else:
                            break
                    else:
                        self.coords.append((endCol, endRow))
                else:
                    break

                

    def find_rook_moves(self, x, y, grid):
        directions = [(0, -1), (0, 1), (1, 0), (-1, 0)]
        enemyColor = "B" if grid[y][x].color == "W" else "W"

        for direction in directions:
            for j in range(1, 8):
                endRow = y + direction[1] * j
                endCol = x + direction[0] * j

                if endRow < 8 and endRow >= 0 and endCol < 8 and endCol >= 0:
                    endPiece = grid[endRow][endCol]
                    if endPiece:
                        if endPiece.color == enemyColor:
                            self.attack_squares.append((endCol, endRow))
                            break
                        else:
                            break
                    else:
                        self.coords.append((endCol, endRow))
                else:
                    break

    def find_l(self, x, y, grid):
        enemyColor = "B" if grid[y][x].color == "W" else "W"
        #finds all permutations of 2s and 1s for knight
        j = list(product([x + 1, x - 1], [y + 2, y - 2])) + list(product([x + 2, x - 2], [y + 1, y - 1]))
        #removes all out of bounds
        j = [i for i in j if all(map(lambda x: x < 8 and x >= 0, i))]
        new_j = j.copy()
        for move in j:
            if grid[move[1]][move[0]]:
                if grid[move[1]][move[0]].color == enemyColor:
                    self.attack_squares.append((move[0], move[1]))
                else:
                    #Using new_j because removing elements during iteration of list can cause it to skip indexes
                    new_j.remove((move[0], move[1]))

        #removes all the ones in attack_squares
        self.coords = [x for x in new_j if x not in self.attack_squares]

    def find_king_moves(self, x, y, grid, chess_set):
        enemyColor = "B" if grid[y][x].color == "W" else "W"
        j = list(product([x - 1, x, x + 1], [y - 1, y, y + 1]))
        j = [i for i in j if all(map(lambda x: x < 8 and x >= 0, i))]
        #Removes the one you're already on
        j.remove((x,y))
        new_j = j.copy()
        for move in j:
            if grid[move[1]][move[0]]:
                if grid[move[1]][move[0]].color == enemyColor:
                    self.attack_squares.append((move[0],move[1]))
                else:
                    new_j.remove((move[0], move[1]))

        self.coords = [x for x in new_j if x not in self.attack_squares]
            

        castle_moves = []
        #if the king hasn't moved
        if not grid[y][x].moved:
            #print("King hasn't moved")
            #checks whether king is in check
            if not chess_set.check_check(grid[y][x].color):
                #gets both rook squares at the edges of the board
                for rook_x, rook_y in [(0, y), (7, y)]:
                    #if there is a piece on that square
                    if grid[rook_y][rook_x]:
                        #print("Piece is there")
                        #if the piece is a rook of the same color
                        if grid[rook_y][rook_x].piece == "r" and grid[rook_y][rook_x].color != enemyColor:
                            #print(rook_x, rook_y, "Rook of same color is there")
                            #if that rook hasn't moved
                            if not grid[rook_y][rook_x].moved:
                                castle_possible = True
                                #print(rook_x, rook_y, "Rook hasn't moved")
                                if rook_x == 7:
                                    #print("rook 7")
                                    #goes through all the squares between those two squares
                                    for i in range(x + 1, 7):
                                        #checks if they're empty
                                        if grid[y][i]:
                                            #print(i, y, grid[y][i].color, grid[y][i].piece)
                                            #print("squares are not empty")
                                            castle_possible = False
                                            break
                                        #checks if they are attacked using check
                                        elif chess_set.check_check(grid[y][x].color, king_coords = (i, y)):
                                            #print(i, "this square is attacked")
                                            castle_possible = False
                                            break
                                    
                                elif rook_x == 0:
                                    #print("rook 1")
                                    for i in range(1, x):
                                        if grid[y][i]:
                                            #print(i, y, grid[y][i].color, grid[y][i].piece)
                                            #print("squares are not empty")
                                            castle_possible = False
                                            break
                                        elif chess_set.check_check(grid[y][x].color, king_coords = (i, y)):
                                            #print(i, "this square is attacked")
                                            castle_possible = False
                                            break

                                if castle_possible:
                                    #print("Castle is possible")
                                    j = 2 if rook_x == 7 else -2
                                    self.coords.append((x + j, y))
                                    castle_moves.append((x + j, y))
                                    #print(castle_moves)

        if castle_moves:
            self.flag = ["C", castle_moves]
                            

    def find_pawn_moves(self, x, y, grid, num_moves):
        enemyColor = ""
        pawnMoves = []
        atk_squares = []
        func = lambda s: s < 8 and s >= 0
        #Checks to see what color. Assigns enemy color and the first move.
        #if it has not moved yet, then it attaches second move
        if self.color == "W":
            enemyColor = "B"
            pawnMoves = [(x, y - 1)]
            if not self.moved: pawnMoves.append((x, y - 2))
            atk_squares = [(x + 1, y - 1), (x - 1, y - 1)]
        else:
            enemyColor = "W"
            pawnMoves = [(x, y + 1)]
            if not self.moved: pawnMoves.append((x, y + 2))
            atk_squares = [(x + 1,  y + 1), (x - 1, y + 1)]

        #removes all that are out of bounds
        pawnMoves = [x for x in pawnMoves if all(map(func, x))]
        atk_squares = [x for x in atk_squares if all(map(func, x))]

        #if any of the forward moves have pieces on them, remove them.
        for move in pawnMoves:
            if grid[move[1]][move[0]]:
                break
            else:
                self.coords.append((move[0], move[1]))

        #only adds those moves which has pieces of the opposite color on it
        for move in atk_squares:
            end_piece = grid[move[1]][move[0]]
            if end_piece:
                if end_piece.color == enemyColor:
                    self.attack_squares.append(move)

        #en passant attack option
        #creates attack options
        en_passant_moves = [x for x in [(x - 1, y), (x + 1, y)] if all(map(func, x))]
        for j in en_passant_moves:
            i = grid[j[1]][j[0]]
            #checks to see if there is a pawn of the opposite color that moved two squares on the move before
            if i:
                if i.color == enemyColor and i.piece == "p" and num_moves == i.two_squares:
                    #appends that move to coords and adds a flag
                    if enemyColor == "B":
                        self.coords.append((j[0], j[1] - 1))
                        self.flag = ["EP", [(j[0], j[1] - 1)]]
                    else:
                        self.coords.append((j[0], j[1] + 1))
                        self.flag = ["EP", [(j[0], j[1] + 1)]]

        #promotion
        promotion_moves = []
        #goes through all possible moves for pawn
        for i in self.coords + self.attack_squares:
            x, y = i
            #checks to see if any move goes to last row
            if y in [0, 7]:
                promotion_moves.append(i)

        #flag becomes list of moves if any moves can be promotion moves
        if promotion_moves:
            self.flag = ["P", promotion_moves]









    
            
