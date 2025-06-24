import tkinter as tk
from tkinter import messagebox as mb, dialog as d
info="HI"

import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QGraphicsScene, QGraphicsView, 
                            QGraphicsPixmapItem, QGraphicsRectItem, QVBoxLayout, QWidget, 
                            QPushButton, QHBoxLayout, QGraphicsEllipseItem, QLabel, 
                            QMessageBox, QDialog, QGridLayout, QFrame)
from PyQt5.QtGui import QPixmap, QColor, QBrush, QPainter, QIcon, QFont
from PyQt5.QtCore import QRectF, Qt, QTimer

class ChessLogic:
    def __init__(self):
        self.board = self.create_initial_board()
        self.current_turn = 'w'  # White starts first
        self.game_over = False
        self.winner = None
        self.move_history = []
        self.captured_pieces = {'w': [], 'b': []}
        self.kings_moved = {'w': False, 'b': False}
        self.rooks_moved = {
            'w': {'kingside': False, 'queenside': False},
            'b': {'kingside': False, 'queenside': False}
        }

    def create_initial_board(self):
        """Create the initial chess board with pieces in their starting positions."""
        board = [[None] * 8 for _ in range(8)]

        # White pieces (row 6 and 7)
        board[7] = ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']
        board[6] = ['wP'] * 8

        # Black pieces (row 0 and 1)
        board[0] = ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR']
        board[1] = ['bP'] * 8

        return board

    def get_piece(self, row, col):
        """Return the piece at the specified position."""
        if 0 <= row < 8 and 0 <= col < 8:
            return self.board[row][col]
        return None

    def place_piece(self, row, col, piece):
        """Place a piece at the specified position."""
        self.board[row][col] = piece

    def is_opponent_in_check(self, color):
        """Check if the opponent's king is in check."""
        opponent_color = 'b' if color == 'w' else 'w'
        king_pos = self.find_king(opponent_color)
        
        if not king_pos:
            return False
            
        # Check if any piece of current player can attack the opponent's king
        for r in range(8):
            for c in range(8):
                piece = self.get_piece(r, c)
                if piece and piece[0] == color:
                    valid_moves = self.highlight_moves((r, c), check_for_check=False)
                    if king_pos in valid_moves:
                        return True
        return False

    def find_king(self, color):
        """Find the position of the king with the specified color."""
        for r in range(8):
            for c in range(8):
                piece = self.get_piece(r, c)
                if piece and piece[0] == color and piece[1] == 'K':
                    return (r, c)
        return None

    def is_checkmate(self, color):
        """Check if the player with the given color is in checkmate."""
        # If king is not in check, it's not checkmate
        if not self.is_opponent_in_check(('b' if color == 'w' else 'w')):
            return False
            
        # Try all possible moves for all pieces of the given color
        for r in range(8):
            for c in range(8):
                piece = self.get_piece(r, c)
                if piece and piece[0] == color:
                    valid_moves = self.highlight_moves((r, c))
                    for move in valid_moves:
                        # Try the move and see if it gets out of check
                        temp_piece = self.get_piece(move[0], move[1])
                        self.board[move[0]][move[1]] = piece
                        self.board[r][c] = None
                        
                        # Check if king is still in check after the move
                        still_in_check = self.is_opponent_in_check(('b' if color == 'w' else 'w'))
                        
                        # Undo the move
                        self.board[r][c] = piece
                        self.board[move[0]][move[1]] = temp_piece
                        
                        if not still_in_check:
                            # Found a move that gets out of check
                            return False
        
        # No move gets out of check, so it's checkmate
        return True

    def is_stalemate(self, color):
        """Check if the player with the given color is in stalemate."""
        # If king is in check, it's not stalemate
        if self.is_opponent_in_check(('b' if color == 'w' else 'w')):
            return False
            
        # Check if the player has any legal moves
        for r in range(8):
            for c in range(8):
                piece = self.get_piece(r, c)
                if piece and piece[0] == color:
                    valid_moves = self.highlight_moves((r, c))
                    if valid_moves:
                        return False
        
        # No legal moves and not in check, so it's stalemate
        return True

    def highlight_moves(self, selected_pos, check_for_check=True):
        """Highlight valid moves based on the selected piece's type and position."""
        row, col = selected_pos
        piece = self.get_piece(row, col)
        if piece is None:
            return []
            
        piece_color = piece[0]  # 'w' for white, 'b' for black
        valid_moves = []
        
        if piece[1] == 'P':
            valid_moves = self.highlight_pawn_moves(row, col, piece_color)
        elif piece[1] == 'R':
            valid_moves = self.highlight_rook_moves(row, col, piece_color)
        elif piece[1] == 'N':
            valid_moves = self.highlight_knight_moves(row, col, piece_color)
        elif piece[1] == 'B':
            valid_moves = self.highlight_bishop_moves(row, col, piece_color)
        elif piece[1] == 'Q':
            valid_moves = self.highlight_queen_moves(row, col, piece_color)
        elif piece[1] == 'K':
            valid_moves = self.highlight_king_moves(row, col, piece_color)
            
        # Filter out moves that would put the king in check
        if check_for_check:
            legal_moves = []
            for move in valid_moves:
                # Try the move
                dest_row, dest_col = move
                temp_piece = self.get_piece(dest_row, dest_col)
                
                # Make the move
                self.board[dest_row][dest_col] = piece
                self.board[row][col] = None
                
                # Check if the king is in check after the move
                king_pos = self.find_king(piece_color)
                king_in_check = False
                
                # Check if any opponent piece can attack the king
                opponent_color = 'b' if piece_color == 'w' else 'w'
                for r in range(8):
                    for c in range(8):
                        opponent_piece = self.get_piece(r, c)
                        if opponent_piece and opponent_piece[0] == opponent_color:
                            opponent_moves = self.highlight_moves((r, c), check_for_check=False)
                            if king_pos in opponent_moves:
                                king_in_check = True
                                break
                    if king_in_check:
                        break
                
                # Undo the move
                self.board[row][col] = piece
                self.board[dest_row][dest_col] = temp_piece
                
                # If the king is not in check, the move is legal
                if not king_in_check:
                    legal_moves.append(move)
                    
            return legal_moves
        
        return valid_moves

    def highlight_pawn_moves(self, row, col, color):
        """Return valid moves for a pawn based on its position and color."""
        valid_moves = []
        direction = -1 if color == 'w' else 1  # White pawns move up (decreasing row), black pawns move down
        start_row = 6 if color == 'w' else 1  # Starting row for pawns

        # Normal move (1 square forward)
        if 0 <= row + direction < 8 and self.get_piece(row + direction, col) is None:
            valid_moves.append((row + direction, col))
            
            # Double move from starting position
            if row == start_row and self.get_piece(row + 2*direction, col) is None:
                valid_moves.append((row + 2*direction, col))

        # Capture moves (diagonally)
        for dc in [-1, 1]:
            if 0 <= row + direction < 8 and 0 <= col + dc < 8:
                piece_to_capture = self.get_piece(row + direction, col + dc)
                if piece_to_capture and piece_to_capture[0] != color:
                    valid_moves.append((row + direction, col + dc))

        return valid_moves

    def highlight_rook_moves(self, row, col, color):
        """Return valid moves for a rook based on its position and color."""
        valid_moves = []

        # Horizontal and vertical directions
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            r, c = row, col
            while True:
                r += dr
                c += dc
                if not (0 <= r < 8 and 0 <= c < 8):
                    break
                piece = self.get_piece(r, c)
                if piece is None:
                    valid_moves.append((r, c))
                elif piece[0] != color:
                    valid_moves.append((r, c))
                    break
                else:
                    break
        return valid_moves

    def highlight_knight_moves(self, row, col, color):
        """Return valid moves for a knight based on its position and color."""
        valid_moves = []
        knight_moves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
        for dr, dc in knight_moves:
            r, c = row + dr, col + dc
            if 0 <= r < 8 and 0 <= c < 8:
                piece = self.get_piece(r, c)
                if piece is None or piece[0] != color:
                    valid_moves.append((r, c))
        return valid_moves

    def highlight_bishop_moves(self, row, col, color):
        """Return valid moves for a bishop based on its position and color."""
        valid_moves = []

        # Diagonal directions
        for dr, dc in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            r, c = row, col
            while True:
                r += dr
                c += dc
                if not (0 <= r < 8 and 0 <= c < 8):
                    break
                piece = self.get_piece(r, c)
                if piece is None:
                    valid_moves.append((r, c))
                elif piece[0] != color:
                    valid_moves.append((r, c))
                    break
                else:
                    break
        return valid_moves

    def highlight_queen_moves(self, row, col, color):
        """Return valid moves for a queen based on its position and color."""
        # Combination of rook and bishop moves
        return self.highlight_rook_moves(row, col, color) + self.highlight_bishop_moves(row, col, color)

    def highlight_king_moves(self, row, col, color):
        """Return valid moves for a king based on its position and color."""
        valid_moves = []

        # King moves one square in any direction
        for dr, dc in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
            r, c = row + dr, col + dc
            if 0 <= r < 8 and 0 <= c < 8:
                piece = self.get_piece(r, c)
                if piece is None or piece[0] != color:
                    valid_moves.append((r, c))
                    
        # Castling logic
        if not self.kings_moved[color]:
            # Kingside castling
            if not self.rooks_moved[color]['kingside']:
                # Check if path is clear
                if all(self.get_piece(row, c) is None for c in range(col+1, 7)):
                    valid_moves.append((row, col+2))  # Castling move
                    
            # Queenside castling
            if not self.rooks_moved[color]['queenside']:
                # Check if path is clear
                if all(self.get_piece(row, c) is None for c in range(col-1, 0, -1)):
                    valid_moves.append((row, col-2))  # Castling move
                    
        return valid_moves

    def is_valid_move(self, selected_piece, start_pos, end_pos):
        """Check if the selected move is valid for the piece."""
        if selected_piece is None:
            return False

        row, col = start_pos
        valid_moves = self.highlight_moves((row, col))
        return end_pos in valid_moves

    def handle_pawn_promotion(self, row, col):
        """Check if a pawn has reached the opposite end of the board."""
        piece = self.get_piece(row, col)
        if piece and piece[1] == 'P':
            if (piece[0] == 'w' and row == 0) or (piece[0] == 'b' and row == 7):
                return True
        return False

    def promote_pawn(self, row, col, new_piece_type):
        """Promote a pawn to a new piece type."""
        piece = self.get_piece(row, col)
        if piece and piece[1] == 'P':
            color = piece[0]
            self.place_piece(row, col, color + new_piece_type)
            return True
        return False

    def make_ai_move(self):
        """Make a simple AI move for black."""
        possible_moves = []
        
        # Collect all possible moves for black pieces
        for r in range(8):
            for c in range(8):
                piece = self.get_piece(r, c)
                if piece and piece[0] == 'b':
                    valid_moves = self.highlight_moves((r, c))
                    for move in valid_moves:
                        # Prioritize capturing
                        target_piece = self.get_piece(move[0], move[1])
                        score = 0
                        if target_piece:
                            # Higher score for capturing higher value pieces
                            if target_piece[1] == 'P': score = 1
                            elif target_piece[1] == 'N' or target_piece[1] == 'B': score = 3
                            elif target_piece[1] == 'R': score = 5
                            elif target_piece[1] == 'Q': score = 9
                            elif target_piece[1] == 'K': score = 100  # Practically checkmate
                        
                        possible_moves.append((score, (r, c), move))
        
        if possible_moves:
            # Sort by score (highest first)
            possible_moves.sort(reverse=True)
            
            # Pick the highest scoring move
            _, start_pos, end_pos = possible_moves[0]
            piece = self.get_piece(start_pos[0], start_pos[1])
            
            # Make the move
            self.place_piece(end_pos[0], end_pos[1], piece)
            self.place_piece(start_pos[0], start_pos[1], None)
            
            # Check for pawn promotion
            if piece[1] == 'P' and end_pos[0] == 7:
                self.promote_pawn(end_pos[0], end_pos[1], 'Q')  # Always promote to queen
            
            return True
        
        return False


class PawnPromotionDialog(QDialog):
    def __init__(self, color, parent=None):
        super().__init__(parent)
        self.color = color
        self.selected_piece = 'Q'  # Default to Queen
        self.setWindowTitle("Pawn Promotion")
        self.setWindowIcon(QIcon('C:/Users/user/Desktop/iii'))
        layout = QGridLayout()
        
        pieces = ['Q', 'R', 'B', 'N']
        piece_names = ['Queen', 'Rook', 'Bishop', 'Knight']
        
        # Try to find the image path
        base_path = os.path.dirname(os.path.abspath(__file__))
        image_paths = [
            os.path.join(base_path, "images"),  # Try local images directory
            os.path.join(os.path.dirname(base_path), "images"),  # Try parent directory
            "C:/Users/user/Desktop/chess/images/"  # Try hardcoded path
        ]
        
        image_path = None
        for path in image_paths:
            if os.path.exists(path):
                image_path = path
                break
        
        # Add piece buttons
        for i, (piece, name) in enumerate(zip(pieces, piece_names)):
            button = QPushButton(name)
            if image_path:
                piece_code = color + piece
                img_path = os.path.join(image_path, f"{piece_code}.png")
                if os.path.exists(img_path):
                    button.setIcon(QIcon(img_path))
            button.clicked.connect(lambda _, p=piece: self.select_piece(p))
            layout.addWidget(button, 0, i)
        
        self.setLayout(layout)

    def select_piece(self, piece):
        self.selected_piece = piece
        self.accept()


class ChessBoard(QMainWindow):
    def __init__(self, chess_logic):
        super().__init__()
        self.chess_logic = chess_logic
        self.valid_moves = []  # Keep track of valid moves
        self.game_mode = "two_player"  # Default to two player mode
        self.ai_thinking = False
        
        # Set up the main window
        self.setWindowTitle("𝚺 CHESS")
        self.setGeometry(180, 150, 1000, 700)
        self.setWindowIcon(QIcon('C:/Users/user/Desktop/iii'))
        self.setStyleSheet("background-color: ;")
        QIcon,QFont("Arial", 12, QFont.Bold),QMessageBox.about(self,"Welcome to Σ CHESS", "BY ARKA DAS [www.arkadas.godaddysites.com], EMAIL: arkadas6989hc@gmail.com")
        
        # Set up the scene and view
       
        self.screen = mb.showinfo("Welcome to Σ CHESS", "BY ARKA DAS [www.arkadas.godaddysites.com], EMAIL: arkadas6989hc@gmail.com")
        
        
    # Central widget and layout
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.captured_frame = QFrame()
        self.captured_frame.setObjectName("capturedFrame")
        cap_layout = QHBoxLayout(self.captured_frame)
        self.white_caps = QLabel()
        self.white_caps.setObjectName("capturedLabel")
        self.black_caps = QLabel()
        self.black_caps.setObjectName("capturedLabel")
        cap_layout.addWidget(self.white_caps)
        cap_layout.addWidget(self.black_caps)
        self.layout.addWidget(self.captured_frame)

        # Game status display
        self.status_label = QLabel("White's turn")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFont(QFont("Cinzel", 15, QFont.Bold))
        self.layout.addWidget(self.status_label)

        # ---- Button Layout ----
        self.button_layout = QHBoxLayout( )  # Horizontal layout for buttons

        # Board style buttons
        self.standard_button = QPushButton("Standard", self)
        self.styled_button1 = QPushButton("Vintage", self)
        self.styled_button2 = QPushButton("Dark", self)
        self.alternative_button = QPushButton("High Contrast", self)

        self.button_layout.addWidget(self.standard_button)
        self.button_layout.addWidget(self.styled_button1)
        self.button_layout.addWidget(self.styled_button2)
        self.button_layout.addWidget(self.alternative_button)

        self.layout.addLayout(self.button_layout)
        
        # Game mode selection
        self.mode_layout = QHBoxLayout()
        self.two_player_button = QPushButton("Two Player", self)
        self.ai_button = QPushButton("vs AI", self)
        self.two_player_button.setStyleSheet("background-color: lightblue;")
        
        self.mode_layout.addWidget(self.two_player_button)
        self.mode_layout.addWidget(self.ai_button)
        self.layout.addLayout(self.mode_layout)

        # New game and quit buttons
        self.control_layout = QHBoxLayout()
        self.new_game_button = QPushButton("New Game", self)
        self.quit_button = QPushButton("Quit", self)
        
        self.control_layout.addWidget(self.new_game_button)
        self.control_layout.addWidget(self.quit_button)
        self.layout.addLayout(self.control_layout)

        # Scene and View
        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene, self)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setRenderHint(QPainter.SmoothPixmapTransform)
        self.layout.addWidget(self.view)
       
        # Board dimensions
        
        self.square_size = 69
        self.board_width = 8
        self.board_height = 8

        # Set up the chess piece images
        self.setup_piece_images()

        # Initial board setup
        self.create_standard_chessboard()
        self.place_pieces()

        # Button connections
        self.standard_button.clicked.connect(self.create_standard_chessboard)
        self.styled_button1.clicked.connect(self.create_styled_chessboard1)
        self.styled_button2.clicked.connect(self.create_styled_chessboard2)
        self.alternative_button.clicked.connect(self.create_alternative_chessboard)
        self.new_game_button.clicked.connect(self.reset_game)
        self.quit_button.clicked.connect(self.close)
        self.two_player_button.clicked.connect(lambda: self.set_game_mode("two_player"))
        self.ai_button.clicked.connect(lambda: self.set_game_mode("vs_ai"))

        # Mouse interaction
        self.selected_piece = None
        self.selected_pos = None
        self.view.mousePressEvent = self.handle_square_click
        
        # AI timer
        self.ai_timer = QTimer(self)
        self.ai_timer.timeout.connect(self.make_ai_move)

    def setup_piece_images(self):
        """Set up the chess piece images."""
        # Default image path
        default_path = "C:/Users/user/Desktop/chess/images/"
        
        # Check if images directory exists in the executable directory
        base_dir = os.path.dirname(os.path.abspath(__file__))
        local_images_dir = os.path.join(base_dir, "images")
        
        # If local images directory exists, use it
        if os.path.exists(local_images_dir):
            images_path = local_images_dir
        # Otherwise try a relative path
        elif os.path.exists(os.path.join(os.path.dirname(base_dir), "images")):
            images_path = os.path.join(os.path.dirname(base_dir), "images")
        # Fall back to default path
        else:
            images_path = default_path
        
        self.piece_images = {
            'wK': os.path.join(images_path, 'wK.png'),
            'wQ': os.path.join(images_path, 'wQ.png'),
            'wR': os.path.join(images_path, 'wR.png'),
            'wB': os.path.join(images_path, 'wB.png'),
            'wN': os.path.join(images_path, 'wN.png'),
            'wP': os.path.join(images_path, 'wP.png'),
            'bK': os.path.join(images_path, 'bK.png'),
            'bQ': os.path.join(images_path, 'bQ.png'),
            'bR': os.path.join(images_path, 'bR.png'),
            'bP': os.path.join(images_path, 'bP.png'),
            'bN': os.path.join(images_path, 'bN.png'),
            'bB': os.path.join(images_path, 'bB.png')
        }

    def set_game_mode(self, mode):
        """Set the game mode."""
        self.game_mode = mode
        if mode == "two_player":
            self.two_player_button.setStyleSheet("background-color: lightblue;")
            self.ai_button.setStyleSheet("")
            self.status_label.setText("Two Player Mode - White's turn")
        else:
            self.two_player_button.setStyleSheet("background-color:lightgreen ;")
            self.ai_button.setStyleSheet("background-color: lightyellow;")
            self.status_label.setText("Playing against AI - White's turn")
        
     
        # Reset game when changing mode
        self.reset_game()

    def reset_game(self):
        """Reset the game to initial state."""
        self.chess_logic = ChessLogic()
        self.selected_pos = None
        self.valid_moves = []
        self.create_standard_chessboard()
        self.place_pieces()
        
        if self.game_mode == "two_player":
            self.status_label.setText("Two Player Mode - White's turn")
        else:
            self.status_label.setText("Playing against AI - White's turn")

    def create_standard_chessboard(self):
        self.scene.clear()
        self.create_chessboard()
        self.place_pieces()

    def create_styled_chessboard1(self):
        self.scene.clear()
        self.create_custom_chessboard(255, 223, 186, 111, 85, 59)
        self.place_pieces()

    def create_styled_chessboard2(self):
        self.scene.clear()
        self.create_custom_chessboard(150, 150, 150, 50, 50, 50)
        self.place_pieces()

    def create_alternative_chessboard(self):
        self.scene.clear()
        self.create_custom_chessboard(220, 220, 220, 40, 40, 40)
        self.place_pieces()

    def create_custom_chessboard(self, light_r, light_g, light_b, dark_r, dark_g, dark_b):
        """Create a chessboard with custom colors."""
        for row in range(self.board_height):
            for col in range(self.board_width):
                x = col * self.square_size
                y = row * self.square_size
                square_color = QColor(light_r, light_g, light_b) if (row + col) % 2 == 0 else QColor(dark_r, dark_g, dark_b)
                rect = QGraphicsRectItem(QRectF(x, y, self.square_size, self.square_size))
                rect.setBrush(square_color)
                self.scene.addItem(rect)

    def create_chessboard(self):
        """Create the standard chessboard with white and gray squares."""
        for row in range(self.board_height):
            for col in range(self.board_width):
                x = col * self.square_size
                y = row * self.square_size
                square_color = QColor(255, 255, 255) if (row + col) % 2 == 0 else QColor(169, 169, 169)
                rect = QGraphicsRectItem(QRectF(x, y, self.square_size, self.square_size))
                rect.setBrush(square_color)
                self.scene.addItem(rect)

    def place_pieces(self):
        """Place the chess pieces on the board according to the current game state."""
        for row in range(self.board_height):
            for col in range(self.board_width):
                piece = self.chess_logic.get_piece(row, col)
                if piece:
                    try:
                        piece_image = QPixmap(self.piece_images[piece])
                        # Scale the image to fit the square
                        piece_image = piece_image.scaled(
                            int(self.square_size * 0.9), 
                            int(self.square_size * 0.9),
                            Qt.KeepAspectRatio, 
                            Qt.SmoothTransformation
                        )
                        piece_item = QGraphicsPixmapItem(piece_image)
                        # Center the image in the square
                        offset_x = col * self.square_size + (self.square_size - piece_image.width()) / 2
                        offset_y = row * self.square_size + (self.square_size - piece_image.height()) / 2
                        piece_item.setOffset(offset_x, offset_y)
                        self.scene.addItem(piece_item)
                    except Exception as e:
                        print(f"Error loading piece image for {piece}: {e}")
    
    def draw_move_highlight(self, valid_moves):
        """Draw green dots to highlight valid move squares."""
        for (r, c) in valid_moves:
            x = c * self.square_size
            y = r * self.square_size
            ellipse = QGraphicsEllipseItem(QRectF(x + self.square_size/3, y + self.square_size/3, self.square_size/3, self.square_size/3))
            ellipse.setBrush(QColor(0, 200, 0, 200))  # Green dot with transparency
            self.scene.addItem(ellipse)

    def handle_square_click(self, event):
        """Handle mouse clicks on the chessboard."""
        if self.chess_logic.game_over or self.ai_thinking:
            return
            
        mouse_pos = event.pos()
        scene_pos = self.view.mapToScene(mouse_pos)
        row = int(scene_pos.y() // self.square_size)
        col = int(scene_pos.x() // self.square_size)

        # Check if the row and col are within the valid range
        if 0 <= row < self.board_height and 0 <= col < self.board_width:
            if self.selected_pos is None:
                selected_piece = self.chess_logic.get_piece(row, col)
                if selected_piece and selected_piece[0] == self.chess_logic.current_turn:
                    self.selected_pos = (row, col)
                    
                    # Refresh the board to remove previous highlights
                    self.refresh_board()  
                    
                    # Get valid moves and draw highlights
                    self.valid_moves = self.chess_logic.highlight_moves((row, col))
                    self.draw_move_highlight(self.valid_moves)

            else:
                start_pos = self.selected_pos
                end_pos = (row, col)
                selected_piece = self.chess_logic.get_piece(start_pos[0], start_pos[1])

                if end_pos in self.valid_moves:
                    # Handle the actual move
                    self.make_move(start_pos, end_pos)
                    
                    # If playing against AI, trigger AI move after player
                    if self.game_mode == "vs_ai" and self.chess_logic.current_turn == 'b' and not self.chess_logic.game_over:
                        self.ai_thinking = True
                        self.status_label.setText("AI is thinking...")
                        self.ai_timer.start(469)  # Give a small delay to simulate thinking
                else:
                    # If clicking on own piece, select that piece instead
                    clicked_piece = self.chess_logic.get_piece(row, col)
                    if clicked_piece and clicked_piece[0] == self.chess_logic.current_turn:
                        self.selected_pos = (row, col)
                        
                        # Refresh the board to remove previous highlights
                        self.refresh_board()
                        
                        # Get valid moves and draw highlights
                        self.valid_moves = self.chess_logic.highlight_moves((row, col))
                        self.draw_move_highlight(self.valid_moves)
                    else:
                        # Deselect if clicking elsewhere
                        self.selected_pos = None
                        self.valid_moves = []
                        self.refresh_board()
                        
        else:
            print("Clicked outside the board")

    def make_move(self, start_pos, end_pos):
        """Make a move on the board."""
        start_row, start_col = start_pos
        end_row, end_col = end_pos
        selected_piece = self.chess_logic.get_piece(start_row, start_col)
        
        # Capture opponent's piece if present
        target_piece = self.chess_logic.get_piece(end_row, end_col)
        if target_piece:
            opponent_color = 'b' if selected_piece[0] == 'w' else 'w'
            self.chess_logic.captured_pieces[selected_piece[0]].append(target_piece)

        # Handle king and rook movement for castling
        if selected_piece[1] == 'K':
            self.chess_logic.kings_moved[selected_piece[0]] = True
            
            # Detect castling
            if abs(start_col - end_col) == 2:
                # Kingside castling
                if end_col > start_col:
                    rook_start_col = 7
                    rook_end_col = end_col - 1
                # Queenside castling
                else:
                    rook_start_col = 0
                    rook_end_col = end_col + 1
                    
                rook = self.chess_logic.get_piece(start_row, rook_start_col)
                self.chess_logic.place_piece(start_row, rook_end_col, rook)
                self.chess_logic.place_piece(start_row, rook_start_col, None)
        
        # Track rook movement for castling
        if selected_piece[1] == 'R':
            color = selected_piece[0]
            if start_row == (7 if color == 'w' else 0):
                if start_col == 0:  # Queenside rook
                    self.chess_logic.rooks_moved[color]['queenside'] = True
                elif start_col == 7:  # Kingside rook
                    self.chess_logic.rooks_moved[color]['kingside'] = True

        # Move the piece
        self.chess_logic.place_piece(end_row, end_col, selected_piece)
        self.chess_logic.place_piece(start_row, start_col, None)
        
        # Check for pawn promotion
        if self.chess_logic.handle_pawn_promotion(end_row, end_col):
            self.handle_promotion_dialog(end_row, end_col, selected_piece[0])
        
        # Change turn
        self.chess_logic.current_turn = 'b' if self.chess_logic.current_turn == 'w' else 'w'
        
        # Refresh board and reset selection
        self.selected_pos = None
        self.valid_moves = []
        self.refresh_board()
        
        # Check for check, checkmate or stalemate
        self.check_game_status()

    def make_ai_move(self):
        """Make an AI move."""
        self.ai_timer.stop()
        
        if self.chess_logic.make_ai_move():
            # Change turn back to player
            self.chess_logic.current_turn = 'w'
            self.refresh_board()
            
            # Check for check, checkmate or stalemate
            self.check_game_status()
        
        self.ai_thinking = False

    def handle_promotion_dialog(self, row, col, color):
        """Show dialog for pawn promotion."""
        dialog = PawnPromotionDialog(color, self)
        if dialog.exec_():
            promoted_piece = dialog.selected_piece
            self.chess_logic.promote_pawn(row, col, promoted_piece)

    def check_game_status(self):
        """Check for check, checkmate, or stalemate."""
        current_color = self.chess_logic.current_turn
        opponent_color = 'w' if current_color == 'b' else 'b'
        
        # Check if current player is in check
        in_check = self.chess_logic.is_opponent_in_check(opponent_color)
        
        # Check if current player is in checkmate
        if in_check and self.chess_logic.is_checkmate(current_color):
            self.chess_logic.game_over = True
            self.chess_logic.winner = opponent_color
            winner = "White" if opponent_color == 'w' else "Black"
            self.status_label.setText(f"Checkmate! {winner} wins!")
            QMessageBox.information(self, "Game Over", f"Checkmate! {winner} wins!,👑 Congratulations! {winner} ")
            self.setWindowIcon(QIcon('C:/Users/user/Desktop/iii'))
            return
            
        # Check for stalemate
        if self.chess_logic.is_stalemate(current_color):
            self.chess_logic.game_over = True
            self.status_label.setText("Stalemate! The game is a draw.")
            QMessageBox.information(self, "Game Over", "Stalemate! 🤝 The game is a draw.")
            self.setWindowIcon(QIcon('C:/Users/user/Desktop/iii')) 
            return
            
        # Update status for check
        if in_check:
            turn = "White's" if current_color == 'w' else "Black's"
            self.status_label.setText(f"{turn} turn - Check!")
        else:
            turn = "White's" if current_color == 'w' else "Black's"
            self.status_label.setText(f"{turn} turn")

    def refresh_board(self):
        """Refresh the board display."""
        # Redraw the board
        if self.scene.items():
            # Get the first item to determine board style
            first_item = self.scene.items()[-1]  # Last added item is the first square
            if isinstance(first_item, QGraphicsRectItem):
                color = first_item.brush().color()
                
                # Recreate the board with the same style
                if color == QColor(255, 255, 255) or color == QColor(169, 169, 169):
                    self.create_standard_chessboard()
                elif color == QColor(255, 223, 186) or color == QColor(111, 85, 59):
                    self.create_styled_chessboard1()
                elif color == QColor(150, 150, 150) or color == QColor(50, 50, 50):
                    self.create_styled_chessboard2()
                elif color == QColor(220, 220, 220) or color == QColor(40, 40, 40):
                    self.create_alternative_chessboard()
                else:
                    self.create_standard_chessboard()
            else:
                self.create_standard_chessboard()
        else:
            self.create_standard_chessboard()


def create_images_dir_if_needed():
    """Create the images directory if it doesn't exist and copy sample images."""
    # Get the directory where the script/executable is located
    base_dir = os.path.dirname(os.path.abspath(__file__))
    images_dir = os.path.join(base_dir, "images")
    
    # Create the images directory if it doesn't exist
    if not os.path.exists(images_dir):
        os.makedirs(images_dir)
        print(f"Created images directory at {images_dir}")
        
        # Create simple placeholder images for pieces if needed
        piece_colors = ['w', 'b']  # white, black
        piece_types = ['K', 'Q', 'R', 'B', 'N', 'P']  # king, queen, rook, bishop, knight, pawn
        
        # Check if any source images exist that we can copy
        source_dirs = [
            "C:/Users/user/Desktop/chess/images/",
            os.path.join(os.path.dirname(base_dir), "images")
        ]
        
        source_dir = None
        for dir_path in source_dirs:
            if os.path.exists(dir_path):
                source_dir = dir_path
                break
                
        if source_dir:
            # Copy existing images
            print(f"Copying chess piece images from {source_dir}")
            for color in piece_colors:
                for piece_type in piece_types:
                    piece_code = color + piece_type
                    source_path = os.path.join(source_dir, f"{piece_code}.png")
                    if os.path.exists(source_path):
                        import shutil
                        dest_path = os.path.join(images_dir, f"{piece_code}.png")
                        shutil.copy2(source_path, dest_path)
                        print(f"Copied {piece_code}.png")
                    else:
                        print(f"Warning: Could not find source image for {piece_code}")
        else:
            print("No source images found. Please add chess piece images to the 'images' directory.")


if __name__ == "__main__":
    # Create images directory if needed
    create_images_dir_if_needed()
    
    app = QApplication(sys.argv)
    chess_logic = ChessLogic()
    window = ChessBoard(chess_logic)
    window.show()
    sys.exit(app.exec_())





    
    #def make_ai_move(self):
    #self.ai_timer.stop()
    #difficulty = self.difficulty_selector.currentText().lower()
    #if self.chess_logic.make_ai_move(difficulty=difficulty):
        #self.chess_logic.current_turn = 'w'
        #self.refresh_board()
        #self.check_game_status()
    #self.ai_thinking = False
