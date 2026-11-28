#!/usr/bin/env python3
"""This is now agents/@aibast-agents-library/templates/brainstem_deploy_agent.py.

The Brainstem target became an agent, so any AI runs it through the Brainstem's chat.
This file keeps the old command and the old import working.
"""
import importlib.util
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_FILE = os.path.join(_HERE, "..", "agents", "@aibast-agents-library", "templates", "brainstem_deploy_agent.py")
_spec = importlib.util.spec_from_file_location("brainstem_deploy_agent", _FILE)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
sys.modules[__name__] = _mod  # the old name is the same module, not a copy

if __name__ == "__main__":
    sys.exit(_mod.main())
