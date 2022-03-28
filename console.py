#!/bin/python3

from cmd2 import Cmd, Cmd2ArgumentParser, with_argparser
from rich.console import Console
import json

#import plugin files here
import cmd2_plugins.clients_plugin
import cmd2_plugins.connections_plugin
import cmd2_plugins.generate_plugin
import cmd2_plugins.commands_plugin


class App(
        #We need to install the plugins here
        cmd2_plugins.clients_plugin.Plugin,
        cmd2_plugins.connections_plugin.Plugin, 
        cmd2_plugins.generate_plugin.Plugin,
        cmd2_plugins.commands_plugin.Plugin,
        Cmd):

    console = Console()
    intro = "Welcome to the listener interface\nConnect to C2 server to start\n"
    prompt = "(Disconnected): "
    connection = {
    "socket" : None,
    "address" : None,
    "port" : None
    }
    clients = {}

     
app = App()
app.cmdloop()
