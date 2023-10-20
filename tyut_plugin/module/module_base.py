
from mcdreforged.api.all import *
from abc import *

from tyut_plugin.api.util import *

class ModuleBase(ABC):
    def __init__(self, id: str, name: str = "", msg_tag: str = "", msg_tag_color: format.Color = format.Color.WHITE):
        self.id = id
        self.name = id if len(name) == 0 else name
        self.msg_tag = id if len(msg_tag) == 0 else msg_tag
        self.msg_tag_color = msg_tag_color

    def on_init(self):
        pass
    
    def on_load(self, server: PluginServerInterface):
        self.server = server

    def on_register_command(self, prefix_cmd: Literal):
        pass

    def on_unload(self, server: PluginServerInterface):
        pass

    def on_stop(self):
        pass

    def broadcast_module_message(self, msg: str):
        self.server.broadcast(generate_module_message(self, msg))

def get_module_message_header(module: ModuleBase) -> str:
    result = format.font_style_code[format.FontStyle.BOLD]
    result = format.color_code[module.msg_tag_color]
    result += '['
    result += module.msg_tag
    result += ']'
    result += format.reset_code
    return result

def generate_module_message(module: ModuleBase, msg: str) -> str:
    result = get_module_message_header(module)
    result += ' '
    result += msg
    return result
