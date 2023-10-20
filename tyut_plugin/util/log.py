
from mcdreforged.api.all import *
import logging

from tyut_plugin.util.apibridge import psi

def log(level: int, msg, *args, **kwargs):
    psi.psi_instance.logger.log(level, msg, *args, **kwargs)

def debug(msg, *args, **kwargs):
    log(logging.DEBUG, msg, *args, **kwargs)

def info(msg, *args, **kwargs):
    log(logging.INFO, msg, *args, **kwargs)

def warn(msg, *args, **kwargs):
    log(logging.WARN, msg, *args, **kwargs)

def error(msg, *args, **kwargs):
    log(logging.ERROR, msg, *args, **kwargs)

def fatal(msg, *args, **kwargs):
    log(logging.FATAL, msg, *args, **kwargs)

d = debug
i = info
w = warn
e = error
f = fatal
