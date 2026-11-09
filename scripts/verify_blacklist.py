#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
相容性進入點：轉向 check_controversy_reference.py
"""
import sys
from check_controversy_reference import audit, UNIFIED_FILE

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else UNIFIED_FILE
    audit(target)
