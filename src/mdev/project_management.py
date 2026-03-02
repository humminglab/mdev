# Author: Snow Yang
# Date  : 2022/03/21

import click
import subprocess
import shutil
from pathlib import Path
from typing import Dict
from urllib.parse import urlparse
from rich import print
from rich.panel import Panel

def parse_url(name_or_url: str) -> str:
    """Create a valid MXOS project url from a project name.

    Args:
        url: The URL, or a project name to turn into an URL.

    Returns:
        Dictionary containing the remote url and the destination path for the clone.
    """
    url_obj = urlparse(name_or_url)
    if url_obj.hostname:
        url = url_obj.geturl()
    elif ":" in name_or_url.split("/", maxsplit=1)[0]:
        # If non-standard and no slashes before first colon, git will recognize as scp ssh syntax
        url = name_or_url
    else:
        url = f"git@codeup.aliyun.com:mxchip/mxos/{url_obj.path}.git"
    return url

@click.command()
@click.argument("path", type=click.Path())
def new(path: str) -> None:
    """Creates a new MXOS project at the specified path.

    Arguments:

        PATH: Path to the destination directory for the project. Will be created if it does not exist.

    Example:

        $ mdev new helloworld
    """
    print(Panel(f"[green]Creating a new MXOS project at path '{path}' ...", style='green'))

    TEMPLATES_DIRECTORY = Path(Path(__file__).parent.resolve(), "templates")
    shutil.copytree(TEMPLATES_DIRECTORY, path)

    subprocess.run(['git', '-C', path, 'init'], check=True)
    subprocess.run(['git', '-C', path, 'submodule', 'add', 'git@codeup.aliyun.com:mxchip/mxos/mxos.git', 'mxos'], check=True)

    click.echo("Downloading mxos and adding it to the project ...")
    cmds = ['git', '-C', path, 'submodule', 'update', '--init', '--recursive']
    click.echo(f"Running '{' '.join(cmds)}' ...")
    subprocess.run(cmds, check=True)

@click.command()
@click.argument("url")
@click.argument("path", type=click.Path(), default="")
@click.option(
    "--branch",
    "-b",
    show_default=True,
    help="checkout <branch> instead of the remote's HEAD",
)
def import_(url: str, path: str, branch: str) -> None:
    """Clone an MXOS project and component dependencies.

    Arguments:

        URL : The git url of the remote project to clone.

        PATH: Destination path for the clone. If not given the destination path is set to the project name in the cwd.

    Example:

        $ mdev import helloworld
    """
    print(Panel(f"[green]Importing MXOS project '{url}' ...", style='green'))

    cmds = ['git', 'clone', '--recursive', parse_url(url)]
    if path:
        cmds.append(path)
    if branch:
        cmds.append('-b')
        cmds.append(branch)
    
    click.echo(f"Running '{' '.join(cmds)}' ...")
    subprocess.run(cmds, check=True)

@click.command()
@click.argument("path", type=click.Path(), default="")
def deploy(path: str) -> None:
    """Checks out MXOS project component dependencies at the revision specified in the ".component" files.

    Ensures all dependencies are resolved and the versions are synchronised to the version specified in the component
    reference.

    Arguments:
    
        PATH: Path to the MXOS project [default: CWD]

    Example:

        $ mdev deploy
    """
    print(Panel(f"[green]Fetching all the submodules and checking out the appropriate commit ...", style='green'))

    cmds = ['git', 'submodule', 'update', '--init', '--recursive']
    if path:
        cmds.append(path)
    
    click.echo(f"Running '{' '.join(cmds)}' ...")
    subprocess.run(cmds, check=True)

@click.command()
def status() -> None:
    """Show component status

    Show all component status in the current project or component.

    Example:

        $ mdev status
    """
    print(Panel(f"[green]Show status of project", style='green'))

    cmds = ['git', 'status']
    click.echo(f"Running '{' '.join(cmds)}' ...")
    subprocess.run(cmds, check=True)