import cmd #for program commands
import argparse #for figure arguments
import numpy as np #for... need I explain?
import matplotlib #urm... seems kinda obvious
import matplotlib.pyplot as plt #convenience
import sys

from cmg.prompt import run

welcome_message = """
    ==================================================================
                                   __        _           
                         _ __  _| / _  __ _ |_)|_        
                        (_ |||(_| \__| | (_||  | |       
                                                        
    ==================================================================
                            W. Somogyi (2020)          
    
    Welcome to cmdGraph, an interactive command-based Python plotter!
    
    Just a few notes before you begin:
        - This is very much not a real proper program. I accept no
        liability for any harm (physical, financial, or otherwise), 
        that may come as a result of its use.
        - Console commands are keywords entered directly into the prompt.
        - For a list of console commands, type 'help' or for details
            of each command 'help <cmd>'. 
        - Figure layout commands have '-' or '--' prefixes. 
        - For a list of figure layout arguments in the current viewing
            mode, type '-h' or '--help'.
    
    Happy plotting!
"""

if __name__ == "__main__":
    print(welcome_message) #print welcome message
    run()