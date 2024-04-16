import pygame
import sys, os
from ChessSet import ChessSet
from copy import deepcopy
from collections import Counter
from multiprocessing import Process, Queue
import ChessAI
from PickleableSurface import PickleableSurface

pygame.Surface = PickleableSurface
pygame.surface.Surface = PickleableSurface


class ChessGame:   
    def __init__(self, piece_size, width = 0, time = 0, fps = 0, ai = None):
        self.time = time
        self.fps = fps
        #records if the player has clicked a piece and the possible moves they can make
        self.moves = []
        #records x and y coords of piece the player has selected, if any
        self.selected_piece = ()
        self.white_to_move = True
        #keeps track of highlighted squares (not including the square player has selected
        self.highlighted_squares = []
        #records how many moves have been made
        self.num_moves = 0
        #Keeps track of whether check has been done. 
        self.check = ""
        #1 is checkmate, 2 is stalemate
        self.mate = 0
        #whether a piece was captured on previous move for move notation
        self.capture = False
        #legal moves on the current turn before moving on to the next for move notation
        self.previous_legal_moves = {}
        #which flag was actually used in that move, if any
        self.used_flag = ""
        #keeps track of milliseconds left by each side
        self.timers = {"W" : self.time * 60000, "B" : self.time * 60000}
        #records time when move started
        self.move_start_time = 0
        #ai player color
        self.ai = ai
        self.ai_thinking = False
        self.move_finder_process = None
        self.move_log = [[None, [], '', {'W': [], 'B': []}]]
        self.player_move = None
        
        if width == 0:
            #if no width passed, uses default based on size of piece
            self.width = piece_size * 8
        else:
            self.width = width
        #sets height to that of 8 pieces
        self.height = piece_size * 8
        
        self.piece_size = piece_size
        
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Chess")
        
        #bg = pygame.image.load("Board.png").convert()
        #In case the width is not equal to height, board should be centered on the left.
        #In this case, width > height to keep some space on right
        #self.board = pygame.transform.scale(bg,(self.height, self.height))

        self.set = ChessSet()
        self.images = {}
        self.load_pieces()
        self.set.generate_legal_moves("W", self.num_moves)


    ############################        GAME MECHANICS              ################################

    def run_game(self):
        clock = pygame.time.Clock()
        self.move_start_time = pygame.time.get_ticks()
        run = True
        while run:
            #print(self.num_moves, len(self.move_log))
            if self.num_moves == len(self.move_log)-1:
                self.check_events()
            else:
                self.timeline_events()
            self.update_screen()

            if self.fps:
                clock.tick(self.fps)

    def timeline_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.move_back()
                if event.key == pygame.K_RIGHT:
                    self.move_fwd()
    
    def move_back(self):
        if self.num_moves > 0:
            self.move_log[self.num_moves][0].undo()
            self.num_moves -= 1
            self.highlighted_squares, self.check, captured = self.move_log[self.num_moves][1:]
            self.set.set_captured(captured)

    def move_fwd(self):
        if self.num_moves < len(self.move_log):
            self.num_moves += 1
            self.move_log[self.num_moves][0].do(self.num_moves)
            self.highlighted_squares, self.check, captured = self.move_log[self.num_moves][1:]
            self.set.set_captured(captured)

    def check_events(self):
        human_turn = (self.white_to_move and self.ai == "B") or (not self.white_to_move and self.ai == "W") or not self.ai
        # print(self.selected_piece)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.move_back()
            elif event.type == pygame.MOUSEBUTTONUP:
                x = pygame.mouse.get_pos()[0]
                #If the player clicks outside the board
                if x > self.piece_size * 8:
                    continue
                #Whether the player re clicked a selected square or made a move
                #Using it instead of else so player can switch pieces without unselecting the previous one
                dont_use_select = False
                #if the player has selected a piece already
                if self.selected_piece:
                    self.player_move = self.set.retrieve_move(self.selected_piece, self.find_mouse_square())
                    #if the square the player has selected has already been chosen, reset
                    if self.find_mouse_square() == self.selected_piece:
                        dont_use_select = True
                        self.selected_piece = ()
                        self.moves = []
                    #If player selects a move
                    elif self.player_move and human_turn:
                        previous_legal_moves = self.set.legal_moves
                        dont_use_select = True
                        # print(self.selected_piece)
                        piece_color = self.set.grid[self.selected_piece[1]][self.selected_piece[0]].color
                        #print(self.flag)
                        #if the player tries to make a special move
                        
                        self.capture = self.set.move(self.player_move, self.num_moves)
                        if self.player_move.flag == "P":
                            #moves the pawn to position, then asks question
                            self.highlighted_squares = [self.find_mouse_square(), self.selected_piece]
                            self.moves = []
                            self.draw_board()
                            pygame.display.update()
                            if not self.white_to_move:
                                print("")
                            CURSOR_UP_ONE = '\x1b[1A' 
                            ERASE_LINE = '\x1b[2K'
                            #while the input is not a piece
                            while True:
                                change_piece = input("What piece would you like to promote to? (q/r/b/n) ").lower()
                                if len(change_piece) == 1 and change_piece in "rqnb":
                                    break
                                sys.stdout.write(CURSOR_UP_ONE) 
                                sys.stdout.write(ERASE_LINE)
                                sys.stdout.flush()
                            
                            self.player_move.promote(piece_color + change_piece)

                        self.end_turn(previous_legal_moves)
                      
                    """elif self.find_mouse_square() in self.attack_squares:
                        dont_use_select = True
                        self.set.capture_piece(*self.selected_piece, *self.find_mouse_square())
                        self.highlighted_squares = []
                        self.highlighted_squares = [self.find_mouse_square(), self.selected_piece]
                        self.selected_piece = ()
                        self.moves = []
                        self.turn += 1"""

                if not dont_use_select:
                    self.select()

        if not human_turn:
            previous_legal_moves = self.set.legal_moves
            self.player_move = ChessAI.findBestMove(self.set, self.set.flattened, self.num_moves)
            if self.player_move is None:
                self.player_move = ChessAI.findRandomMove(self.set.flattened)
            # self.player_move = ChessAI.findRandomMove(self.set.flattened)
            self.capture = self.set.move(self.player_move, self.num_moves)
            if self.player_move.flag == "P": self.player_move.promote(self.ai + "q")
            # # self.num_moves += 1
            # if not self.ai_thinking:
            #     print("starting thinking")
            #     self.ai_thinking = True
            #     return_queue = Queue()  # used to pass data between threads
            #     flattened = list({x for v in self.set.legal_moves.values() for x in v})
            #     print("flattened list")
            #     move_finder_process = Process(target=ChessAI.findBestMove, args=(self.set, flattened, return_queue, self.num_moves))
            #     print("initialized process")
            #     move_finder_process.start()
            #     print("started process")

            # print(move_finder_process.is_alive())
            # if not move_finder_process.is_alive():
            #     print("i'm not alive")
            #     ai_move = return_queue.get()
            #     if ai_move is None:
            #         ai_move = ChessAI.findRandomMove(self.set.legal_moves)
            #     self.set.move(ai_move)
            #     self.highlighted_squares = [ai_move.start, ai_move.end]
            #     self.ai_thinking = False
            
            self.end_turn(previous_legal_moves)
            # print("is this running?")
    
    def end_turn(self, previous_legal_moves):
        opp_color = "W" if self.white_to_move else "B"
        self.timers[opp_color] = self.timers[opp_color] - (pygame.time.get_ticks() - self.move_start_time)
        self.white_to_move = not self.white_to_move
        color = "W" if self.white_to_move else "B"
        self.check = color if self.set.check_check(color) else ""
        self.set.generate_legal_moves(color, self.num_moves)
        self.num_moves += 1
        
        #print(self.set.legal_moves)
        #If the king is in check and there are no legal moves, checkmate
        self.highlighted_squares = [self.player_move.start, self.player_move.end]
        self.moves = []

        if self.set.no_moves:
            self.update_screen()
            if self.check:
                self.mate = 1
            else:
                self.mate = 2       

        self.set.write_move_notation(*self.player_move.start, *self.player_move.end,
                                       self.check, self.mate, self.player_move.flag, self.capture, previous_legal_moves, self.num_moves)

        self.move_log.append([self.player_move])
        self.move_log[len(self.move_log) - 1].extend([self.highlighted_squares, self.check, deepcopy(self.set.captured_pieces)])
        # print(self.move_log)
        self.selected_piece = ()
        self.capture = False
        self.player_move = None

        self.move_start_time = pygame.time.get_ticks()

        if self.mate:
            self.update_screen()
            if self.mate == 1:
                self.end_game(color)
            elif self.mate == 2:
                self.end_game(color, 1)

    def find_mouse_square(self):
        x, y = pygame.mouse.get_pos()
        #By dividing by piece_size, we find which square it is on
        x, y = x // self.piece_size, y // self.piece_size
        
        return (x, y)

    def select(self):
        x, y = self.find_mouse_square()
        turn_color = "W" if self.white_to_move else "B"
        #if there is a piece on the square
        if self.set.grid[y][x] and self.set.grid[y][x].color == turn_color:
            self.selected_piece = (x, y)
            self.moves = self.set.find_legal_moves(x, y)



    ################################           BOARD             ####################################

    def load_pieces(self):
        pieces = pygame.image.load("img\\chess_spritesheet.png")
        #Got this number from where I picked the spritesheet
        p_width = 128
        
        for y in range(0, p_width*2, p_width):
            for x in range(0, p_width*6, p_width):
                #creates a surface with dimensions of part we want to cut
                #SRCALPHA fixes some stuff which made the pieces background go black previously
                #Makes them transparent
                cropped = pygame.Surface((p_width, p_width), pygame.SRCALPHA)
                #blits the big picture at 0,0 on cropped and cuts out the rectangle
                #in the third parameter
                cropped.blit(pieces, (0, 0), (x, y, p_width, p_width))
                
                cropped = pygame.transform.scale(cropped, (self.piece_size, self.piece_size))

                if y == 0: #i.e. color is black
                    color = "B"
                else:
                    color = "W"

                j = x / p_width #makes it easier to index
                if j == 0:
                    piece = "p"

                elif j == 1:
                    piece = "n"

                elif j == 2:
                    piece = "b"

                elif j == 3:
                    piece = "r"

                elif j == 4:
                    piece = "q"

                elif j == 5:
                    piece = "k"

                #stores pieces in a dictionary by color and piece type
                self.images[color + piece] = cropped

    def draw_grid(self):
        DARK = (118, 150, 86)
        LIGHT = (238,238,210)

        for y in range(8):
            for x in range(8):
                if (x + y) % 2 == 0:
                    pygame.draw.rect(self.screen, LIGHT, (x * self.piece_size, y * self.piece_size, self.piece_size, self.piece_size))
                else:
                    pygame.draw.rect(self.screen, DARK, (x * self.piece_size, y * self.piece_size, self.piece_size, self.piece_size))

    def display_times(self):
        font = pygame.font.Font(None, self.piece_size // 2)
        turn_color = "W" if self.white_to_move else "B"
        mate = ""

        #Generating an output time
        for color in self.timers:
            timer = self.timers[color]
            
            if color == turn_color:
                current_time = pygame.time.get_ticks()

                #To counteract the effects of loading
                time_difference = timer - (current_time - self.move_start_time)
                if time_difference <= 0:
                    mate = True
            else:
                time_difference = timer

            seconds, milliseconds = divmod(time_difference, 1000)
            minutes, seconds = divmod(seconds, 60)
            milliseconds = str(milliseconds)[:2]

            text_color = (255, 255, 255) if color == "W" else (0, 0, 0)
            back_color = (255, 255, 255) if color == "B" else (0, 0, 0)

            if mate and turn_color == color:
                output = "00:00.00"
            else:
                output = f'{int(minutes):02d}:{int(seconds):02d}.{int(milliseconds):02d}'


            #blitting output time to screen

            text_color = (255, 255, 255) if color == "B" else (0, 0, 0)
            rect_color = (0, 0, 0) if color == "B" else (255, 255, 255)
            text = font.render(output, True, text_color)
            
            buffer = self.piece_size // 6
            board_size = self.piece_size * 8
            
            width = (self.width - board_size) - (buffer * 2)
            height = self.piece_size // 2
            x = board_size + buffer
            y = buffer if color == "B" else board_size - buffer - height
            
            text_rect = text.get_rect(center = (x + (width // 2), y + (height // 2)))
            
            pygame.draw.rect(self.screen, rect_color, (x, y, width, height), border_radius = 10)
            self.screen.blit(text, text_rect)

        if mate:
            self.end_game(turn_color, 2)

    def display_captured_pieces(self):
        font = pygame.font.Font(None, self.piece_size // 3)
        adv_font = pygame.font.Font(None, self.piece_size // 2)
        value_order = {"q" : 9, "r" : 5, "b" : 3, "n" : 3, "p" : 1}
        time_buffer = self.piece_size // 6
        buffer = self.piece_size // 7
        scale = 2
        #print(self.set.captured_pieces)
        
        for color in self.set.captured_pieces:
            opp_color = "W" if color == "B" else "B"
            counter = Counter(self.set.captured_pieces[color])
            for piece in counter:
                count = counter[piece]
                piece_image = self.images[opp_color + piece]
                piece_image = pygame.transform.scale(piece_image, (self.piece_size // scale, self.piece_size // scale))
                if color == "B":
                    y = time_buffer + (self.piece_size // 2) + buffer + list(value_order.keys()).index(piece) * self.piece_size // scale
                else:
                    y = (self.piece_size * 8) - time_buffer - (self.piece_size // 2) - buffer - (5 - list(value_order.keys()).index(piece)) * self.piece_size // scale

                x = self.piece_size * 8 + time_buffer
                self.screen.blit(piece_image, (x, y))

                text = font.render(f" x {count}", True, (217, 216, 212))
                text_rect = text.get_rect(midleft = (x + (self.piece_size // scale), y + (self.piece_size // scale) // 2))
                self.screen.blit(text, text_rect)

        board_pieces = [x.color + x.piece for y in self.set.grid for x in y if x]
        material_advantage = 0
        for x in board_pieces:
            if x[1] != "k":
                if x[0] == "W" : material_advantage += value_order[x[1]]
                else: material_advantage -= value_order[x[1]]

        if material_advantage:
            adv_x = int(self.piece_size * 9.5)
            adv_y = (self.piece_size * 8) // 4 if material_advantage < 0 else ((self.piece_size * 8) // 4) * 3

            text = adv_font.render("+" + str(abs(material_advantage)), True, (217, 216, 212))
            text_rect = text.get_rect(midleft = (adv_x, adv_y))
            self.screen.blit(text, text_rect)
        

    def draw_board(self):
        self.screen.fill((56,44,44))
        #self.screen.blit(self.board, (0,0))

        self.draw_grid()

        #transparent yellow square
        for x in self.highlighted_squares:
            #print("highlighted", x)
            if x:
                s = pygame.Surface((self.piece_size, self.piece_size), pygame.SRCALPHA)
                #Makes the square lighter if it is on a black square
                if sum(x) % 2 == 0:
                    pygame.draw.rect(s, (246,246,105,255), s.get_rect())
                else:
                    pygame.draw.rect(s, (186,202,43,255), s.get_rect())
                self.screen.blit(s, (x[0]*self.piece_size, x[1]*self.piece_size))


        if self.check:
            x, y = self.set.findKing("W") if self.check == "W" else self.set.findKing("B")
            s = pygame.Surface((self.piece_size, self.piece_size), pygame.SRCALPHA)
            if (x + y) % 2 == 0:
                pygame.draw.rect(s, (236,126,106,255), s.get_rect())
            else:
                pygame.draw.rect(s, (212,108,81,255), s.get_rect())

            self.screen.blit(s, (x*self.piece_size, y*self.piece_size))
            
        if self.selected_piece:
            radius = self.piece_size // 6
            attack_radius = self.piece_size // 2.1
            outline = self.piece_size // 10
            #transparent/outlined gray circle
            for x in self.moves:
                if x.is_attack_move:
                    s = pygame.Surface((self.piece_size, self.piece_size), pygame.SRCALPHA)
                    pygame.draw.circle(s, (180, 180, 180, 164), (self.piece_size // 2, self.piece_size // 2), attack_radius, outline)              
                    self.screen.blit(s, (x.end_x*self.piece_size, x.end_y*self.piece_size))
                else:
                    s = pygame.Surface((self.piece_size, self.piece_size), pygame.SRCALPHA)
                    pygame.draw.circle(s, (180, 180, 180, 130), (self.piece_size // 2, self.piece_size // 2), radius)
                    self.screen.blit(s, (x.end_x*self.piece_size, x.end_y*self.piece_size))

            #transparent yellow square
            s = pygame.Surface((self.piece_size, self.piece_size), pygame.SRCALPHA)
            if sum(self.selected_piece) % 2 == 0:
                pygame.draw.rect(s, (246,246,105,255), s.get_rect())
            else:
                pygame.draw.rect(s, (186,202,43,255), s.get_rect())
                
            self.screen.blit(s, (self.selected_piece[0]*self.piece_size, self.selected_piece[1]*self.piece_size))

            
        self.draw_pieces()
        if self.time:
            self.display_times()
        self.display_captured_pieces()

    def draw_pieces(self):
        for i, y in enumerate(self.set.grid):
            for j, x in enumerate(y):
                if x:
                    self.screen.blit(self.images[x.color + x.piece], (j*self.piece_size, i*self.piece_size))

    def update_screen(self):
        self.draw_board()
        pygame.display.update()



    #################################         MENUS         ################################


    def end_game(self, color, stalemate = 0):
        font = pygame.font.Font(None, self.piece_size // 2)
        #sets the scale for the pics
        scale = 2.5
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.move_back()
                    if event.key == pygame.K_RIGHT:
                        self.move_fwd()
                    self.update_screen()

            full_color = "white" if color == "W" else "black"
            opposite_color = "black" if full_color == "white" else "white"
            
            #Generates analysis icons for winner and loser
            if stalemate == 1:
                checkmate = pygame.image.load(f"img\\draw_{full_color}_128x.png")
                winner = pygame.image.load(f"img\\draw_{opposite_color}_128x.png")
            elif stalemate == 2:
                checkmate = pygame.image.load(f"img\\unnamed_clock_{full_color}_128x.png")
                winner = pygame.image.load(f"img\\winner_128x.png")
            else:
                checkmate = pygame.image.load(f"img\\checkmate_{full_color}_128x.png")
                winner = pygame.image.load("img\\winner_128x.png")

            #blits image to surface which supports transparency and resizes it
            mate = pygame.Surface((128, 128), pygame.SRCALPHA)
            mate.blit(checkmate, (0, 0))
            mate = pygame.transform.scale(mate, (self.piece_size // scale, self.piece_size // scale))

            win = pygame.Surface((128, 128), pygame.SRCALPHA)
            win.blit(winner, (0, 0))
            win = pygame.transform.scale(win, (self.piece_size // scale, self.piece_size // scale))

            #Finds coordinates of winning and losing king
            white = self.set.findKing("W") 
            black = self.set.findKing("B")
            winner, loser = (white, black) if color == "B" else (black, white)

            self.screen.blit(mate, (self.piece_size * (loser[0] + 0.65), self.piece_size * (loser[1] - 0.06)))
            self.screen.blit(win, (self.piece_size * (winner[0] + 0.65), self.piece_size * (winner[1] - 0.06)))

            buffer = self.piece_size // 5
            board_size = self.piece_size * 8
            #generates the string to be printed
            out_string = f"{opposite_color.capitalize()} Won" if stalemate in [0, 2] else "Draw"
            text = font.render(out_string, True, (217, 216, 212))
            width = text.get_rect().w
            height = text.get_rect().h
            text_rect = text.get_rect(center = (board_size + ((self.width - board_size) // 2), board_size // 2))

            self.screen.blit(text, text_rect)
            
            pygame.display.update()



    """def promotion_menu(self, color, x, y):
        direction = 
        p_run = True
        while p_run:
            for event in pygame.event.get:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()"""
                

#################################       START       ################################
    

if __name__ == "__main__":
    pygame.init()
    stop = False

    os.system("cls")

    while True:
        ai = input("Would you like to play against an AI? (B/W, or enter for human): ")
        os.system("cls")
        if ai:
            if ai.upper() in ["B", "W"]: 
                break
        else:
            break
    
    if not ai:
        while True:
            time = input("Minutes for each side (max 60, press 0 or enter for infinite time): ")
            if time:
                try:
                    time = int(time)
                    if time > 60:
                        time = 60
                        
                    elif time < 0:
                        time = 0
                        
                    stop = True
                        
                except ValueError:
                    pass
            else:
                time = 0
                stop = True

            os.system("cls")

            if stop:
                break
    else: time = 0

    width = 1000
    chessgame = ChessGame(94, fps = 60, width = 960, time = time, ai = ai.upper())
    chessgame.run_game()











    """def animate_move(self, x, y, move_x, move_y, moved_piece):
        self.attack_squares = []
        self.highlighted_squares = []
        self.moves = []
        #how much time the object takes to move 
        time = 10

        pixel_x = x * self.piece_size
        pixel_y = y * self.piece_size

        pixel_move_x = move_x * self.piece_size
        pixel_move_y = move_y * self.piece_size

        #print(x, move_x)
        x_diff = pixel_move_x - pixel_x
        y_diff = pixel_move_y - pixel_y

        #print(x_diff, y_diff)

        x_speed = round(x_diff // time)
        y_speed = round(y_diff // time)
        #print(x_speed, y_speed)


        #print(x_speed)
        #print(y_speed)

        self.set.grid[y][x] = ""
        #print(self.set.grid[y][x])
        self.draw_board()

        #print(pixel_x, pixel_move_x, pixel_y, pixel_move_y)

        while True:
            if pixel_x != pixel_move_x or pixel_y != pixel_move_y:
                self.draw_board()
                
                pixel_x += x_speed
                pixel_y += y_speed

                #print(pixel_x, pixel_y)

                image = self.set.pieces[moved_piece.color + moved_piece.piece][2]
                self.screen.blit(image, (pixel_x, pixel_y))

                pygame.display.update()
            else:
                break

            #clock1.tick(self.fps)

        self.set.grid[y][x] = moved_piece"""
