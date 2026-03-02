# Author: Snow Yang
# Date  : 2022/09/29

import os
import click
from mdev.mflash import mflash
from subprocess import CalledProcessError

from rich.progress import *
from rich import print
from rich.panel import Panel

@click.group()
def flash() -> None:
    pass


def update_write(out, bar):
    if '%' not in out:
        return
    if not bar.erase_start:
        bar.start_task(bar.erase_task)
        bar.update(bar.erase_task, completed=100)
        bar.erase_start = True
    pos = int(out[:-1], 0)
    bar.update(bar.write_task, completed=pos * bar.step)


@click.command()
@click.argument("chip")
@click.argument("addr")
@click.argument("image", type=click.Path())
def write(chip: str, addr: str, image: str):
    """
    Write image into flash

    Arguments:

        CHIP    Chip name, current support: rtl8762c, mx1270, mx1290, mx1300, mx1310, mx1350

        ADDR    Start address

        IMAGE   Image file

    Example:

        $ mdev flash write mx1300 0x20000 app.bin
    """
    with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeRemainingColumn(),
            TransferSpeedColumn()) as bar:
        image_size = os.path.getsize(image)
        bar.step = image_size / 100
        bar.erase_task = bar.add_task("[green]Erase", total=100, start=False)
        bar.erase_start = False
        bar.write_task = bar.add_task("[green]Write", total=image_size)
        __mflash = mflash.Mflash(chip, update_write, context=bar)
        try:
            __mflash.write(image, int(addr, 0))
        except CalledProcessError as e:
            print(Panel.fit(f"[red]{e.cmd}", title="Failed", style='red'))
            exit(1)

def update_read(out, bar):
    if '%' not in out:
        return
    pos = int(out[:-1], 0)
    bar.update(bar.read_task, completed=pos * bar.step)


@click.command()
@click.argument("chip")
@click.argument("addr")
@click.argument("size")
@click.argument("image", type=click.Path())
def read(chip: str, addr: str, size: str, image: str):
    """
    Read image from flash

    Arguments:

        CHIP    Chip name, current support: rtl8762c, mx1270, mx1290, mx1300, mx1310, mx1350

        ADDR    Start address

        SIZE    Read size

        IMAGE   Image file to store the read data

    Example:

        $ mdev flash read mx1300 0x20000 0x1000 app.bin
    """
    with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeRemainingColumn(),
            TransferSpeedColumn()) as bar:
        size = int(size, 0)
        bar.step = size / 100
        bar.read_task = bar.add_task("[green]Read", total=size)
        __mflash = mflash.Mflash(chip, update_read, context=bar)
        try:
            __mflash.read(image, int(addr, 0), size)
        except CalledProcessError as e:
            print(Panel.fit(f"[red]{e.cmd}", title="Failed", style='red'))


@click.command()
@click.argument("chip")
@click.argument("addr")
@click.argument("size")
def erase(chip: str, addr: int, size: int):
    """
    Erase flash

    Arguments:

        CHIP    Chip name, current support: rtl8762c, mx1270, mx1290, mx1300, mx1310, mx1350

        ADDR    Start address

        SIZE    Erase size

    Example:

        $ mdev flash erase mx1300 0x20000 0x1000
    """
    with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeRemainingColumn(),
            TransferSpeedColumn()) as bar:
        size = int(size, 0)
        bar.step = size / 100
        bar.erase_task = bar.add_task("[green]Erase", total=100, start=False)
        __mflash = mflash.Mflash(chip, None)
        try:
            __mflash.erase(int(addr, 0), size)
        except CalledProcessError as e:
            print(Panel.fit(f"[red]{e.cmd}", title="Failed", style='red'))
        bar.start_task(bar.erase_task)
        bar.update(bar.erase_task, completed=100)


@click.command()
@click.argument("chip")
def mac(chip: str):
    """
    Read MAC address

    Arguments:

        CHIP    Chip name, current support: rtl8762c, mx1270, mx1290, mx1300, mx1310, mx1350

    Example:

        $ mdev flash mac mx1300
    """
    __mflash = mflash.Mflash(chip, None)
    try:
        print(__mflash.mac())
    except CalledProcessError as e:
        print(Panel.fit(f"[red]{e.cmd}", title="Failed", style='red'))


flash.add_command(write)
flash.add_command(read)
flash.add_command(erase)
flash.add_command(mac)
