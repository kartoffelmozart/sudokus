import numpy as np

# The sudokus will be solved recursively. For each recursion, a new Sudoku instance will be created.
# The Configuration class contains the information about a sudoku that is common for all the Sudoku
# instances, and does not need to be copied for every instance of Sudoku.
# It is collected in a seperate class, so that several different families of sudokus, using different
# configurations, simultaneously. This could arguably have been done a lot smarter with inheritance.

class Configuration:
    def __init__(self,size=9,partition_size=None):
        # size is the side length of a given sudoku. Usually 9.
        # partition_size is the side length of the (usually 9) subgroups in a sudoku.
        self.setParameters(size,partition_size)
    
    def setParameters(self,size,partition_size):

        # Make sure that size and partition_size are alright to go forwards
        self.size , self.partition_size = self.validateParameters(size,partition_size)

        # numbers is a list of bitmaps that correspond to a given number. 
        # The bitmaps corresponds to numbers like so:
        # 1: 0000000010
        # 2: 0000000100
        # 3: 0000001000
        # 4: 0000010000
        # 5: 0000100000
        # 6: 0001000000
        # 7: 0010000000
        # 8: 0100000000
        # 9: 1000000000
        # (for a 9x9 sudoku)
        self.number_to_bitmask = [1 << i for i in range(self.size + 1)]

        # To see if a given number n can be placed in a given cell (x,y), use Sudoku.placability_board
        # as so:
        # sudoku.placability_board[y,x] & numbers[n]
        # This returns 0 if n can not be placed here, because n is already in this row/column/partition,
        # and returns some non-zero number if the n can be placed here.

        # cell_free_bit reveals if this cell is free at all, like so:
        # solution[y,x] & cell_free_bit (this returns a number if the cell is free)
        self.cell_free_bit = 1

        # An empty sudoku matrix for copying
        # (bc it's faster than making it on scratch on the fly)
        self.empty_matrix = np.zeros((self.size,self.size),np.uint16)

        # The availability_masks field holds self.size matrices for each cell in a soduko. 
        # Each mask corresponds to this cell and one of the self.size numbers. 
        # The mask is a 2d bitmap over which spaces in the sudoku would be blocked from placing this number
        # in the future, if it were placed in this cell. 
        # When a number is placed, the solution will use this field to note down where this number can no longer
        # be placed according to the laws of sudokuing.
        # Defining the field:
        self.availability_masks = \
            [
                [
                    [                        
                        None for _ in range(self.size+1)
                    ] for _ in range(self.size+1)
                ] for _ in range(self.size+1)
            ]
        # Filling the field with matrices
        for y in range(self.size):
            for x in range(self.size):
                for number in range(1,self.size+1):
                    matrix = self.empty_matrix.copy()
                    partition_y = (y // self.partition_size) * self.partition_size
                    partition_x = (x // self.partition_size) * self.partition_size
                    matrix[y,:] = self.number_to_bitmask[number]
                    matrix[:,x] = self.number_to_bitmask[number]
                    matrix[partition_y:partition_y + self.partition_size , 
                        partition_x:partition_x + self.partition_size] = self.number_to_bitmask[number]
                    self.availability_masks[y][x][number] = matrix

        # This is an attempt at visualising what availability_masks[1][2][6] looks like:

        #   a a a    0 0 0    0 0 0 
        #   a a a    0 0 0    0 0 0 
        #   a a a    a a a    a a a
        #
        #   0 a 0    0 0 0    0 0 0
        #   0 a 0    0 0 0    0 0 0
        #   0 a 0    0 0 0    0 0 0
        #
        #   0 a 0    0 0 0    0 0 0
        #   0 a 0    0 0 0    0 0 0
        #   0 a 0    0 0 0    0 0 0
        
        # Where ´´a´´ is the bitmask found in numbers[6]

        # This, together with self.number_to_bitmask and Sudoku.placability_matrix is
        # supposed to provide tools for quickly checking if a given number can be placed
        # in a given cell, and quickly updating the Sudoku.placability_matrix to match 
        # the current state of the sudoku.



    def validateParameters(self,size,partition_size):

        # ensure that the parameters have the right types
        if (type(size) , type(partition_size)) not in ((int,int) , (int,type(None))):
            raise TypeError(f'the types of size and partition_size must be int and int, not {type(size)} and {type(partition_size)}')

        # ensure that size is not too large
        if size > 10**2: 
            raise ValueError(f'size can not be greater than 100, not {size}')

        # ensure that size is a square
        elif not (size**.5).is_integer(): 
            raise ValueError(f'size must be a square, not {size}')

        # set partition_size if None
        if partition_size is None:
            partition_size = int(size**.5)
        
        # ensure that partition_size is the square root of size
        if partition_size != size**.5:
            raise ValueError(f'partition_size must he the square root of size (which is {int(size**.5)}), not {partition_size}')
        
        return size , partition_size
        
# The configuration of a 9x9 sudoku with 3x3 partitions
_9x9_configuration = Configuration(9)

# The configuration of a 4x4 with 2x2 partitions
_4x4_configuration = Configuration(4)