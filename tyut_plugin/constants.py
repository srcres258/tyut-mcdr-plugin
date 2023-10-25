
from tyut_plugin.module.core.module import CoreModule
from tyut_plugin.module.server_notice.module import ServerNoticeModule
from tyut_plugin.module.time_announcement.module import TimeAnnouncementModule
from tyut_plugin.module.scheduled_restart.module import ScheduledRestartModule
from tyut_plugin.module.dustman.module import DustmanModule
from tyut_plugin.module.maintenance_notice.module import MaintenanceNoticeModule
from tyut_plugin.module.backup.module import BackupModule

PLUGIN_ID = 'tyut_plugin'
PLUGIN_VERSION = '0.1.6'
PLUGIN_COMMAND_PREFIX = '!!tyut'

MODULES = [CoreModule, TimeAnnouncementModule, MaintenanceNoticeModule, BackupModule]
