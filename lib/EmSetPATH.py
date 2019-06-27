#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: GlobalModule.py
'''
Set the PATH(PYTHONPATH) to be used for EM.
'''
import sys
import os


def get_pypath(dirname):
    for obj in os.listdir(dirname):
        tmp = os.path.join(dirname, obj)
        if os.path.isdir(tmp):
            sys.path.append(tmp)
            get_pypath(tmp)

cur_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(cur_dir)
get_pypath(cur_dir)
