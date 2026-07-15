import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import logging
from data_platform.universe.universe_manager import UniverseManager
from data_platform.universe.universe_db import UniverseDB

logging.basicConfig(level=logging.INFO)
db = UniverseDB()
um = UniverseManager(db)
um.refresh_universe()
