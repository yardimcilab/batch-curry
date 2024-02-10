import click
import subprocess
import sys
import yaml
import os
from multiprocessing import Pool

def worker_init():
    # Ignore SIGINT in worker processes to handle KeyboardInterrupt in the main process
    import signal
    signal.signal(signal.SIGINT, signal.SIG_IGN)

def execute_command(args):
    env = os.environ.copy()
    command, arg_list, shell, dryrun = args
    wc_dict = enumerate_wildcards(arg_list)
    try:
        if shell:
            formatted_command = safe_format(command, wc_dict)
        else:
            command_list = yaml.safe_load(command)
            formatted_command = [safe_format(arg, wc_dict) for arg in command_list]
    except Exception as e:
        print(f"Error in execute_command for arg_list {arg_list} and command template {command}: {e}")
    if dryrun:
        click.echo(formatted_command)
        result = ''
    else:
        result = subprocess.run(formatted_command, shell=shell, capture_output=True, text=True, env=env)
        result = result.stdout.strip()
    return result

def execute_commands_multiprocessing(commands, arguments, shell=True, max_processes=None, dryrun=False):
    output = []
    args_for_pool = [(command, args, shell, dryrun) for args in arguments for command in commands]

    with Pool(processes=max_processes, initializer=worker_init) as pool:
        try:
            results = pool.map(execute_command, args_for_pool)
        except KeyboardInterrupt:
            pool.terminate()
            pool.join()
            sys.exit("Execution was interrupted by the user")

    # Reorganize results to match the structure of `commands` x `arguments`
    it_results = iter(results)
    for _ in arguments:
        output.append([next(it_results) for _ in commands])

    return output


def safe_format(template, kwargs):
    for wc, arg in kwargs.items():
        template = template.replace(wc, str(arg))
    return template

def enumerate_wildcards(arguments):
    wc_dict = {}
    for idx, arg in enumerate(arguments):
        wc = "{" + str(idx+1) + "}"
        wc_dict[wc] = arg
    return wc_dict

@click.command()
@click.argument('commands', nargs=-1, required=True)
@click.option("--shell/--no-shell", is_flag=True, default=True, help="Run with shell=True (--shell) or with shell=False and interpreting commands as lists of argumnets (--no-shell)")
@click.option('--max-processes', default=None, help='Limit number of processes to use for parallel execution')
@click.option('--dryrun', is_flag = True, help='Echo commands to stdout rather than running them')
def curry_batch(commands, shell, max_processes, dryrun):
    input = sys.stdin.read()
    arguments = yaml.safe_load(input)
    output = execute_commands_multiprocessing(commands, arguments, shell, max_processes, dryrun)
    if not dryrun:
        click.echo(yaml.dump(output))

if __name__ == '__main__':
    curry_batch()
