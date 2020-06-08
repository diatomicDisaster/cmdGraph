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

### Running the program

To run as a standalone module, simply type the following into the command line:
```
python3 cmdGraph
```
This will open the matplotlib interactive plotting window and start the cmdGraph interactive prompt
