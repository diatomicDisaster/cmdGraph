import cmd #for program commands
import argparse #for figure arguments
import numpy as np #for... need I explain?
import matplotlib #urm... seems kinda obvious
import matplotlib.pyplot as plt #convenience
import sys

_small_ = 1e-300

### Data Classes 

class _Data:
    def __init__(self, filename):
        self.fName = filename

class xyData(_Data):
    """Data format for two column x, y data files where each row is a data point.
    assumes no column headers. Currently just a skeleton class for basic operation."""
    def read_file(self):
        """Read x, y columns from file"""
        with open(self.fName, 'r') as f:
            datLines = []
            for l in f:
                line = l.strip().split()
                datLines.append(line)
            self.dat = np.array(datLines, dtype=float).T
        return self

class stickData(_Data):
    def read_file(self):
        with open(self.fName, 'r') as f:
            datLines = []
            ymin = ymax = 0
            for l in f:
                x, y = l.strip().split()
                datLines.append([[x, _small_], [x, y]])
                ymin = float(y) if (float(y) < ymin) else ymin
                ymax = float(y) if (float(y) > ymax) else ymax
            self.dat = np.array(datLines, dtype=float)
            self.ybounds = [float(ymin), (ymax)]
        return self

class cmgData(_Data):
    """Data format for internal cmdGraph data files. This allows configurations
    to be saved so that they can be transferred and reloaded after the program
    exits.

    The format of cmdGraph save files is simply a list of commands to be executed 
    to reproduce the configuration from the input data files. A standard save file
    would look like:

    | ---cmdGraph---                    <- file header confirms cmdGraph format
    | mode graph                        <- select view mode
    | adat file1.csv file2.csv          <- load data files
    | --xrange 0 10                     <- axes arguments
    | --yrange -1 1                     <-
    | single file1.csv                  <- enter single mode for first file
    | --linewidth 2.0                   <- plot arguments of first file
    | --label The#first#data
    | single file2.csv                  <- enter single mode for second file
    | --label The#second#data           <- plot arguments of second file
    | --linecolour red

    """
    def write_file(self, view):
        """Write the View instance to a '.cmg' file with provided name. 
        
        Tries to retrieve corresponding '_prop_' attribute for every argument in
        the View instance's list of argument names. First at the level of View
        attributes for axes arguments, or else at the level of Plot attributes
        for plot arguments.

        """

        f = open(self.fName, 'w')
        f.write("---cmdGraph---" + '\n')
        f.write("mode " + view.mode + '\n')
        f.write(("adat " + " {}"*len(view.plots)
            + '\n').format(*[P._Data.fName for P in view.plots]))
        _plotArgs = []
        for argName in view.argNames:
            try:
                argVal = getattr(view, '_prop_' + argName)
                argVal = str(argVal) if (type(argVal) is not str) else argVal
                f.write('--' + argName + ' ' + argVal + '\n')
            except:
                _plotArgs.append(argName)
        for plot in view.plots:
            f.write('single ' + plot._Data.fName + '\n')
            for argName in _plotArgs:
                try:
                    argVal = getattr(plot, '_prop_' + argName)
                    argVal = str(argVal) if (type(argVal) is not str) else argVal
                    f.write('--' + argName + ' ' + argVal + '\n')
                except:
                    pass
        f.close()

    def read_file(self):
        """Read a View instance from file and return the list of command strings 
        to be executed in order to recover the figure.

        """
        with open(self.fName, 'r') as f:
            datLines = []
            start = False
            for line in f:
                line = line.strip()
                while not start:
                    if line == '---cmdGraph---':
                        start = True
                        line = ''
                    continue
                if line == '':
                    continue
                else:
                    datLines.append(line)
        if not start:
            print("Not recognised as a cmdGraph file.")
        else:
            self.dat = datLines
        return self
