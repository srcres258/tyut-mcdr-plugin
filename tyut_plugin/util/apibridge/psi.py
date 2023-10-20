
from mcdreforged.api.all import *

psi_instance: PluginServerInterface = None

def attach_psi_instance(ins: PluginServerInterface):
    global psi_instance
    psi_instance = ins
