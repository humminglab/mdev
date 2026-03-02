import os
import sys
import collections
from time import sleep
from subprocess import Popen, run, CalledProcessError, PIPE, DEVNULL


class Mflash():
    def __init__(self, chip, progress, debugger='jlink_swd', context=None):
        self.progress = progress
        self.context = context
        hostos = 'osx' if sys.platform == 'darwin' else 'Linux64' if sys.platform == 'linux2' else 'win'
        cwd = os.path.join(os.path.dirname(os.path.abspath(__file__)))
        openocd = '%s/openocd/%s/openocd_mxos' % (cwd, hostos)
        self._cmd_hdr = ' '.join([
            openocd,
            '-s %s' % cwd,
            '-f interface/%s.cfg' % debugger,
            '-f targets/%s.cfg' % chip,
            '-f flashloader/scripts/flash.tcl',
            '-f flashloader/scripts/cmd.tcl',
            '-c "gdb_port disabled"',
            '-c "tcl_port disabled"',
            '-c "telnet_port disabled"',
            '-c init',
            '-c mflash_pre_init',
            '-c "mflash_init flashloader/ramcode/%s.elf"' % chip])

    def _construct_cmdline(self, cmds):
        cmds.append('shutdown')
        cmdline = ' '.join(
            [self._cmd_hdr, ' '.join('-c "%s"' % cmd for cmd in cmds)])
        return cmdline

    def _run(self, cmds, progress=True):
        cmdline = self._construct_cmdline(cmds)
        p = Popen(cmdline, shell=True, universal_newlines=True,
                  stdout=PIPE, stderr=DEVNULL)
        out = ''
        while True:
            o = p.stdout.readline().strip()
            if o:
                out += o
                if progress:
                    self.progress(o, self.context)
            if p.poll() != None:
                if p.poll():
                    raise CalledProcessError(1, cmdline, out, '')
                return out

    def justrun(self):
        cmdline = self._construct_cmdline([])
        run(cmdline, shell=True, check=True, stdout=DEVNULL, stderr=DEVNULL)

    def connect(self):
        while True:
            try:
                self.justrun()
                sleep(0.1)
                self.justrun()
                break
            except CalledProcessError:
                sleep(0.5)

    def disconnect(self):
        while True:
            try:
                self.justrun()
            except CalledProcessError:
                sleep(0.1)
                try:
                    self.justrun()
                except CalledProcessError:
                    break
            sleep(0.5)

    def mac(self):
        return self._run(['mflash_mac'], progress=False)

    def write(self, file, addr):
        self._run(['mflash_unlock', 'mflash_erase %s %d' % (
            addr, os.path.getsize(file)), 'mflash_write %s %s' % (file, addr)])

    def erase(self, addr, size):
        self._run(['mflash_unlock', 'mflash_erase %s %d' % (addr, size)], progress=False)

    def read(self, file, addr, size):
        self._run(['mflash_read %s %s %s' % (file, addr, size)])


if __name__ == '__main__':

    from rich.progress import *

    image = '/Users/snowyang/work/matter/xgateway/build/chip/demos/lighting-emc3180/lighting.bin'

    def update_write(out, bar):
        if '%' not in out:
            return
        if not bar.start:
            bar.start_task(bar.erase_task)
            bar.update(bar.erase_task, completed=100 * bar.step)
            bar.start = True
        pos = int(out[:-1], 0)
        bar.update(bar.write_task, completed=pos * bar.step)

    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeRemainingColumn(), 
        TransferSpeedColumn()) as bar:
        image_size = os.path.getsize(image)
        bar.step = image_size / 100
        bar.erase_task = bar.add_task("[green]Erase", total=image_size, start=False)
        bar.start = False
        bar.write_task = bar.add_task("[green]Write", total=image_size)
        __mflash = Mflash('mx1300', update_write, context=bar)
        __mflash.write(image, 0x20000)

