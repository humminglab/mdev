# Author: Snow Yang
# Date  : 2022/03/21

import sys
import subprocess
import shutil
import random
import click
from pathlib import Path

from mdev.env import get_env, get_cmake, get_ninja
from mdev import log

from rich import print
from rich.panel import Panel


mxos_logo = '''
███╗   ███╗██╗  ██╗ ██████╗ ███████╗
████╗ ████║╚██╗██╔╝██╔═══██╗██╔════╝
██╔████╔██║ ╚███╔╝ ██║   ██║███████╗
██║╚██╔╝██║ ██╔██╗ ██║   ██║╚════██║
██║ ╚═╝ ██║██╔╝ ██╗╚██████╔╝███████║
╚═╝     ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝
'''

failed = '''
███████╗ █████╗ ██╗██╗     ███████╗██████╗ 
██╔════╝██╔══██╗██║██║     ██╔════╝██╔══██╗
█████╗  ███████║██║██║     █████╗  ██║  ██║
██╔══╝  ██╔══██║██║██║     ██╔══╝  ██║  ██║
██║     ██║  ██║██║███████╗███████╗██████╔╝
╚═╝     ╚═╝  ╚═╝╚═╝╚══════╝╚══════╝╚═════╝ 
'''

success = '''
███████╗██╗   ██╗ ██████╗ ██████╗███████╗███████╗███████╗
██╔════╝██║   ██║██╔════╝██╔════╝██╔════╝██╔════╝██╔════╝
███████╗██║   ██║██║     ██║     █████╗  ███████╗███████╗
╚════██║██║   ██║██║     ██║     ██╔══╝  ╚════██║╚════██║
███████║╚██████╔╝╚██████╗╚██████╗███████╗███████║███████║
╚══════╝ ╚═════╝  ╚═════╝ ╚═════╝╚══════╝╚══════╝╚══════╝
'''

fortune_txt = (
    '一个好的程序员是那种过单行线马路都要往两边看的人 - DougLinder',
    '程序有问题时不要担心,如果所有东西都没问题,你就失业了 - 软件工程的Mosher定律',
    '我想大部分人都知道通常一个程序员会具有的美德 当然了,有三种：懒惰,暴躁,傲慢 - Perl语言发明者LarryWall',
    '编程时要保持这种心态：就好象将来要维护你这些代码的人是一位残暴的精神病患者,而且他知道你住在哪 - MartinGolding',
    '一个人写的烂软件将会给另一个人带来一份全职工作 - JessicaGaston',
    '如果建筑工人像程序员写软件那样盖房子,那第一只飞来的啄木鸟就能毁掉人类文明 - GeraldWeinberg',
    '这世界最有可能毁灭的方式大多数专家都同意是次意外 这就是为什么会有我们,我们是计算机专家,我们创造意外 - NathanielBorenstein',
    '我们这个行业有个特别奇怪的现象：不仅我们不从失败里吸取教训,同时也不从成功中学习经验 - KeithBraithwaite',
    '一种新技术一旦开始流行,你要么坐上压路机,要么成为铺路石 - StewartBrand',
    '傻瓜都能写出计算机能理解的程序 优秀的程序员写出的是人类能读懂的代码 ',
    '任何你写的代码,超过6个月不去看它,当你再看时,都像是别人写的 - Eaglesonslaw',
    '软件就像做爱,一次犯错,你需要用余下一生来维护支持 - MichaelSinz',
    '在水上行走和按需求文档开发软件都很容易前提是它们都是冻结状态 - EdwardVBerard',
    '最初90%的代码用去了最初90%的开发时间;余下10%的代码用去了另外90%的开发时间 - TomCargill',
    '注释代码很像清洁你的厕所你不想干,但如果你做了,这绝对会给你和你的客人带来更愉悦的体验 - RyanCampbell',
    '如今的编程是一场程序员和上帝的竞赛,程序员要开发出更大更好、傻瓜都会用到软件 而上帝在努力创造出更大更傻的傻瓜 目前为止,上帝是赢的 - RickCook',
    '软件设计最困难的部分,是阻挡新功能的引入 - DonaldNorman',
    '为了理解递归,我们首先要理解的是递归 - Anonymous',
    '世上只有两类编程语言：那些拥有被人诟病的和那些没人用的 - BjarneStroustrup',
    '预备,开火,瞄准：这是最快的软件开发方法 预备,瞄准,瞄准,瞄准,瞄准：这是最慢的软件开发方法 - Anonymous',
    '编程是10%的科学,20%天份,和70%的让这天份符合科学 - Anonymous',
    '程序必须是为了给人看而写,给机器去执行只是附带任务 - Abelson/Sussman',
    '计算机善于遵循指令,但不善于理解你的思维 - DonaldKnuth',
    '没有文档等于白做 - 沈建华',
    '一个百思不得其解的奇怪问题一定是个很傻逼的问题 - 杨海波',
    '要有产品思维 - 徐炜',
    '代码千万条，注释第一条，命名不规范，同事两行泪 - SnowYang',
    '解决代码的编译警告有两个办法，一个是规范代码，另一个是关闭编译器警告 - SnowYang'
)


@click.command()
@click.argument("project", type=click.Path())
@click.argument("module")
@click.option(
    "--flash",
    "-f",
    type=click.Choice(["APP", "ALL", "None"], case_sensitive=False),
    help="Download firmware to flash after built.",
)
@click.option(
    "--clean",
    "-c",
    is_flag=True,
    help="Rebuild the project.",
)
@click.option(
    "--kconfig",
    "-k",
    is_flag=True,
    help="Open config menu",
)
@click.option(
    "--define",
    "-D",
    multiple=True,
    help="Define an cmake variable, this option can be provided multiple times",
)
def build(project: str, module: str, flash: str, clean: bool, kconfig: str, define: str) -> None:
    """
    Build a MXOS project.

    Arguments:

        PROJECT : Path to the MXOS project

        MODULE  : Module name

    Example:

        $ mdev build demos/helloworld emc3080
    """

    if not Path('.mdev').exists():
        print(Panel(f"[red]Error! We are not at a mdev project's root directory.", style='red'))
        return

    if clean and kconfig:
        print(Panel(f"[red]Error! Option '-c' and '-k' cannot coexist.", style='red'))
        return

    env_path = get_env()
    project = str(Path(project)).replace('\\', '/')
    build_diretory = f'build/{project}-{module}'

    print(Panel.fit(f"[cyan]{mxos_logo}",
          title="Thanks for using MXOS!", style='cyan'))

    if clean:
        log.dbg(f'Removing {build_diretory} ...')
        shutil.rmtree(build_diretory, ignore_errors=True)

    print(Panel(f"[magenta]Configuring ...", style='magenta'))
    command = f'{get_cmake()} -B {build_diretory} -GNinja -DAPP={project} -DMODULE={module} -DFLASH={flash} -DMXOS_ENV={env_path} -DCMAKE_MAKE_PROGRAM={get_ninja()}'
    if define:
        command += ' -D' + ' -D'.join(define)
    log.dbg(command)
    ret = subprocess.run(command, shell=True)
    if ret.returncode != 0:
        exit(ret.returncode)

    print(Panel(f"[green]Building ...", style='green'))
    command = f'{get_cmake()} --build {build_diretory}'
    if kconfig:
        command += f' --target guiconfig'
    log.dbg(command)
    ret = subprocess.run(command, shell=True)
    if ret.returncode != 0:
        print(Panel.fit(f"[red]{failed}", title="Sorry ...", style='red'))
        exit(ret.returncode)
    print(Panel.fit(f"[green]{success}",
          title="Congratulation!", style='green'))

    txt = fortune_txt[random.randint(0, len(fortune_txt)-1)]
    print(Panel(txt, style='cyan'))

@click.command()
def clean() -> None:
    """
    Remove the build directory.

    Example:

        $ mdev clean
    """

    if not Path('.mdev').exists():
        print(Panel(f"[red]Error! We are not at a mdev project's root directory.", style='red'))
        return

    shutil.rmtree('build', ignore_errors=True)