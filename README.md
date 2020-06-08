# cmdGraph

The cmdGraph program is an interactive, command line plotting tool that acts as a UI for Python's matplotlib library. It's akin to *gnuplot* except it has a miniscule fraction of the functionality, it's littered with bugs and it's barely supported. The only advantage is that the graphs it produces look slightly prettier.

## Getting Started

### Installing the program

The program is packaged as a Python library, but can be run independently as a standalone module. Either installation method will provide the `cmdGraph` directory which contains all the submodules of the program.

1. To download the files directly, go to https://github.com/diatomicDisaster/neo, click the green button on the right hand side "Clone or Download" and select "Download ZIP".

2. To install from the command line, using git:
```
git clone https://github.com/diatomicDisaster/cmdGraph.git
```

#### Dependencies

The following Python 3 libraries are required to run the cmdGraph program:
- numpy
- matplotlib

#### Running the program

To run as a standalone module, simply type the following into the command line:
```
python3 cmdGraph
```
This will open the matplotlib interactive plotting window and start the cmdGraph interactive prompt. The prompt accepts two types of commands: console commands, and figure commands. The former are the set of commands used for controlling the cmdGraph program itself, e.g adding data, saving/loading configurations, or printing images to files. The latter are the commands used to control the appearance of the current figure, e.g line styles, plot/axis labels, axes ranges, etc. Figure commands are distinguished from console commands by a prefixing dash '-' or double dash '--'.

### Adding Data

To plot data, we first select a plotting mode. There are currently two modes: `graph` and `stick`, the former is used for plotting conventional x, y data such as lines and scatter plots, while the latter can be used for plotting stick spectra.The default plotting mode when the program is opened is `graph`. The plotting mode is selected with the `mode` console command:
```
> mode stick
```
Each dataset should be provided as a separate input file, with two columns containing the x, y data. Datasets can be added simultaneously, or individually, using the `adat` command:
```
> adat <file1> <file2> ...
```
Note that the program does not store the data internally, and so a permanent reference to the file is required to reload the configuration.

### Saving/Loading Configurations

Once you have finished adjusting the figure, the configuration can be saved to a cmdGraph '.cmg' file, with the `save` command:
```
> save <filename>.cmg
```
If no file name is given, the default file is 'autosave.cmg'. Previous configurations can be loaded into the program from the '.cmg' format with the `load` command:
```
> load <filename>.cmg
```
The '.cmg' file format consists of an initial header `---cmdGraph---`, followed by a series of commands that the program executes to recreate the configuration. Thus it is possible to pre-program a configuration in a text file before starting the program, or to edit saved configurations outside of the program.
