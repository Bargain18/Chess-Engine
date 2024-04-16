class Move:
    def __init__(self, start, end, grid, flag = None, promote_to = None):
        self.start = start
        self.start_x = start[0]
        self.start_y = start[1]
        self.piece = grid[self.start_y][self.start_x]
        self.end = end
        self.end_x = end[0]
        self.end_y = end[1]
        self.grid = grid
        self.flag = flag
        self.done = False
        self.promote_to = promote_to
            
        
        if self.flag != "EP":
            self.captured_x = self.end_x
            self.captured_y = self.end_y 
        else:
            direction = 1 if self.piece.color == "W" else -1
            self.captured_x = self.end_x
            self.captured_y = self.end_y + direction
        
        self.captured_piece = grid[self.captured_y][self.captured_x]    
        self.is_attack_move = True if grid[self.end_y][self.end_x] != "" else False

        self.two_squares = False
        self.moved = False
    
    def equal(self, move):
        return [self.start, self.end, self.flag, self]

    def do(self, num_moves):
        self.done = True
        self.grid[self.start_y][self.start_x] = ""
        self.grid[self.captured_y][self.captured_x] = ""
        self.grid[self.end_y][self.end_x] = self.piece
        
        if self.piece.piece in ["p", "r", "k"] and not self.piece.moved:
            self.piece.moved = True
            self.moved = True
        
        #Checks to see if pawn moved two squares
        if abs(self.start_y - self.end_y) == 2 and self.piece.piece == "p":
            self.piece.two_squares = num_moves
            self.two_squares = True
                
        if self.flag == "P":
            if self.promote_to:
                self.promote(self.promote_to)
        elif self.flag == "C":
            if self.end_x > self.start_x:
                self.grid[self.start_y][5] = self.grid[self.start_y][7]
                self.grid[self.start_y][7] = ""
            else:
                self.grid[self.start_y][3] = self.grid[self.start_y][0]
                self.grid[self.start_y][0] = ""
        
        return self.captured_piece

    def undo(self):
        if not self.done: return
        self.done = False

        self.grid[self.start_y][self.start_x] = self.piece
        self.grid[self.end_y][self.end_x] = ""
        self.grid[self.captured_y][self.captured_x] = self.captured_piece
        
        if self.moved:
            self.piece.moved = False
            self.moved = False
        
        #Checks to see if pawn moved two squares
        if self.two_squares:
            self.piece.two_squares = 0
            self.two_squares = False
                

        if self.flag == "C":
            if self.end_x > self.start_x:
                self.grid[self.start_y][7] = self.grid[self.start_y][5]
                self.grid[self.start_y][5] = ""
            else:
                self.grid[self.start_y][0] = self.grid[self.start_y][3]
                self.grid[self.start_y][3] = ""

    def promote(self, str_piece):
        if self.flag == "P" and str_piece[1] in "rqnb":
            from Piece import Piece
            self.promoted_piece = Piece(str_piece[0], str_piece[1])
            self.grid[self.end_y][self.end_x] = self.promoted_piece