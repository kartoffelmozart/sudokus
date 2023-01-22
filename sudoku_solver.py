from sudoku import Sudoku
from configuration import _9x9_configuration
import numpy as np


class SudokuSolver:
    config = _9x9_configuration
    def __init__(self,input_material):
        # The input_material must be a 2d array representing the sudoku OR a Sudoku object

        if isinstance(input_material , Sudoku):
            # If the input material is a sudoku, then nothing more is required.
            self.sudoku = input_material
            return

        # If not, it must be transformed into a sudoku.
        # Verify that the input material is valid
        input_material = self.verifyInput(input_material)

        # The object modelling the sudoku to solve
        self.sudoku = Sudoku(self.config)

        # Use the input material to fill out the initial sudoku
        for y,row in enumerate(input_material):
            for x,number in enumerate(row):
                if number not in (1,2,3,4,5,6,7,8,9): 
                    continue
                elif self.sudoku.canPlace(y,x,number):
                    self.sudoku.place(y,x,number)
                else:
                    raise AttributeError('the laws of sudokus does not recognize this input material as valid!',input_material)
                

    def verifyInput(self,input_material):
        # The shape of the input material. Should be (self.config.size , self.config.size),
        # implying that it's a quadratic 2d array with side length of self.config.size.
        # For a 9x9 sudoku, the shape should be (9,9).

        shape = np.shape(input_material)

        # Check if the shape is correct
        if shape != (self.config.size , self.config.size):
            raise ValueError(f'the shape of the input material to a {self.config.size}x{self.config.size} sudoku should be {(self.config.size,self.config.size)}, not {shape}')

        # If the input material is not ints (could be strings or floats), convert them to ints
        for y in range(shape[0]):
            for x in range(shape[1]):
                input_material[y][x] = int(input_material[y][x])

        return input_material


    def solve(self):

        # A method that solves a sudoku recursively. It places all ´´trivial´´ numbers in a given sudoku, 
        # and then makes a guess on where a number could be placed and place it in a new copy of the 
        # sudoku. Then it makes a new SudokuSolver object that attempts to solve the new copy. 
        # If this fails (because the guess was incorrect), make a new guess on the original sudoku in 
        # a new copy and try again. 
        # The method returns (True, <solved sudoku>) if it managed to solve the sudoku, and 
        # (False , "the sudoku could not be solved") if it fails.

        # Place trivial numbers. placeTrivials can some times detect an invalid sudoku, and will return
        # a Boolean that denotes if there is still hope that this guess is valid.


        solution_valid = self.placeTrivials()
        if not solution_valid: 
            return False , 'the sudoku could not be solved'
        
        # If the sudoku is now solved, return
        if self.sudoku.isSolved(): return True , self.sudoku

        # By now, the solver has assembled a range of guesses. The best guesses are chosen
        # and each guess is tried. 
        for guess in self.best_guesses:
            # make a new soduko for each guess
            new_sudoku = self.makeGuess(guess)
            # and attempt to solve it
            solved , result = SudokuSolver(new_sudoku).solve()
            # If a completed, validly solved sudoku is found, return it
            if solved: 
                return True , result
            # else, start over for the next guess

        # if all guesses have been tried and no solution is found, the sudoku can not be solved
        # (or there is flaw in the solving method/bug in the program)
        return False , 'the sudoku can not be solved'

    
    def placeTrivials(self):
        # This method attempts to place the numbers that are ´´safe´´ to place in the sudoku.
        # There are many approaches of doing this. This solver only uses one, as it's pleanty
        # fast. 
        # Check each cell for each number. If a cell can only hold one number, it's safe to place.
 
        # Boolean to keep track of whether or not a number was placed.
        self.trivial_found = True

        # After placing a number, more numbers might now be safe to place. Repeat the loop until
        # no more safe placements can be found.
        while self.trivial_found:
            self.trivial_found = False

            self.best_guesses = [None] * self.config.size
            # best_guesses will hold the shortest group of guesses we can find, out of which
            # we know at least one must be a correct guess. That way we keep the tree of recursive
            # guessing as small as possible
            # best_guesses is initialised as a list of the longest length such a group could have.
            # That way we are sure that the first group we find will be shorter than it, and replace it.
            # A guess has the form (y,x,number), denoting the placing of a number on the sudoku.

            # considerEachCell can sometimes preemptively see if a solution is invalid. If it detects that the 
            solution_valid = self.considerEachCell()
            if not solution_valid: return False
            
            # If you implement more approaches of placing trivial numbers, put the methods for it here.

        return True

    
    def considerEachCell(self):
        # Go through each cell, check how many different numbers can be placed here.
        # If the range of different numbers that can be placed is 1, that means this number is 
        # safe to place. If the range of different numbers is greater than 1 but shorter than
        # best guesses, this range of numbers is our new best guesses.

        # Iter though each free cell. I do this using the Python specific numpy library. It can
        # find all the free cells using just one line. In a different language, you would
        # probably have to iter through all cells and check each one if it's free.
        for y,x in zip(*np.where((self.sudoku.placability_board & self.config.cell_free_bit))):
            # (x,y) is a free cell.

            numbers_this_cell_can_hold = []

            # Go through each number that is used in this sudoku. The numbers (1,2,3,4,5,6,7,8,9) for
            # a 9x9 sudoku.
            for number in range(1,self.config.size + 1):

                # Check if number can be placed here. 
                if self.sudoku.canPlace(y,x,number):
                    numbers_this_cell_can_hold.append((y,x,number))

            # numbers_this_cell_can_hold now holds all numbers placable on (x,y)  
            
            # If the length of numbers_this_cell_can_hold is 0, no number could be placed. Thee solution is invalid!
            if len(numbers_this_cell_can_hold) == 0:
                return False

            # If only one number could be placed, numbers_this_cell_can_hold now looks like this: [(y,x,number)]. Place it.
            elif len(numbers_this_cell_can_hold) == 1:
                self.sudoku.place(*numbers_this_cell_can_hold[0])
                self.trivial_found = True

            # We know that each out of the entries in numbers_this_cell_can_hold, one of them must
            # be correct (if the sudoku can be solved at all).
            # If the length is shorter than the current best_guesses, it's a better contender for guesses.
            elif len(numbers_this_cell_can_hold) > 1 and len(numbers_this_cell_can_hold) < len(self.best_guesses):
                self.best_guesses = numbers_this_cell_can_hold
            
        # After placing the trivial numbers might have been revealed after placing these trivials.
        # If so, the self.trivial_found field will be True, and this method will be called again to
        # pick up on the new trivials before guesses are made.

        # Returning True, since this method failed to reveal that this solution is invalid.
        return True


    def makeGuess(self,guess):
        # Make a new (possibly invalid) sudoku that assumes this guess to be true.
        new_sudoku = self.sudoku.copy()
        new_sudoku.place(*guess)
        return new_sudoku

if __name__ == '__main__':
    # Entry point
    input_material = [
        [0,0,0,0,4,3,0,0,2],
        [0,5,0,0,0,0,0,0,0],
        [7,0,4,6,0,0,1,0,0],
        [0,8,0,9,0,0,0,0,0],
        [0,6,0,0,0,0,5,0,0],
        [9,0,5,0,2,0,0,0,1],
        [8,0,0,0,0,0,0,0,0],
        [0,0,0,0,6,0,0,7,0],
        [1,0,9,7,0,0,4,0,0]
    ]
    solver = SudokuSolver(input_material)
    solved,result = solver.solve()
    if solved: result.display()
    else: print(result)
