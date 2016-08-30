
from termcolor import colored

# Script commands

def require(description, assertion):
    print("%s : %s" % (description, colored("pass", 'green') if assertion else colored("FAIL", 'red')))

def percentage(numerator, denominator, places = 0):
    return "{0:0.{1}f} %".format( 100.0 * numerator / denominator, places )

def output_report(filename, report_type, *args):
    # TODO - implement this
    pass

def print_result():
    print("Overall result: %s" % colored("TODO", 'red'))

SCRIPTCOMMANDS = {"require": require,
                  "percentage": percentage,
                  "print_result": print_result,
                  "output_report": output_report,
}

# Script runner / context

class ScriptContext:
    def __init__(self, tsmap):
        self.globalsymbols = SCRIPTCOMMANDS.copy()
        self.localsymbols = tsmap.copy()

    def run_python_code(self, code):
        exec(code, self.globalsymbols, self.localsymbols)

    def run_python_file(self, filename):
        with open(filename) as f:
            code = compile(f.read(), filename, 'exec')
        self.run_python_code(code)
