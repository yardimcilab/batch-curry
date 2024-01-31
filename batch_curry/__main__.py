import click
import subprocess
import sys
import yaml
import pandas as pd
from io import StringIO

def safe_format(template, kwargs):
    for wc, arg in kwargs.items():
        template = template.replace(wc, arg)
    return template

def enumerate_wildcards(arguments):
    wc_dict = {}
    for idx, arg in enumerate(arguments):
        wc = "{" + str(idx+1) + "}"
        wc_dict[wc] = arg
    return wc_dict

def execute_commands(commands, arguments):
    output = []
    for args in arguments:
        output_line = []
        wc_dict = enumerate_wildcards(args)
        for command in commands:
            try:
                formatted_command = safe_format(command, wc_dict)
            except:
                print(f"Error in execute_commands in template-filter for args {args} and command template {command}")
                sys.exit(1)
            result = subprocess.run(formatted_command, shell=True, capture_output=True, text=True)
            output_line.append(result.stdout.strip())
        output.append(output_line)
    return output

@click.command()
@click.argument('commands', nargs=-1, required=True)
def batch_curry(commands):
    input = sys.stdin.read()
    arguments = yaml.safe_load(input)
    output = execute_commands(commands, arguments)
    click.echo(yaml.dump(output))

if __name__ == '__main__':
    batch_curry()
