import cmd #for program commands
import argparse #for figure arguments
import numpy as np #for... need I explain?
import matplotlib #urm... seems kinda obvious
import matplotlib.pyplot as plt #convenience
import sys

_small_ = 1e-300

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
      - For a list of figure layout arguments in the current view, 
        type '-h' or '--help'.
  
  Happy plotting!
"""

### User interface object

class cmgPrompt(cmd.Cmd):
    """The cmdGraph user command prompt interface object.

    The cmdPrompt controls the operation of the program for a given figure.
    In normal operation, with a single figure instance, this amounts to the 
    entire program. 
    
    The class defines the program commands, reads/writes data files, and owns
    and passes commands to the current View instance.
    """
    prompt = '> ' #set left hand icon for prompt

    def __init__(self, mode='launch', **kwargs):
        """Initialise a new prompt mode. 
        
        Creates a figure and sets the View object and Data type specified by the 
        'mode' keyword argument. The default value is 'launch', which is used 
        when the program starts to call the Cmd superclass __init__ function. 
        Other keyword arguments are passed to the Cmd superclass.
        """
        self._modes = ['graph', 'stick'] #define available modes
        if mode == 'launch': #for first __init__
            cmd.Cmd.__init__(self, **kwargs)
            mode = 'graph' #default to graph
        if mode in self._modes:
            self.mode = mode
            self.fig = plt.figure()
            self._single = False
            if mode == 'graph':
                self._DataType = xyData #set the data mode
                self._View = GraphView(self.fig) #set the view mode
            elif mode == 'stick':
                self._DataType = stickData
                self._View = StickView(self.fig)
        else:
            print("Mode not defined.")
    def preloop(self):
        """Turn matplotlib interactive mode on before opening prompt."""
        plt.ion()
    def postloop(self):
        """Turn matplotlib interactive mode off after closing prompt."""
        plt.ioff()
    def onecmd(self, line):
        """Overwritten from default cmd.onecmd method to prevent exiting command
        loop when an error is raised.

        """
        cmd, arg, line = self.parseline(line)
        if not line:
            return self.emptyline()
        if cmd is None:
            return self.default(line)
        self.lastcmd = line
        if line == 'EOF' :
            self.lastcmd = ''
        if cmd == '':
            return self.default(line)
        else:
            try:
                func = getattr(self, 'do_' + cmd)
            except AttributeError:
                return self.default(line)
            try: #only try to execute
                f = func(arg)
            except:
                print("Command failed, check for typos.")
                print("Error type: ", sys.exc_info()[0]) #basic error message
                f = None
            return f

    ## Command methods ##
    def default(self, line):
        """Pass input string to the View instance's argparse parser if the string
        is unrecognised as a cmdPrompt command. Check if argparse has successfully
        parsed and warn if not.
        
        """
        argIn = line.split(' ') #argparse expects list of arguments
        hasParsed = self._View.parse(argIn)
        if not hasParsed: #unrecognised argparse argument
            print("Unrecognised argument.")
        else:
            self._changed = True

    def do_exit(self, inp): #not working
        """Checks if in single plot mode, if so makes all View plots live,
        and exits single mode. Otherwise, asks before exiting program.
        
        """
        if self._single:
            self._View.livePlots = self._View.plots
            self._single = False
            print("Leaving single plot mode...")
            return False
        else:
            yn = 'm'
            while yn not in ['Y', 'y', 'N', 'n']:
                yn = input("Exit the program? [y/n] ")
            if yn in ['N', 'n']:
                print("Exit cancelled.")
                return False
            elif yn in ['Y', 'y']:
                print("Exiting cmdGraph...")
                return True          
    def help_exit(self):
        print("usage: exit\n    Exit current environment, or if no environment, exit program.")

    def do_adat(self, inp):
        """Calls the read file method to initialise a Data instance for the input
        file using the active data mode. Requires that self._Data has been set 
        to a valid Data class by __init__. Then adds Data to the View instance as
        as plot.
        
        """
        for inFile in inp.split(): #assume spaces in input delimit files
            _Data = self._DataType(inFile).read_file()
            self._View.add_plot(_Data)
    def help_adat(self):
        print("usage: adat <file1> <file2> ... \n    Add lines(s) to figure from file(s). ")

    def do_ddat(self, inp):
        """Remove a data file from the figure. Not working yet, placeholder only.
        
        """
        for p, plot in enumerate(self._View.plots):
            if plot._Data.fName == inp:
                self._View.plots.remove(plot)
    def help_ddat(self):
        print("usage: ddat <file>\n    Placeholder.")

    def do_single(self, inp):
        """Replace live plots in View instance with a single plot, allows for
        tweaking of individual Plot instances within a figure without having to
        pass arguments for every other instance.
        
        Requires self.do_exit() call to terminate and return all plots to View
        live plots.
        
        """
        for plot in self._View.plots:
            _Data = plot._Data
            if _Data.fName == inp:
                self._View.livePlots = [plot] #single live plot
                self._single = True #enter single mode
                print("Entering single plot mode for '{}'".format(_Data.fName))
                break
        if not self._single:
            print("Plot file not found.")
    def help_single(self):
        print("usage: single <file>\n    Switch to single dataset edit mode.")

    def do_mode(self, inp):
        """Set the current plotting mode. Calls the cmdPrompt __init__ method
        to initialise a new View instance and change the data mode. Closes current
        figure (without saving) and opens new figure for the input View mode.
        
        """
        if inp in self._modes:
            plt.close(fig='all')
            self.__init__(mode=inp)
        else:
            print("Mode not defined.")
    def help_mode(self):
        print("usage: mode <mode>\n    Change figure mode (graph, stick)")

    def do_save(self, inp):
        """Save configuration for current figure in a native cmdGraph 'save file'.
        This is done by initialising an instance o the cmdGraph data class and
        calling it's write file method for the current View instance.
        
        """
        cmgData(inp).write_file(self._View)
        self._changed = False
    def help_save(self):
        print("usage: save <filename>\n    Save the current figure as <filename>.cmg, allows figures to be reload after exit.")

    def do_load(self, inp):
        """Load a View instance from a cmdGraph 'save file' by initialising a
        cmdGraph data instance and calling it's read file method. Then pass
        each item in the data attribute as though it were a user command.
        
        """
        buff = cmgData(inp).read_file()
        for cmdString in buff.dat:
            self.onecmd(cmdString)
        if self._single:
            self.do_exit('')
    def help_load(self):
        print("usage: load <filename>.cmg\n    Load figure from cmdGraph file.")

    def do_print(self, inp):
        """Rudimentary print figure to file. Redirects to plt.savefig(), the
        filetpye is automatically chosen from the suffix used in the input
        string, i.e '.pdf', '.jpg'.
        
        """
        plt.savefig(inp)


### View Classes

class _View:
    """The superclass for View modes. 
    
    Defines basic properties required for a View object to function within the 
    program, but should always be expanded with custom methods.

    Every View instance has a Plot class. Instances of a Plot class are
    associated with a data file for the current View instance, and have a set
    of commands that can be passed by the user to edit their properties and call
    methods. View instances also have an axes. 
    
    Currently axes are not defined as an inner class, but this might change if 
    View modes are introduced with multiple axes.
    
    See existing subclasses for examples.
    """
    def __init__(self, figure=None, mode=None):
        """View mode superclass with necessary functions, do not overwrite."""
        self.fig       = figure
        self.mode      = mode
        self.plots     = []
        self.livePlots = self.plots
        self.argNames  = []
        self.parser    = argparse.ArgumentParser(
            usage="Figure commands should have a '-' or '--' in front.\n"
            "       Type '-h' for a list of figure commands available in the current mode."    
        )
    def parse(self, inp):
        """Method for parsing arguments using the parser defined for the future
        View subclass. Tries argument and if not parsed returns false to the
        cmdPrompt instance. Otherwise attempts to set attribute of axes, and
        then of plots if command is not recognised as an axes property.

        """
        try: #catch argparse system exit
            args = self.parser.parse_args(inp) #use argparse to parse args
        except:
            return False
        for argName in self.argNames:
            if hasattr(args, argName):
                inp = getattr(args, argName)
                if hasattr(self, '_set_'+argName): #axes command?
                    _set = getattr(self, '_set_'+argName)
                    _set(inp)
                else: #plot command?
                    for p, plot in enumerate(self.livePlots):
                        _set = getattr(plot, '_set_'+argName)
                        _set(inp[p])
        return True

    def _add_arg(self, *args, **kwargs):
        """Adds argument to View instance, essentially a wrapper for argparse
        'add_argument' that forces default to SUPPRESS and adds the argument
        name to an internal list.

        Every argument should have an associated 'self._set_<argument>' method, 
        the first action of which should always be to set 'self._prop_<argument>' 
        equal to the console input. Without '_prop_' attributes, the 
        configuration cannot be saved, and without '_set_' methods the argument
        will not activate any change.
        
        """
        self.parser.add_argument(*args, **kwargs, default=argparse.SUPPRESS)
        self.argNames.append(args[1].lstrip('--'))

    class Plot:
        def __init__(self, data, ax):
            """Template class for the View subclass's Plot class. The Plot class
            define the type of graph the user is plotting, and has associated
            properties and methods. All plot instances should however have an
            associated data object (data) and axes (ax). 
            
            The __init__ function is called by the cmdPrompt adat method when
            a data file is added to the current View instance.
            
            """
            self._Data = data
            self.ax  = ax

    def add_plot(self, data):
        """Method for adding a Plot instance to the current View with data from
        a given Data object. Adds plot to list of plots in current View and resets
        live plots. Assumes plot is being added to current matplotlib axes.
        
        """
        plot = self.Plot(data, plt.gca())
        self.plots.append(plot)
        self.livePlots = self.plots
            
class GraphView(_View):
    """Simple x-y data View class.
    
    The GraphView class is a simple View class for plotting x-y data points. It
    consists of a single axes, and can contain any number of xyData Plot objects.
    It is also the default View mode opened when the program starts.

    """
    def __init__(self, fig):
        """Add axes to the provided figure and set the view mode to 'graph'. The
        available arguments for the user in view mode are defined below, and each
        has a '_set_<argument>' method further down that is called when the
        argument is parsed.
        
        """
        _View.__init__(self, figure=fig, mode='graph')
        self.ax = fig.add_subplot(111)
        # Line arguments
        self._add_arg('-lw', '--linewidth',  nargs='+', type=float, metavar='float', 
            help="Width of plot line.")
        self._add_arg('-lc', '--linecolour', nargs='+', type=str,   metavar='str',
            help="line colours for plots in figure (any valid matplotlib colour, e.g 'red', 'blue')")
        self._add_arg('-ls', '--linestyle',  nargs='+', type=str,   metavar='str',
            help="line styles for plots in figure (any valid matplotlib style, e.g '-', '--', 'none')")
        self._add_arg('-m',  '--marker',     nargs='+', type=str,   metavar='str',
            help="marker styles for plots in figure (any valid matplotlib style, e.g 'o', 'x', 'none')")
        self._add_arg('-ms', '--markersize', nargs='+', type=str,   metavar='float',
            help="marker sizes for plots in figure(any valid matplotlib style, e.g '-', '--', 'none')")
        self._add_arg('-l',  '--label',      nargs='+', type=str,   metavar='str',
            help="labels for plots in figure legend, use '#' for spaces")
        # Axis arguments
        self._add_arg('-xr', '--xrange', nargs=2, type=str, metavar='float',
            help="min and max range of figure x-axis, use * * to automatically choose value")
        self._add_arg('-yr', '--yrange', nargs=2, type=str, metavar='float',
            help="min and max range of figure y-axis, use * * to automatically choose value")
        # Note: argparse does not always handle more exotic variable types and
        # uses in the expected manner. As a result we prefer to use either float
        # or int values, and parse arrays, tuples etc. as multiple arguments, or
        # booleans as strings.

    # Axes methods
    def _set_xrange(self, inp):
        """Set the x range of axis. If an asteriks is detected in place of a
        float for either value then that bound is autoscaled.
        
        """
        self._prop_xrange = inp
        inp = inp.split()
        if any([i == '*' for i in inp]):
            self.ax.autoscale(enable=True, axis='x')
        if inp[0] != '*':
            self.ax.set_xlim(xmin=float(inp[0]))
        if inp[1] != '*':
            self.ax.set_xlim(xmax=float(inp[1]))
    def _set_yrange(self, inp):
        """Set the y range of axis. If an asteriks is detected in place of a
        float for either value then that bound is autoscaled.
        
        """
        self._prop_yrange = inp
        inp = inp.split()
        if any([i == '*' for i in inp]):
            self.ax.autoscale(enable=True, axis='y')
        if inp[0] != '*':
            self.ax.set_ylim(ymin=float(inp[0]))
        if inp[1] != '*':
            self.ax.set_ylim(ymax=float(inp[1]))

    # View Plot objects
    class Plot(_View.Plot):
        """The Plot object for the GraphView class. Called by cmdPrompt to
        initialise a plot object in the current View instance for a new data file.
        
        """
        def __init__(self, data, ax):
            """Add plot points from Data object to provided axes from the parent 
            View instance. Call the superclass __init__ to store the associated
            Data object and axes for this Plot.
            
            Arguments specified in the parent View instance's __init__ method
            that act on plots have their '_set_' methods defined here. Every
            '_set_' method should first store the input value in the relevant
            '_prop_' attribute to allow the configuration to be written to file.

            """
            _View.Plot.__init__(self, data, ax)
            x, y = self._Data.dat
            self._plot, = ax.plot(x, y)
        # Line methods
        def _set_linewidth(self, inp):
            """Set line width of plot."""
            self._prop_linewidth = inp
            inp = float(inp)
            plt.setp(self._plot, linewidth=inp)
        def _set_linecolour(self, inp):
            """Set line colour of plot."""
            self._prop_linecolour = inp
            plt.setp(self._plot, color=inp)
        def _set_linestyle(self, inp):
            """Set line style of plot."""
            self._prop_linestyle = inp
            plt.setp(self._plot, ls=inp)
        def _set_marker(self, inp):
            """Set marker style of plot."""
            self._prop_marker = inp
            plt.setp(self._plot, marker=inp)
        def _set_markersize(self, inp):
            """Set size of plot markers."""
            self._prop_markersize = inp
            inp = float(inp)
            plt.setp(self._plot, ms=inp)
        def _set_label(self, inp):
            """Set legend labels of plot."""
            self._prop_label = inp
            if inp is 'none': #line has no label
                plt.setp(self._plot, label='__nolegend__')
            else:
                inp = inp.replace('#', ' ')
                plt.setp(self._plot, label=inp)
            plt.legend()

class StickView(_View):
    """Simple x-y data View class.
    
    The GraphView class is a simple View class for plotting x-y data points. It
    consists of a single axes, and can contain any number of xyData Plot objects.
    It is also the default View mode opened when the program starts.

    """
    def __init__(self, fig):
        """Add axes to the provided figure and set the view mode to 'graph'. The
        available arguments for the user in view mode are defined below, and each
        has a '_set_<argument>' method further down that is called when the
        argument is parsed.
        
        """
        _View.__init__(self, figure=fig, mode='stick')
        self.ax = fig.add_subplot(111)
        self.ax.set_yscale('log')
        # Line arguments
        self._add_arg('-lw', '--linewidth',  nargs='+', type=float, metavar='float', 
            help="Width of plot line.")
        self._add_arg('-lc', '--linecolour', nargs='+', type=str,   metavar='str',
            help="line colours for plots in figure (any valid matplotlib colour, e.g 'red', 'blue')")
        self._add_arg('-l',  '--label',      nargs='+', type=str,   metavar='str',
            help="labels for plots in figure legend, use '#' for spaces")
        # Axis arguments
        self._add_arg('-xr', '--xrange', nargs=2, type=str, metavar='float',
            help="min and max range of figure x-axis, use * * to automatically choose value")
        self._add_arg('-yr', '--yrange', nargs=2, type=str, metavar='float',
            help="min and max range of figure y-axis, use * * to automatically choose value")
        # Note: argparse does not always handle more exotic variable types and
        # uses in the expected manner. As a result we prefer to use either float
        # or int values, and parse arrays, tuples etc. as multiple arguments, or
        # booleans as strings.

    # Axes methods
    def _set_xrange(self, inp):
        """Set the x range of axis. If an asteriks is detected in place of a
        float for either value then that bound is autoscaled.
        
        """
        self._prop_xrange = inp
        inp = inp.split()
        if any([i == '*' for i in inp]):
            self.ax.autoscale(enable=True, axis='x')
        if inp[0] != '*':
            self.ax.set_xlim(xmin=float(inp[0]))
        if inp[1] != '*':
            self.ax.set_xlim(xmax=float(inp[1]))
    def _set_yrange(self, inp):
        """Set the y range of axis. If an asteriks is detected in place of a
        float for either value then that bound is autoscaled.
        
        """
        self._prop_yrange = inp
        ymin, ymax = inp.split()
        ylow = 0
        self.ax.autoscale(enable=True, axis='y')
        if ymin == '*':
            for plot in StickView.plots:
                ylow = plot.data.ybounds[0] if ylow > plot.data.ybounds[0] else ylow
            self.ax.set_ylim(ymin=.1*ylow)
        else:
            self.ax.set_ylim(ymix=float(ymax))
        if ymax != '*':
            self.ax.set_ylim(ymax=float(ymax))

    # View Plot objects
    class Plot(_View.Plot):
        """The Plot object for the GraphView class. Called by cmdPrompt to
        initialise a plot object in the current View instance for a new data file.
        
        """
        def __init__(self, data, ax):
            """Add plot points from Data object to provided axes from the parent 
            View instance. Call the superclass __init__ to store the associated
            Data object and axes for this Plot.
            
            Arguments specified in the parent View instance's __init__ method
            that act on plots have their '_set_' methods defined here. Every
            '_set_' method should first store the input value in the relevant
            '_prop_' attribute to allow the configuration to be written to file.

            """
            _View.Plot.__init__(self, data, ax)
            sticks = self._Data.dat
            self._plot = ax.add_collection(
                matplotlib.collections.LineCollection(sticks))
            StickView._set_xrange(self, '* *')
            StickView._set_yrange(self, '* *')
        # Line methods
        def _set_linewidth(self, inp):
            """Set line width of plot."""
            self._prop_linewidth = inp
            inp = float(inp)
            plt.setp(self._plot, linewidth=inp)
        def _set_linecolour(self, inp):
            """Set line colour of plot."""
            self._prop_linecolour = inp
            plt.setp(self._plot, color=inp)
        def _set_label(self, inp):
            """Set legend labels of plot."""
            self._prop_label = inp
            if inp is 'none': #line has no label
                plt.setp(self._plot, label='__nolegend__')
            else:
                inp = inp.replace('#', ' ')
                plt.setp(self._plot, label=inp)
            plt.legend()


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
    def write_file(self, fName, view):
        """Write the View instance to a '.cmg' file with provided name. 
        
        Tries to retrieve corresponding '_prop_' attribute for every argument in
        the View instance's list of argument names. First at the level of View
        attributes for axes arguments, or else at the level of Plot attributes
        for plot arguments.

        """

        f = open(self.fName, 'w')
        f.write("---cmdGraph---" + '\n')
        f.write("mode " + view.mode + '\n')
        f.write(("adat " + " {}"*len(_View.plots)
            + '\n').format(*[P._Data.fName for P in _View.plots]))
        _plotArgs = []
        for argName in view.argNames:
            try:
                argVal = getattr(view, '_prop_' + argName)
                argVal = str(argVal) if (type(argVal) is not str) else argVal
                f.write('--' + argName + ' ' + argVal + '\n')
            except:
                _plotArgs.append(argName)
        for plot in _View.plots:
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
            for l, line in enumerate(f):
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

print(welcome_message) #print welcome message
cmgPrompt(mode='launch').cmdloop() #run program