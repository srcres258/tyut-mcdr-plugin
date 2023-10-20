
import enum

class Color(enum.Enum):
    BLACK = 0
    DARK_BLUE = 1
    DARK_GREEN = 2
    DARK_AQUA = 3
    DARK_RED = 4
    DARK_PURPLE = 5
    GOLD = 6
    GARY = 7
    DARK_GARY = 8
    BLUE = 9
    GREEN = 10
    AQUA = 11
    RED = 12
    LIGHT_PURPLE = 13
    YELLOW = 14
    WHITE = 15
    MINECOIN_GOLD = 16
    MATERIAL_QUARTZ = 17
    MATERIAL_IRON = 18
    MATERIAL_NETHERITE = 19
    MATERIAL_REDSTONE = 20
    MATERIAL_COPPER = 21
    MATERIAL_GOLD = 22
    MATERIAL_EMERALD = 23
    MATERIAL_DIAMOND = 24
    MATERIAL_LAPIS = 25
    MATERIAL_AMETHYST = 26

class FontStyle(enum.Enum):
    RANDOM = 0
    BOLD = 1
    DELETE = 2
    UNDERLINE = 3
    ITALIC = 4
    RESET = 5

color_code = {
    Color.BLACK: '§0',
    Color.DARK_BLUE: '§1',
    Color.DARK_GREEN: '§2',
    Color.DARK_AQUA: '§3',
    Color.DARK_RED: '§4',
    Color.DARK_PURPLE: '§5',
    Color.GOLD: '§6',
    Color.GARY: '§7',
    Color.DARK_GARY: '§8',
    Color.BLUE: '§9',
    Color.GREEN: '§a',
    Color.AQUA: '§b',
    Color.RED: '§c',
    Color.LIGHT_PURPLE: '§d',
    Color.YELLOW: '§e',
    Color.WHITE: '§f',
    Color.MINECOIN_GOLD: '§g',
    Color.MATERIAL_QUARTZ: '§h',
    Color.MATERIAL_IRON: '§i',
    Color.MATERIAL_NETHERITE: '§j',
    Color.MATERIAL_REDSTONE: '§m',
    Color.MATERIAL_COPPER: '§n',
    Color.MATERIAL_GOLD: '§p',
    Color.MATERIAL_EMERALD: '§q',
    Color.MATERIAL_DIAMOND: '§s',
    Color.MATERIAL_LAPIS: '§t',
    Color.MATERIAL_AMETHYST: '§u'
}

font_style_code = {
    FontStyle.RANDOM: '§k',
    FontStyle.BOLD: '§l',
    FontStyle.DELETE: '§m',
    FontStyle.UNDERLINE: '§n',
    FontStyle.ITALIC: '§o',
    FontStyle.RESET: '§r'
}

reset_code = '§r'
