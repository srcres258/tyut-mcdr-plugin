
from mcdreforged.api.all import *

from tyut_plugin.api.module import *
from tyut_plugin.api.util import *

WELCOME_MESSAGE = \
"""§f-------------------------------------------
§e欢迎来到 §bTYUT 呆梨 Minecraft 服务器
§e官方QQ群：§c681874322
§e命令用法请输入 §a/help §e查阅
§7呆梨服插件 版本：v0.1.5  by src_resources
§9§nhttps://github.com/srcres258/tyut-mcdr-plugin§r
§f-------------------------------------------§r"""

def _on_player_joined(server: PluginServerInterface, player: str, info: Info):
    instance.server.tell(player, WELCOME_MESSAGE)
    instance.broadcast_module_message('§a[+]§r {}'.format(player))

def _on_player_left(server: PluginServerInterface, player: str):
    instance.broadcast_module_message('§c[-]§r {}'.format(player))

class CoreModule(ModuleBase):
    def __init__(self):
        super().__init__("core", name="核心", msg_tag="呆梨娘", msg_tag_color=format.Color.WHITE)

    def on_init(self):
        super().on_init()
        global instance
        instance = self

    def on_load(self, server: PluginServerInterface):
        super().on_load(server)
        server.register_event_listener('mcdr.player_joined', _on_player_joined)
        server.register_event_listener('mcdr.player_left', _on_player_left)

    def on_unload(self, server: PluginServerInterface):
        super().on_unload(server)

    def on_stop(self):
        super().on_stop()
        global instance
        instance = None

instance: CoreModule = None
