#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(c) 2017 Nippon Telegraph and Telephone Corporation
# Filename: GlobalModule.py

EM_CONFIG = None
DB_CONTROL = None
EM_ORDER_CONTROL = None
NETCONFSSH = None
EM_REST_SERVER = None
EMSYSCOMUTILDB = None
EM_LOGGER = None

EM_CONF_PATH = None
EM_LIB_PATH = None

EM_SERVICE_LIST = None
EM_ORDER_LIST = None
EM_NAME_SPACES = None
EM_REST_SEND = None

SERVICE_SPINE = "spine"
SERVICE_LEAF = "leaf"
SERVICE_B_LEAF = "b-leaf"
SERVICE_L2_SLICE = "l2-slice"
SERVICE_L3_SLICE = "l3-slice"
SERVICE_CE_LAG = "ce-lag"
SERVICE_INTERNAL_LINK = "internal-link"
SERVICE_BREAKOUT = "breakout"
SERVICE_CLUSTER_LINK = "cluster-link"

ORDER_MERGE = "merge"
ORDER_DELETE = "delete"
ORDER_REPLACE = "replace"
ORDER_GET = "get"

TRA_STAT_PROC_RUN = 1           
TRA_STAT_EDIT_CONF = 2          
TRA_STAT_CONF_COMMIT = 3        
TRA_STAT_COMMIT = 4             
TRA_STAT_PROC_END = 5           
TRA_STAT_ROLL_BACK = 6          
TRA_STAT_ROLL_BACK_END = 7      
TRA_STAT_ROLL_BACK_ERR = 8      
TRA_STAT_PROC_ERR_CHECK = 9     
TRA_STAT_PROC_ERR_ORDER = 10    
TRA_STAT_PROC_ERR_MATCH = 11    
TRA_STAT_PROC_ERR_INF = 12      
TRA_STAT_PROC_ERR_TEMP = 13     
TRA_STAT_PROC_ERR_OTH = 14      

ORDER_RES_OK = 1                
ORDER_RES_ROLL_BACK_END = 2     
ORDER_RES_PROC_ERR_CHECK = 3    
ORDER_RES_PROC_ERR_ORDER = 4    
ORDER_RES_PROC_ERR_MATCH = 5    
ORDER_RES_PROC_ERR_INF = 6      
ORDER_RES_PROC_ERR_TEMP = 7     
ORDER_RES_PROC_ERR_OTH = 8      

COM_CONNECT_OK = 1              
COM_CONNECT_NG = 2              
COM_CONNECT_NO_RESPONSE = 3     

COM_UPDATE_OK = 1               
COM_UPDATE_VALICHECK_NG = 2     
COM_UPDATE_NG = 3               

COM_DELETE_OK = 1               
COM_DELETE_VALICHECK_NG = 2     
COM_DELETE_NG = 3               

COM_COMPARE_MATCH = 1           
COM_COMPARE_UNMATCH = 2         
COM_COMPARE_NO_INFO = 3         

COM_STOP_NORMAL = 0             
COM_STOP_CHGOVER = 2            
