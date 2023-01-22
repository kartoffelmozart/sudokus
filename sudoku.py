from configuration import _9x9_configuration
import numpy as np


class Sudoku:
    def __init__(self,config):
        # An instance of the Configuration class
        self.config = config

        # The number of numbers so far placed on the soduko board
        self.placed_numbers = 0

        # In this matrix "availability_board", each cell holds a bitmap. If a bit is flipped, 
        # it indicates that the corresponding number can be placed here. 
        # 1111111111  <- bitmap
        # 987654321X <- corresponding numbers
        # If a cell in board has the bitmap
        # 1000000101
        # this indicates that the number 2 and the number 9 can be placed here.
        # The rightmost bit indicates if this cell is free or not. 
        self.placability_board = self.config.empty_matrix.copy()
        # To check if a number can be placed on the coordinates (x,y) board, do the following check:
        # self.availability_board[y,x] & self.config.number_to_bitmask[number] and self.availability_board[y,x] & self.cell_free_bit
        # This checks if the bit corresponding to the given number is flipped, and checks if the bit that indicates that the
        # cell is free is flipped.
        # The ´´number_to_bitmask´´ field in Configuration holds the bitmask corresponding to a given number, accessed like so
        # config.number_to_bitmask[number]

        # Fill the bitmap-board up, indicating that any number can be placed anywhere - the board is empty.
        for n in self.config.number_to_bitmask:
            self.placability_board |= n
        
        # The displayable field with hold the human-readable sudoku, with 0 representing an empty cell.
        self.displayable = np.array([[0 for _ in range(self.config.size)] for _ in range(self.config.size)])

        
    def canPlace(self,y,x,number):
        # Return True if a given number can be placed on a given coordinate, else False
        return self.placability_board[y,x] & self.config.number_to_bitmask[number] and \
            self.placability_board[y,x] & self.config.number_to_bitmask[0]

    
    def place(self,y,x,number):
        # Place a number on the coordinates (x,y).
        # This will result in an invalid solution if called when canPlace(y,x,number) returns False. 
        # self.place will is not responsible for not commiting an illegal move.

        # Unset the bits in placability_board, so that canPlace will return False if asked if number can be placed
        # in this partition, row or column.
        self.placability_board = self.placability_board & ~ self.config.availability_masks[y][x][number]

        # Unset the cell_free_bit in this cell, so that canPlace will return False if asked if any number can be
        # placed here.
        self.placability_board[y,x] = self.placability_board[y,x] & ~ self.config.cell_free_bit

        # Place the number in the human-readable sudoku
        self.displayable[y][x] = number

        # Increment the number of placed numbers. A number was placed!
        self.placed_numbers += 1

    
    def unplace(self,y,x,number):
        # Unplace a given number on (x,y)

        # Check if there is anything placed here. If not, just return.
        if not self.placability_board[y,x] & self.config.cell_free_bit:
            return 

        # Set the bits in placability_board so that canPlace(y,x,number) will once again return True
        # when asked if this number can be placed in the partition, row or column that (x,y) belongs to.
        self.placability_board |= self.config.availability_matrices[y][x][number]
        # NOTE: THE ABOVE NOTATION IS SPECIFIC TO THE NUMPY LIBRARY IN PYTHON. 
        # In a different language, you should attempt the same approach, but the code will look much 
        # different. Iter through each cell on the placability_board and do the operation for each cell.

        # Set the bit denoting that this cell is empty.
        self.placability_board[y,x] |= self.config.cell_free_bit

        # Remove the number from the human-readable board
        self.displayable[y][x] = 0

        # Take one away from the number of placed numbers on the board. A number was removed.
        self.placed_numbers -= 1


    def copy(self):
        # Make and return a copy of this sudoku. If the copy is altered, this version will not be altered.
        new = Sudoku(self.config)
        new.placability_board = self.placability_board.copy()
        new.displayable = self.displayable.copy()
        new.placed_numbers = self.placed_numbers
        return new


    def isSolved(self):
        # Check if the sudoku is solved by checking if self.config.size**2 (81 in the case of a 9x9 sudoku)
        # numbers has been placed
        return self.placed_numbers == self.config.size**2
    
    
    def display(self,mode=1):
        # mode 1: display only the human readable board
        # mode 2: display only the placability_board
        # mode 3: display both boards
        if mode & 1: 
            for y in range(self.config.size):
                for x in range(self.config.size):
                    print(self.displayable[y,x],end=' ')
                    if x % self.config.partition_size == self.config.partition_size - 1:
                        print(end=' ')
                if y % self.config.partition_size == self.config.partition_size - 1:
                    print()
                print()
        if mode & 2:
            for y in range(self.config.size):
                for x in range(self.config.size):
                    print(f'{self.placability_board[y,x]:^3}',end=' ')
                    if x % self.config.partition_size == self.config.partition_size - 1:
                        print(end=' ')
                if y % self.config.partition_size == self.config.partition_size - 1:
                    print()
                print()
