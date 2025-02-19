import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
# Copyright (C) 2017 Cuckoo Foundation.
# This file is part of Cuckoo Sandbox - http://www.cuckoosandbox.org
# See the file 'docs/LICENSE' for copying permission.

from cuckoo.common.abstracts import Processing
from cuckoo.core.extract import ExtractManager

class Extracted(Processing):
    key = "extracted"
    order = 3

    def run(self):
        return ExtractManager.for_task(self.task.id).results()
