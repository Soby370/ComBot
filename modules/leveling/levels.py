from typing import List


class LevelRole:
    level = 0
    emoji = ""
    required = 0


class Novice(LevelRole):
    emoji = "🌟"
    required = 3
    name = "Novice"


class Chatter(LevelRole):
    name = "Chatter"
    required = 10
    emoji = "🤘"


class Scholar(LevelRole):
    emoji = "🎓"
    required = 50
    name = "Scholar"


class Communicator(LevelRole):
    emoji = "💬"
    required = 100
    name = "Communicator"


class Magician(LevelRole):
    emoji = "🪄"
    required = 250
    name = "Magician"


class WisdomKeeper(LevelRole):
    emoji = "🌠"
    required = 500
    name = "Wisdom Keeper"


class KnowledgeSeeker(LevelRole):
    emoji = "📚"
    required = 1000
    name = "Knowledge Seeker"


class Explorer(LevelRole):
    emoji = "🗺️"
    required = 2000
    name = "Explorer"


class ChatLegend(LevelRole):
    emoji = "📱"
    required = 5000
    name = "Chat legend"


class Conversationalist(LevelRole):
    emoji = "🔥"
    required = 7000
    name = "Conversationalist"


class CosmicOverlord(LevelRole):
    emoji = "🌌"
    required = 9000
    name = "Cosmic Overlord"


class Unicorn(LevelRole):
    emoji = "🦄"
    required = 15000
    name = "Unicorn"


class Wizard(LevelRole):
    emoji = "🧙‍♂️"
    required = 20000
    name = "Wizard"


class CaptainCrunch(LevelRole):
    emoji = "🚢"
    name = "Captain Crunch"
    required = 25000


class Superstar(LevelRole):
    emoji = "🤩"
    required = 30000
    name = "Superstar"


class MagicMaestro(LevelRole):
    emoji = "🎩"
    name = "Magic Maestro"
    required = 40000


class GalacticEnchanter(LevelRole):
    emoji = "🪐"
    name = "Galactic Enchanter"
    required = 50000


class PiratePlunderer(LevelRole):
    name = "Pirate Plunderer"
    emoji = "🏴‍☠️"
    required = 60000


orderLevels: List[LevelRole] = [
    Novice,
    Chatter,
    Scholar,
    Communicator,
    Magician,
    WisdomKeeper,
    KnowledgeSeeker,
    Explorer,
    ChatLegend,
    Conversationalist,
    CosmicOverlord,
    Unicorn,
    Wizard,
    CaptainCrunch,
    Superstar,
    MagicMaestro,
    GalacticEnchanter,
    PiratePlunderer,
]

for index, order in enumerate(orderLevels, start=1):
    order.level = index

ReverseLevels = orderLevels.copy()
ReverseLevels.reverse()
