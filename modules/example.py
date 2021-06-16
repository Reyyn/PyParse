# This file serves as an example for developing custom log parsers


# All modules require the manual function. It serves as a guide for the user for required/optional
# parameters to parse logs.
def manual():
    print("This is my usage guide")


# All modules use this function to write to disk.
def output(outfile: str, entries: list, verbose: bool = False):
    # Do any processing of entries to make suitable for writing to disk

    # Write new parsed log file
    try:
        with open('output\\' + outfile, 'w') as f:
            # Write the output to disk
            pass

        print("\nParsed log can be found in output\\" + outfile)
        return True
    except Exception as e:
        print("Error writing output to disk!" if not verbose else e)
        return False


# All module require the execute function. It serves as the entry point for the log parser script
def execute(logfile: str, outfile: str, verbose: str, arglist: dict = None):
    print(f"I have this {logfile} to parse")
    print(f"I will write to this file when done: {outfile}")
    print(f"I was given this list of arguments: {arglist}")
    if verbose:
        print("I will print extra processing information")

    output()
