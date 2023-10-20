
from mcdreforged.api.all import *

from tyut_plugin.api.module import *
from tyut_plugin.api.util import *

module_class_list: list[type[ModuleBase]] = []
module_list: dict[type[ModuleBase], ModuleBase] = {}

def load_module_classes(classes: list[type[ModuleBase]]):
    global module_class_list
    module_class_list = classes.copy()
    log.d("将要加载的模块:{0}".format(module_class_list))

def init_modules():
    for (i, module_class) in enumerate(module_class_list):
        log.d("正在初始化模块:{0}".format(module_class))
        module = module_class()
        module.on_init()
        module_list[module_class] = module
        log.d("模块初始化完毕:{0}".format(module_class))

def load_modules(server: PluginServerInterface):
    for (i, module) in enumerate(module_list.values()):
        log.i("正在加载模块:{0} {1}".format(module.id, module.name))
        module.on_load(server)
        log.i("模块加载完毕:{0} {1}".format(module.id, module.name))

def unload_modules(server: PluginServerInterface):
    for (i, module) in enumerate(module_list.values()):
        log.i("正在卸载模块:{0} {1}".format(module.id, module.name))
        module.on_unload(server)
        log.i("模块卸载完毕:{0} {1}".format(module.id, module.name))

def stop_modules():
    for (i, module) in enumerate(module_list.values()):
        log.d("正在停止模块:{0} {1}".format(module.id, module.name))
        module.on_stop()
        log.d("模块停止完毕:{0} {1}".format(module.id, module.name))
    module_list.clear()
    module_class_list.clear()

def get_module(t: type[ModuleBase]):
    return module_list[t]
