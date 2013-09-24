# -*- coding: utf-8 -*-

import sys
import os
import re

func_re = re.compile(r'(native|function)[ ]+([a-zA-Z_][a-zA-Z0-9_]*)[ ]+takes([\s\S]*?)returns')

func = {}

def create_directories(p):
    try:
        os.makedirs(p)
    except WindowsError:
        pass
    
class ini_reader(dict):
    
    __id_re = re.compile(r"""
        \[(?P<ID>[A-Za-z_][A-Za-z0-9_]*)\]
        """, re.VERBOSE)
    __tag_re = re.compile(r"""
        (?P<TAG>[A-Za-z_][A-Za-z0-9_]*)=(?P<VALUE>.*)
        """, re.VERBOSE)
    
    def __init__(self, path):	
        try:
            fp = open(path, 'r')
            try:
                cur_ = None
                line = fp.readline()
                # UTF-8 BOM
                if len(line)>=3 and line[0] == '\xEF' and line[1] == '\xBB' and line[2] == '\xBF':
                    line = line[3:]
                while line:
                    m = self.__id_re.match(line)
                    if m:
                        if m.group('ID') not in self:
                            self[m.group('ID')] = {}
                        cur_ = self[m.group('ID')]
                    else:
                        m = self.__tag_re.match(line)
                        if m and (cur_ is not None) and (m.group('TAG') not in cur_):
                            cur_[m.group('TAG')] = m.group('VALUE')
                            
                    line = fp.readline()
            finally:
                fp.close()
        except IOError:
            pass
        
def read_script(filename):
    func_type = os.path.basename(filename)
    try:
        f = file(filename, 'r')
        try:
            for m in func_re.finditer(f.read()):
                param = m.group(3).strip()
                if param == 'nothing':
                    param = ''
                func[m.group(2)] = {'type':func_type, 'param':param}
        finally:
            f.close()
    except IOError:
        pass

def read_ui():
    ui_data   = ini_reader('ui/triggerdata.txt')
    ui_string = ini_reader('ui/triggerstrings.txt')
    we_string = ini_reader('ui/worldeditstrings.txt')['WorldEditStrings']
    
    ui_categories = {}
    for k, v in ui_data['TriggerCategories'].items():
        v = v[:v.find(',')]
        if v in we_string:
            v = we_string[v].strip('"')
        ui_categories[k] = v
        
    for k, v in func.items():
        k_cat = '_{0}_Category'.format(k)
        k_cat_val = None
        if k_cat in ui_data['TriggerEvents']:
            k_cat_val = ui_data['TriggerEvents'][k_cat]
        elif k_cat in ui_data['TriggerConditions']:
            k_cat_val = ui_data['TriggerConditions'][k_cat]
        elif k_cat in ui_data['TriggerActions']:
            k_cat_val = ui_data['TriggerActions'][k_cat]
        elif k_cat in ui_data['TriggerCalls']:
            k_cat_val = ui_data['TriggerCalls'][k_cat]
        if k_cat_val is not None and k_cat_val != 'TC_NOTHING':
            v['category'] = ui_categories[k_cat_val]
            
        k_val = None
        if k in ui_string['TriggerEventStrings']:
            k_val = ui_string['TriggerEventStrings'][k]
        elif k in ui_string['TriggerConditionStrings']:
            k_val = ui_string['TriggerConditionStrings'][k]
        elif k in ui_string['TriggerActionStrings']:
            k_val = ui_string['TriggerActionStrings'][k]
        elif k in ui_string['TriggerCallStrings']:
            k_val = ui_string['TriggerCallStrings'][k]   
        if k_val is not None:  
            v['comment'] = k_val.strip('"')

def create_jass_ecp(filename):
    create_directories(os.path.dirname(filename))
    
    f = file(filename, 'w')
    for k, v in func.items():
        if 'comment' in v:
            if 'category' in v:
                f.write('{0}({1})\\n{2} {3} - {4}\n'.format(k, v['param'], v['type'], v['category'], v['comment']))
            else:
                f.write('{0}({1})\\n{2} {3}\n'.format(k, v['param'], v['type'], v['comment']))
        else:
            f.write('{0}({1})\\n{2}\n'.format(k, v['param'], v['type']))
    f.close()

if __name__ == '__main__':
    read_script('script/common.j')
    read_script('script/blizzard.j')
    read_ui()
    create_jass_ecp('jass_for_everedit/calltip/jass.ecp')

