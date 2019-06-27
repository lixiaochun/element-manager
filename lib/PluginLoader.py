#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: PluginLoader.py
'''
Module for controlling plugin.
'''
import imp
import os
import GlobalModule


def load_module(module_name, basepath):
    '''
    Module is loaded and returned.
    '''
    f, n, d = imp.find_module(module_name, [basepath])
    return imp.load_module(module_name, f, n, d)


def load_plugins(basepath, plugin_top_name):
    '''
    Plugin is loaded and the list of Plugin is returned.
    '''
    plugin_list = []
    for fdn in os.listdir(basepath):
        try:
            fdn_full_path = os.path.join(basepath, fdn)
            if not fdn.startswith(plugin_top_name):
                continue
            if fdn.endswith(".py"):
                GlobalModule.EM_LOGGER.info(
                    '116001 Start Loading Plugin ("%s")', fdn)
                m = load_module(fdn.replace(".py", ""), basepath)
                plugin_list.append(m)
            elif os.path.isdir(fdn_full_path):
                m = load_plugins(fdn_full_path, plugin_top_name)
                plugin_list.extend(m)
        except ImportError as ex:
            GlobalModule.EM_LOGGER.error(
                '316002 Error Load Plugin ("%s")', fdn)
            GlobalModule.EM_LOGGER.debug("Import Error:%s", ex)
            raise
    return plugin_list
