"""The config subcommand for opsdroid cli."""

import click

from opsdroid.cli.utils import (
    edit_files,
    warn_deprecated_cli_option,
    validate_config,
    list_all_modules,
    path_option,
)
from opsdroid.const import EXAMPLE_CONFIG_FILE


def print_example_config(ctx, param, value):
    """[Deprecated] Print out the example config.

    Args:
        ctx (:obj:`click.Context`): The current click cli context.
        param (dict): a dictionary of all parameters pass to the click
            context when invoking this function as a callback.
        value (bool): the value of this parameter after invocation.
            Defaults to False, set to True when this flag is called.

    Returns:
        int: the exit code. Always returns 0 in this case.

    """
    if not value or ctx.resilient_parsing:
        return
    if ctx.command.name == "cli":
        warn_deprecated_cli_option(
            "The flag --gen-config has been deprecated. "
            "Please run `opsdroid config gen` instead."
        )
    with open(EXAMPLE_CONFIG_FILE, "r") as conf:
        click.echo(conf.read())
    ctx.exit(0)


@click.group()
def config():
    """Subcommands related to opsdroid configuration."""


@config.command()
@click.pass_context
def gen(ctx):
    """Print out the example config.

    This is a pretty basic function that will simply open your opsdroid
    configuration file and prints the whole thing into the terminal.

    Args:
        ctx (:obj:`click.Context`): The current click cli context.

    Returns:
        int: the exit code. Always returns 0 in this case.

    """
    print_example_config(ctx, None, True)


@config.command()
@click.pass_context
def edit(ctx):
    """Open config file with your favourite editor.

    By default this command will open the configuration file with
    vi/vim. If you have a different editor that you would like to sure,
    you need to change the environment variable - `EDITOR`.

    Args:
        ctx (:obj:`click.Context`): The current click cli context.

    Returns:
        int: the exit code. Always returns 0 in this case.

    """
    edit_files(ctx, None, "config")


@config.command()
@click.pass_context
@path_option
def lint(ctx, path):
    """Validate the configuration.

    This subcommand allows you to validate your configuration or a configuration
    from a file if the -f flag is used. This avoids the need to start the bot just
    to have it crash because of a configuration error.

    This could also be helpful if you need to do changes to the configuration but
    you are unsure if everything is set correct. You could have the new config
    file located somewhere and test it before using it to start opsdroid.

    Args:
        ctx (:obj:`click.Context`): The current click cli context.
        path (str): Path obtained by using the -f flag, if provided it will only
        validate the config of the file.

    Returns:
        int: the exit code. Always returns 0 in this case.

    """
    validate_config(ctx, path, "config")


@config.command()
@click.pass_context
@path_option
def list_modules(ctx, path):
    """Print out a list of all active modules.

    This function will try to get information from the modules that are active in the
    configuration file and print them as a table or will just print a sentence saying that
    there are no active modules for that type.

    Args:
        ctx (:obj:`click.Context`): The current click cli context.
        path (str): Path obtained by using the -f flag, if provided it will only list
        the active modules of this file.

    """
    list_all_modules(ctx, path, "config")
