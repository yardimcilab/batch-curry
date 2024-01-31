import click
import subprocess
import sys
import yaml
from multiprocessing import Pool

def worker_init():
    # Ignore SIGINT in worker processes to handle KeyboardInterrupt in the main process
    import signal
    signal.signal(signal.SIGINT, signal.SIG_IGN)

def execute_command(args):
    command, arg_list = args
    wc_dict = enumerate_wildcards(arg_list)
    try:
        formatted_command = safe_format(command, wc_dict)
    except Exception as e:
        print(f"Error in execute_command for arg_list {arg_list} and command template {command}: {e}")
        return None
    result = subprocess.run(formatted_command, shell=True, capture_output=True, text=True)
    return result.stdout.strip()

def execute_commands_multiprocessing(commands, arguments, max_processes=None):
    output = []
    args_for_pool = [(command, args) for args in arguments for command in commands]

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
        template = template.replace(wc, arg)
    return template

def enumerate_wildcards(arguments):
    wc_dict = {}
    for idx, arg in enumerate(arguments):
        wc = "{" + str(idx+1) + "}"
        wc_dict[wc] = arg
    return wc_dict

@click.command()
@click.argument('commands', nargs=-1, required=True)
@click.option('--max-processes', default=1, help='Maximum number of processes to use for parallel execution')
def curry_batch(commands, max_processes):
    input = sys.stdin.read()
    arguments = yaml.safe_load(input)
    output = execute_commands_multiprocessing(commands, arguments, max_processes)
    click.echo(yaml.dump(output))

if __name__ == '__main__':
    curry_batch()
