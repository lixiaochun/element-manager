#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(c) 2018 Nippon Telegraph and Telephone Corporation
# Filename: GlobalModule.py
'''
Set the PATH(PYTHONPATH) to be used for EM.
'''
import sys
import os

cur_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(cur_dir)
for obj in os.listdir(cur_dir):
    tmp = os.path.join(cur_dir, obj)
    if os.path.isdir(tmp):
        sys.path.append(tmp)
