# -*- coding: iso-8859-1 -*-
import sys
__version__ = "6.0.0.dev3"
__all__ = ["simpleTAL", "simpleTALES", "simpleTALUtils"]
if sys.version_info.major == 2:
    __all__.append("simpleElementTree")
