
from mcdreforged.api.all import *

from tyut_plugin.api.util import *

from tyut_plugin import constants
from tyut_plugin.module import module_manager
from tyut_plugin.util.apibridge import psi

def on_load(server: PluginServerInterface, prev_module):
    psi.attach_psi_instance(server)
    
    log.i("*-------------------------------------------------*")
    log.i("|                                                 |")
    log.i("| 欢迎使用太原理工大学 Minecraft 服务器 MCDR 插件 |")
    log.i("|                                                 |")
    log.i("*-------------------------------------------------*")

    module_manager.load_module_classes(constants.MODULES)
    module_manager.init_modules()
    module_manager.load_modules(server)
    module_manager.load_command_system(server)

def on_unload(server: PluginServerInterface):
    module_manager.unload_modules(server)
    module_manager.stop_modules()
