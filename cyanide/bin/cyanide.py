import os
import click
from celery import Celery
from cyanide.app import app as cyanide_app
from celery.utils.imports import symbol_by_name

@click.command(context_settings={'ignore_unknown_options': True})
@click.option('-i', '--iterations', type=int, default=50, help='Number of iterations for each test')
@click.option('-n', '--numtests', type=int, default=None, help='Number of tests to execute')
@click.option('-o', '--offset', type=int, default=0, help='Start at custom offset')
@click.option('--block-timeout', type=int, default=30 * 60, help='Block timeout in seconds')
@click.option('-l', '--list-all', is_flag=True, default=False, help='List all tests')
@click.option('-r', '--repeat', type=float, default=0, help='Number of times to repeat the test suite')
@click.option('-g', '--group', default='all', help='Specify test group (all|green|redis)')
@click.option('--diag', is_flag=True, default=False, help='Enable diagnostics (slow)')
@click.option('-J', '--no-join', is_flag=True, default=False, help='Do not wait for task results')
@click.option('-S', '--suite', default=None, help='Specify test suite to execute (path to class)')
@click.argument('names', nargs=-1)  # Arguments can be passed to the command
def cyanide_command(names, iterations, numtests, offset, block_timeout, list_all, repeat, group, diag, no_join, suite):
    """ Custom cyanide command for Celery """

    # Ensure the Celery app is correctly initialized
    app = cyanide_app

    if suite is None:
        suite = app.cyanide_suite

    # Run the suite
    try:
        run_suite(names, suite, block_timeout=block_timeout, no_color=False, iterations=iterations, numtests=numtests, offset=offset, list_all=list_all, repeat=repeat, group=group, diag=diag, no_join=no_join)
    except KeyboardInterrupt:
        print('### Interrupted by user: exiting...')

def run_suite(names, suite, block_timeout=None, no_color=False, **options):
    return symbol_by_name(suite)(
        cyanide_app,
        block_timeout=block_timeout,
        no_color=no_color,
    ).run(names, **options)

def main(argv=None):
    if argv:
        # Pass custom arguments to the Click command
        cyanide_command.main(args=argv, standalone_mode=False)
    else:
        # Run normally
        cyanide_command()

if __name__ == '__main__':
    main()
