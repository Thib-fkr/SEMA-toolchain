import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
# Copyright (C) 2014-2016 Cuckoo Foundation.
# This file is part of Cuckoo Sandbox - http://www.cuckoosandbox.org
# See the file 'docs/LICENSE' for copying permission.

import os

__all__ = ["blueprints"]
blueprints = []

for fname in os.listdir(os.path.dirname(__file__)):
    if fname.endswith(".py") and not fname.startswith("__init__"):
        view = __import__("cuckoo.distributed.views.%s" % fname.rstrip(".py"),
                          globals(), locals(), ["blueprint", "routes"], -1)
        blueprints.append((view.blueprint, view.routes))
