# -*- coding: utf-8 -*-

import sys
import os
import re
from mac_builder import *

func_re = re.compile(r'(native|function)[ \t]+([a-zA-Z_][a-zA-Z0-9_]*)[ \t]+takes([\s\S]*?)returns')

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
    
def build_jass_mac(cj, bj):
    syntax = syntax_file()
    syntax.header('jass', 'actboy168', 'www.ydwe.net')
    syntax.Include('.\const.mac')
    
    syntax.block('create parser')
    jass = syntax.Set('jass', syntax.CreateParser())
    
    syntax.block('comment')
    rLineComment  = syntax.Set('rLineComment',  jass.CreateRegion(COLOR_COMMENT1, '+//+', '$',    True))
    rBlockComment = syntax.Set('rBlockComment', jass.CreateRegion(COLOR_COMMENT2, '+/*+', '+*/+', True))
    jass.AddRegion(rLineComment)
    jass.AddRegion(rBlockComment)
    iTodo = syntax.Set('iTodo', jass.CreateItem(COLOR_HIGHLIGHT2, r'\b(TODO|FIX)\b', False))
    rLineComment.AddItem(iTodo)
    rBlockComment.AddItem(iTodo)
    
    syntax.block('string')
    jass.AddRegion(jass.CreateStringRegion(COLOR_STRING1, '\'', '\\', False))
    jass.AddRegion(jass.CreateStringRegion(COLOR_STRING1, '""', '\\', False))
    
    syntax.block('function def')
    jass.AddItem(jass.CreateItem(COLOR_FUNCTION, r'\b(function)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+takes\s+', False))
    
    syntax.block('number')
    jass.AddItem(jass.CreateItem(COLOR_NUMBER, r'\b\d+\b', False))
    
    syntax.block('operators')
    jass.AddItem(jass.CreateItem(COLOR_OPERATOR, r'[\{\}\(\)\+\-\*\\=%&\^!~\|<>?\.;\[\]]', False))

    syntax.block('keywords')
    jass.AddWord(jass.CreateWord(COLOR_WORD3, 'globals endglobals library endlibrary struct endstruct scope endscope method endmethod interface endinterface function endfunction loop endloop if then else elseif endif exitwhen native takes returns return local call set true false null array extends type constant and or not requires needs uses initializer public private defaults operator debug', True))

    syntax.block('type')
    jass.AddItem(jass.CreateWord(COLOR_WORD2, 'hashtable integer real boolean string handle agent event player widget unit destructable item ability buff force group trigger triggercondition triggeraction timer location region rect boolexpr sound conditionfunc filterfunc unitpool itempool race alliancetype racepreference gamestate igamestate fgamestate playerstate playerscore playergameresult unitstate aidifficulty eventid gameevent playerevent playerunitevent unitevent limitop widgetevent dialogevent unittype gamespeed gamedifficulty gametype mapflag mapvisibility mapsetting mapdensity mapcontrol playerslotstate volumegroup camerafield camerasetup playercolor placement startlocprio raritycontrol blendmode texmapflags effect effecttype weathereffect terraindeformation fogstate fogmodifier dialog button quest questitem defeatcondition timerdialog leaderboard multiboard multiboarditem trackable gamecache version itemtype texttag attacktype damagetype weapontype soundtype lightning pathingtype image ubersplat nothing', True))

    syntax.block('common.j function')
    jass.AddItem(jass.CreateWord(COLOR_WORD4, cj, True))
    
    syntax.block('blizzard.j function')
    jass.AddItem(jass.CreateWord(COLOR_WORD1, bj, True))
    
    syntax.block('marco')
    jass.AddItem(jass.CreateItem(COLOR_MACRO, r'#\s*if\s+!?defined', False))
    jass.AddItem(jass.CreateItem(COLOR_MACRO, r'#\s*(if|pragma|else|elif|error|ifndef|define|endif|undef|ifdef)\b', False))
    jass.AddRegion(jass.CreateRegion(COLOR_COMMENT1, r'#\s*error\b', '$', True))
    iInclude1 = syntax.Set('iInclude1', jass.CreateItem(COLOR_MACRO, r'#\s*include\s*(<.*?>)', False))
    iInclude1.Capture(1, COLOR_STRING2)
    jass.AddItem(iInclude1)
    iInclude2 = syntax.Set('iInclude2', jass.CreateItem(COLOR_MACRO, r'#\s*include\s*(?="")', False))
    iInclude2.Capture(1, COLOR_STRING2)
    jass.AddItem(iInclude2)
    
    syntax.block('extra')
    syntax.Call(jass.FoldText(r'^\s*\b(globals|library|struct|scope|method|interface|function|if|loop|private\s+function|public\s+function|private\s+method|public\s+method|private\s+struct|public\s+struct)\b', True))
    syntax.Call(jass.UnfoldText(r'\b(endglobals|endlibrary|endfunction|endstruct|endscope|endmethod|endinterface|endif|endloop)\b', True))
    syntax.Call(jass.IndentText(r'^\s*(globals|library|struct|scope|method|interface|function|if|loop)', True))
    syntax.Call(jass.UnindentText(r'\b(endglobals|endlibrary|endfunction|endstruct|endscope|endmethod|endinterface|endif|endloop)$', True))
    syntax.Call(jass.SetPairs('[]()""""\'\''))
    syntax.Call(jass.CommentLine(r'//'))
    syntax.Call(jass.CommentBlock(r'/*', r'*/'))
    jass.AddSnippet('jass.snippet')
    jass.AddCallTip('jass.ecp', True, ' ', '(', ',', ')', True)

    return syntax.get()
    
def create_jass_mac(filename):
    create_directories(os.path.dirname(filename))
    cj = ''
    bj = ''
    for k, v in func.items():
        if 'common.j' == v['type']:
            cj += k + ' '
        elif 'blizzard.j' == v['type']:
            bj += k + ' '
    f = file(filename, 'w')
    f.write(build_jass_mac(cj[:-1], bj[:-1]))
    f.close()
    
if __name__ == '__main__':
    read_script('script/common.j')
    read_script('script/blizzard.j')
    read_ui()
    create_jass_ecp('jass_for_everedit/calltip/jass.ecp')
    create_jass_mac('jass_for_everedit/syntax/jass.mac')

