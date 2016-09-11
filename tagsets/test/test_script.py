import os
import pytest

from tagsets.script import ScriptContext

# Test support code


# Tests

# require command

def test_script_require_command_true():
    runner = ScriptContext({})
    code = compile("require(\"a tree is a tree is a tree\", True)",
                   '<string>', 'exec')
    runner.run_python_code(code)

def test_script_require_command_false():
    runner = ScriptContext({})
    code = compile("require(\"the end of the world is nigh\", False)",
                   '<string>', 'exec')
    runner.run_python_code(code)

# percentage command

def test_script_percentage_command_10dps():
    runner = ScriptContext({})
    code = compile("result = percentage(100/3, 1000, 10)",
                   '<string>', 'exec')
    runner.run_python_code(code)
    assert(runner.localsymbols['result'] == "3.3333333333 %")

def test_script_percentage_command_div_by_0():
    runner = ScriptContext({})
    code = compile("percentage(100, 0, 0)",
                   '<string>', 'exec')
    with pytest.raises(ZeroDivisionError):
        runner.run_python_code(code)

def test_script_percentage_command_negative_numerator():
    runner = ScriptContext({})
    code = compile("result = percentage(-10, 1, 2)",
                   '<string>', 'exec')
    runner.run_python_code(code)
    assert(runner.localsymbols['result'] == "-1000.00 %")

def test_script_percentage_command_negative_dps():
    runner = ScriptContext({})
    code = compile("result = percentage(100, 100, -1)",
                   '<string>', 'exec')
    with pytest.raises(ValueError):
        runner.run_python_code(code)

def test_script_percentage_command_negative_denominator():
    runner = ScriptContext({})
    code = compile("result = percentage(100, -1000, 0)",
                   '<string>', 'exec')
    runner.run_python_code(code)
    assert(runner.localsymbols['result'] == "-10 %")

# output_report command

# TODO define behaviour for this comamnd
def test_script_output_report_command():
    runner = ScriptContext({})
    code = compile("output_report(\"tags.html\", 'html_taglist')",
                   '<string>', 'exec')
    runner.run_python_code(code)

# print_result command

# TODO define behaviour for this comamnd
def test_script_print_result_command():
    runner = ScriptContext({})
    code = compile("print_result()",
                   '<string>', 'exec')
    runner.run_python_code(code)

