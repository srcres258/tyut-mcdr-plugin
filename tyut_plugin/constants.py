
from tyut_plugin.module.core.module import CoreModule
from tyut_plugin.module.server_notice.module import ServerNoticeModule
from tyut_plugin.module.time_announcement.module import TimeAnnouncementModule
from tyut_plugin.module.scheduled_restart.module import ScheduledRestartModule

PLUGIN_ID = 'tyut_plugin'
PLUGIN_VERSION = '0.1.0'

MODULES = [CoreModule, ServerNoticeModule, TimeAnnouncementModule, ScheduledRestartModule]
