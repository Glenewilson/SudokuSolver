import click
from sudoku import SudokuV1
import csv

@click.group(invoke_without_command=True)
@click.option("--command", prompt=">")
@click.pass_context
def cli(ctx, command):
    cmd = ""
    try:
        cmd = cli.get_command(ctx, command)
        #click.echo("got cmd: " + str(cmd))
        ctx.invoke(cmd)
    except click.exceptions.Abort:
        raise click.exceptions.Abort()
    except:
        print("got command " + str(cmd) + " and didn't recognize it")
        print(help_str)

help_str = """
Sudoku solver - starts with an empty grid. As initial values are set the solver reduces the possible values. Hopefully, after all initial values are set the solver resolves the puzzle.

valid commands:
\tset - Set a value.
\tp - Print out the current state of the grid.
\t    Each cell, or element in the grid displays the remaining possible values.
\t    If only one value is left AND it looks like *V* in the center of the grid,
\t    then it is the final value, not just the last remaining possibility.
\tf - Read in a file of initial values.
\te - Evaluate the Grid with the rules.
\th - Print out this help.
\tq - Quit.
"""
            
@cli.command(name='set')
def command1():
    row = click.prompt('row', type=click.IntRange(1,9)) - 1
    col = click.prompt('col', type=click.IntRange(1,9)) - 1
    val = click.prompt('val', type=click.IntRange(1,9))
    click.echo("got " + str(row) + "," + str(col) + " value: " + str(val))
    myGrid.setValue(row, col, val)

@cli.command(name='f')
def readFile():
    #print('in readFile')
    inputFile = click.prompt('input', type=click.STRING)
    #print('input file is ' + str(inputFile))
    with open (inputFile, newline='') as csvFile:
        reader = csv.reader(csvFile)
        for row in reader:
            print(str(row))
            myGrid.setValue(int(row[0]) - 1, int(row[1]) - 1, int(row[2]))

@cli.command(name='e')
def evaluateGrid():
    myGrid.evaluate()

@cli.command(name='p')
def gridPrint():
    print("printing grid")
    print(myGrid.pretty_print())

@cli.command(name='q')
def quitapp():
    print("bye")
    raise click.exceptions.Abort()
    
@cli.command(name='h')
def help():
    print(help_str)

def main():
    while True:
        try:
            cli.main(standalone_mode=False)
        except click.exceptions.Abort:
            break

myGrid = SudokuV1.Grid()
                                    
if __name__ == '__main__':
    main()