# Standard Python Libraries
import argparse
from pathlib import Path
from os import walk, getcwd
import sys
from importlib import import_module, invalidate_caches
from multiprocessing import Pool, cpu_count

# Third party libraries
from rich.console import Console

# Project Libraries
from src.display import logo

# Some constants
version = "0.1.0"


# Define arguments
def set_args(parser):
    # processing arguments
    parser.add_argument("logtype",
                        action='store',
                        nargs="?",
                        help="Type of logfile")
    parser.add_argument("-i", "--logfile",
                        action='store',
                        required=False,
                        help="Log file to parse")
    parser.add_argument("-o", "--outfile",
                        nargs="?",
                        required=False,
                        default="",
                        help="Output file containing the parsed log")
    parser.add_argument("-l", "--list",
                        action='store_true',
                        required=False,
                        help="Process each file in the input directory with the given parser module, and output the "
                             "logs as log-name--output.log NOTE: -i is ignored in this case.")

    # optional arguments
    parser.add_argument('-r', '--module-args',
                        nargs='*',
                        help="Additional arguments to be sent to the log processing module")
    parser.add_argument('-v', '--verbose',
                        action='store_true',
                        help="Display verbose parsing information")
    parser.add_argument('-m', '--manual',
                        action='store_true',
                        help="Display quick use guide for the given log parser")

    parser.add_argument('--modules',
                        action='store_true',
                        help="Display list of modules found in \\modules")
    parser.add_argument('--version',
                        action='version',
                        version=f'%(prog) {version}')


# Module argument parser. These can either be parameters (key=value) or a boolean flag
def module_args(arglist: list) -> dict:
    args = {}
    if arglist is not None:
        for arg in arglist:
            # Parameter
            if '=' in arg:
                temp = arg.split('=')
                args[temp[0]] = temp[1]
            # Or a bool flag
            else:
                args[arg] = True

    return args


# Module handler
def call_module(logtype: str, log: str = "", out: str = "", arglist: list = None, verbose: bool = False, manual: bool = False):
    # Find and load the parser module located in \modules
    module = import_module(f".{logtype}", package="modules")

    # Check if we want to display the use guide
    if manual:
        print()
        try:
            module.manual()
        except:
            print("Module does not have a provided usage guide.")
    # Otherwise execute the parser module
    else:
        # first check the out put file name. If blank, use default
        if out == "":
            # check path delim character
            if '/' in log:
                delim = '/'
            else:
                delim = '\\'

        out = log.split(delim)[-1] + "--output.log"

        try:
            module.execute(log, out, verbose, module_args(arglist))
        except AttributeError:
            print("Not a valid module!")
        except Exception as e:
            print("Error in module!" if not verbose else f"Error in module! --- {e}")


# Script entry point
def main():
    # Create arg parser
    parser = argparse.ArgumentParser(
        description=f"PyParser - {version} :\n This python script attempts to use a python parser module defined in "
                    f"\\modules to interpret a recovered log file. The resultant parsed log is output to a file for "
                    f"analyst use.",
        epilog="DISCLAIMER: Parsed logs are not guaranteed to be accurate. Accuracy is determined by the module "
               "and the documentation available to the creator of that module."
    )
    set_args(parser)

    # Parse args
    args = parser.parse_args()

    if args.modules:
        print("\nAvailable logtype modules can be found in \\modules:")
        _, _, files = next(walk('.\\modules'))
        for file in files:
            print(file[:-3])
        sys.exit()

    # create rich console
    console = Console()

    # Begin program output
    print(logo)
    #print(args)
    console.print("Attempting log parse ....", style="bold")

    # Check that we have the module
    have_module = False
    if Path(f"modules\\{args.logtype}.py").is_file():
        out = f"Log Type: {args.logtype} -- [green]Found Module[/green]"
        have_module = True
    else:
        out = f"Log Type: {args.logtype} -- [red]No Module[/red]"
    console.print(out)

    if not have_module:
        console.print("\nModule not found. EXITING", style="red bold")
        sys.exit()

    # Check if we are displaying the quick use guide
    if args.manual or (args.logfile is None and args.list is None):
        call_module(args.logtype, manual=True)
        sys.exit()

    have_file = False
    if args.logfile is not None:
        # Check that file exists
        if Path(f"{args.logfile}").is_file():
            out = f"Log File: {args.logfile} -- [green]Found Log File[/green]"
            have_file = True
        else:
            out = f"Log File: {args.logfile} -- [red]No Log File[/red]"
        console.print(out + "\n")

    if not have_file and not args.list:
        console.print("\nLogfile not found. Input directory empty. EXITING", style="red bold")


    # Hand off processing to log module
    # Single file mode
    if have_file:
        console.print(f"Calling {args.logtype} log parser....")
        call_module(args.logtype, log=args.logfile, out=args.outfile, arglist=args.module_args, verbose=args.verbose)
    # Multi file mode
    elif args.list:
        # Get log list from input directory
        _, _, log_list = next(walk('.\\input'))

        # Do parallel log processing
        pool = Pool()
        results = \
            [pool.apply(call_module, args=(args.logtype, log, args.outfile, args.module_args)) for log in log_list]
        pool.close()


if __name__ == "__main__":
    main()
