import sys
import copy
import gc

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())


    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """

        tmp_domain = copy.deepcopy(self.domains)
        for crossword_variable in self.crossword.variables:
            crossword_variable_str = str(crossword_variable)
            number_of_letters = int(crossword_variable_str.split(" : ")[1])            
            for domain_word in self.domains[crossword_variable]:
                if len(domain_word) != number_of_letters:
                    tmp_domain[crossword_variable].remove(domain_word)

        self.domains = tmp_domain

        del tmp_domain # Trow away the temp variable
        gc.collect() # garbage collection   
        return None


    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        tmp_domains = copy.deepcopy(self.domains)  

        #find position where each word intersect the other
        overlaps_for_variable_x_and_variable_y=self.crossword.overlaps[x, y]
        somthing_has_been_revised = False
        if(overlaps_for_variable_x_and_variable_y != None):
            #delete any word in the domain for x that does not have an intersection with domain y in the correct location
            for a_word_in_x_domain in self.domains[x]:
                delete_this = True
                for a_word_in_y_domain in self.domains[y]:
                    # check if the two words intersect in the correct locations
                    if  a_word_in_x_domain[overlaps_for_variable_x_and_variable_y[0]] == a_word_in_y_domain[overlaps_for_variable_x_and_variable_y[1]]:
                        delete_this = False  
                
                # if the current word does not have the correct letter for the intersection then delete it 
                if delete_this:
                    tmp_domains[x].remove(a_word_in_x_domain)
                    somthing_has_been_revised = True 
                                            
            # if some words were deleted from the domain x then copy th temporary domain to the global domain
            if somthing_has_been_revised == True:
                self.domains =  tmp_domains

        del tmp_domains # Trow away the temp variable
        gc.collect() # garbage collection
        return somthing_has_been_revised 


    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        
        list_of_arcs_tuples = []
        x = None
        y = None
        
        if arcs == None:
            #find  all the Arcs
            keys_to_all_variable_overlaps = self.crossword.overlaps.keys()
        

            
        for possible_overlap_key in keys_to_all_variable_overlaps:
            if self.crossword.overlaps[possible_overlap_key] != None:
                tmp_list = list(possible_overlap_key)
                tmp_tuple = (tmp_list[0],tmp_list[1])
                list_of_arcs_tuples.append(tmp_tuple)
        
        while len(list_of_arcs_tuples) > 0:
            arc_tuple = list_of_arcs_tuples.pop(0)
            x = arc_tuple[0]
            y = arc_tuple[1]
           
            if(x != y):
                if self.revise(x, y):
                    if len(self.domains[x]) == 0:
                        print("DOMAIN IS FALSE DOMAIN IS FALSE DOMAIN IS FALSE DOMAIN IS FALSE DOMAIN IS FALSE DOMAIN IS FALSE ")
                        return False
                    for z in self.crossword.neighbors(x):
                        if z != y:
                            tmp_tuple = (z,x)
                            list_of_arcs_tuples.append(tmp_tuple)
        return True


        

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """

        for variable in self.crossword.variables:
            if variable not in assignment.keys():
                return False

        return True


    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        across_variable_set = []
        down_variable_set = []
        

        # determine if all words are unique (#check for duplicate words)
        all_words = set()
        
        for one_assignment_key, one_assignment_value in assignment.items():
            all_words.add(one_assignment_value)
        
        # all wards are not unique return False
        if len(all_words) != len(assignment):
            return False 

        
        
        #check for length consistency
        for one_assignment_key, one_assignment_value in assignment.items():
            tmp_value = str(one_assignment_key).split(":")
            variable_length = int(tmp_value[1])
            if variable_length != len(one_assignment_value):
                return False

        
        
        
        # check for word conistency
        for one_assignment_key, one_assignment_value in assignment.items():
            #print(f"one_assignment = {one_assignment_key} {one_assignment_value}")
            if str(one_assignment_key).find("across") > -1:
                #print(one_assignment_key)
                across_variable_set.append(one_assignment_key) # ??????? this might need to be a list or dictionary ?????

            if str(one_assignment_key).find("down") > -1:
                #print(one_assignment_key)
                down_variable_set.append(one_assignment_key) # ??????? this might need to be a list or dictionary ?????

        
        #find where all down variables intersect with all across variables
        for down_variable in down_variable_set:
            #print(down_variable)
            for across_variable in across_variable_set:
                variable_overlaps = self.crossword.overlaps[down_variable, across_variable]
                if variable_overlaps != None:
                    # check if overlaping is character consistent
                    if assignment[down_variable][variable_overlaps[0]] != assignment[across_variable][variable_overlaps[1]]:
                        return False

        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """

        heuristicl_dict = {}
        heuristicly_ordered_list = []
        un_assigned_neighbors = []
        
        

        #find the words in var's domain
        var_domain_words = []
        for word in self.domains[var]:
            var_domain_words.append(word)
        

        # find unassigned neighbors
        neighbors =  self.crossword.neighbors(var)
        for neighbor in neighbors:
            if neighbor not in assignment:
                un_assigned_neighbors.append(neighbor)
               
        # if assigning var to a particular value results in eliminating n possible choices for neighboring variables, 
        # then order your results in ascending order of n.
        for un_assigned_neighbor in un_assigned_neighbors:
            overlaps = self.crossword.overlaps[var,un_assigned_neighbor]
            for var_domain_word in var_domain_words:
                domain_word_not_overlap_count = 0
                for un_assigned_neighbor_word in self.domains[un_assigned_neighbor]:
                    if un_assigned_neighbor_word[overlaps[1]] != var_domain_word[overlaps[0]]:
                        domain_word_not_overlap_count += 1
                heuristicl_dict[var_domain_word] = domain_word_not_overlap_count
        heristic_sorted = sorted(heuristicl_dict.items(), key=lambda heuristicl_dict: heuristicl_dict[1])
       

        for heristic_sorted_val  in heristic_sorted:
            heuristicly_ordered_list.append(heristic_sorted_val[0])
     

        if len(heuristicly_ordered_list) == 0:
            heuristicly_ordered_list = var_domain_words

        return var_domain_words

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        not_assigned_variable = []

        #find all unassigned variables
        for variable in self.crossword.variables:
            if variable not in assignment:
                not_assigned_variable.append(variable)
                
        # determine which unassigned variable has the least words in their domain
        remaining_values_count = 99999999
        MRV_Hueristic_Variable = []
        for variable in not_assigned_variable:
            if len(self.domains[variable]) <= remaining_values_count:
                MRV_Hueristic_Variable.append(variable)
                remaining_values_count = len(self.domains[variable])

        # determine which unassigned variable has the most neighbors
        Degree_Hueristic_Variable = ""
        remaining_neighbor_count = -1
        for variable in MRV_Hueristic_Variable:
            if len(self.crossword.neighbors(variable)) >= remaining_neighbor_count:
                Degree_Hueristic_Variable = variable


        return Degree_Hueristic_Variable


    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
      
        if self.assignment_complete(assignment):
            return assignment

        variable = self.select_unassigned_variable(assignment)
        hueristly_order_domain = self.order_domain_values(variable, assignment)
        for word in hueristly_order_domain:
            new_assignment = assignment.copy()
            new_assignment[variable] = word
            if self.consistent(new_assignment):
                result = self.backtrack(new_assignment)
                if result is not None:
                    return result

        return None



def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()

