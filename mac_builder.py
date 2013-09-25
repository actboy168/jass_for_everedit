# -*- coding: utf-8 -*-

import types

class constant:
    def __init__(self, name):
        self.__name = name
        
    def __str__(self):
        return self.__name
         
COLOR_COMMENT1   = constant('COLOR_COMMENT1')
COLOR_DEFAULT    = constant('COLOR_DEFAULT')
COLOR_COMMENT1   = constant('COLOR_COMMENT1')
COLOR_COMMENT2   = constant('COLOR_COMMENT2')
COLOR_STRING1    = constant('COLOR_STRING1')
COLOR_STRING2    = constant('COLOR_STRING2')
COLOR_TAG        = constant('COLOR_TAG')
COLOR_MACRO      = constant('COLOR_MACRO')
COLOR_URL        = constant('COLOR_URL')
COLOR_EMAIL      = constant('COLOR_EMAIL')
COLOR_NUMBER     = constant('COLOR_NUMBER')
COLOR_FOUND      = constant('COLOR_FOUND')
COLOR_WORD1      = constant('COLOR_WORD1')
COLOR_WORD2      = constant('COLOR_WORD2')
COLOR_WORD3      = constant('COLOR_WORD3')
COLOR_WORD4      = constant('COLOR_WORD4')
COLOR_PAIR       = constant('COLOR_PAIR')
COLOR_FUNCTION   = constant('COLOR_FUNCTION')
COLOR_VAR        = constant('COLOR_VAR')
COLOR_SUBLAN     = constant('COLOR_SUBLAN')
COLOR_OPERATOR   = constant('COLOR_OPERATOR')
COLOR_HIGHLIGHT1 = constant('COLOR_HIGHLIGHT1')
COLOR_HIGHLIGHT2 = constant('COLOR_HIGHLIGHT2')
COLOR_HIGHLIGHT3 = constant('COLOR_HIGHLIGHT3')
COLOR_HIGHLIGHT4 = constant('COLOR_HIGHLIGHT4')
COLOR_HIGHLIGHT5 = constant('COLOR_HIGHLIGHT5')
COLOR_HIGHLIGHT6 = constant('COLOR_HIGHLIGHT6')
COLOR_HIGHLIGHT7 = constant('COLOR_HIGHLIGHT7')
COLOR_HIGHLIGHT8 = constant('COLOR_HIGHLIGHT8')
COLOR_IGNORE     = constant('COLOR_IGNORE')
COLOR_CONCEAL    = constant('COLOR_CONCEAL')

class cache():
    def __init__(self):
        self.__buffer = ''
        
    def write(self, value):
        self.__buffer += value
        
    def get(self):
        return self.__buffer
        
class variable_base():
    def __init__(self, name):
        self.__name   = name
        
    def get_name(self):
        return self.__name
        
    def get_args(self, args):
        ret = ''
        if len(args) > 0:
            if type(args[0]) is types.StringType:
                ret += '"' + args[0] + '"'
            else:
                ret += str(args[0])
            for v in args[1:]:
                if type(v) is types.StringType:
                    ret += ', "' + v + '"'
                else:
                    ret += ', ' + str(v)
        return ret
    
class variable_action(variable_base):
    def __init__(self, name):
        variable_base.__init__(self, name)
        
    def __call__(self, *args):
        ret = self.get_name()
        ret += '('
        ret += self.get_args(args)
        ret += ')'
        return constant(ret)
        
class variable_call(variable_base):
    def __init__(self, name, buffer):
        variable_base.__init__(self, name)
        self.__buffer = buffer
        
    def __call__(self, *args):
        ret = self.get_name()
        ret += '('
        ret += self.get_args(args)
        ret += ')\n'
        self.__buffer.write(ret)
        
class variable_call_v2(variable_base):
    def __init__(self, name, buffer):
        variable_base.__init__(self, name)
        self.__buffer = buffer
        
    def __call__(self, *args):
        ret = self.get_name()
        ret += ' '
        ret += self.get_args(args)
        ret += '\n'
        self.__buffer.write(ret)
        
class variable():
    variable_action_attr  = ['CreateRegion', 'CreateStringRegion', 'CreateItem', 'CreateWord', 'FoldText', 'UnfoldText', 'IndentText', 'UnindentText', 'SetPairs', 'CommentLine', 'CommentBlock']
    variable_call_attr    = ['AddRegion', 'AddItem', 'AddWord']
    variable_call_v2_attr = ['Capture', 'AddSnippet', 'AddCallTip']
    
    def __init__(self, name, buffer):
        self.__buffer = buffer
        self.__name   = name
        
    def write(self, value):
        self.__buffer.write(value)
        
    def __str__(self):
        return self.__name
        
    def __getattr__(self, attrname):
        if attrname in self.variable_action_attr:
            return variable_action(self.__name + '.' + attrname)
        elif attrname in self.variable_call_attr:
            return variable_call(self.__name + '.' + attrname, self.__buffer)
        elif attrname in self.variable_call_v2_attr:
            return variable_call_v2(self.__name + '.' + attrname, self.__buffer)
        else:
            raise AttributeError, attrname
        
class syntax_file():
    def __init__(self):
        self.buffer = cache()
        
    def get(self):
        return self.buffer.get()
        
    def write(self, value):
        self.buffer.write(value)
        
    def newline(self):
        self.write('\n')
        
    def comment(self, value):
        self.write('\'' + value + '\n')
        
    def block(self, name):
        self.newline()
        self.comment(name)
        
    def header(self, language, author, maintainer):
        self.comment('*******************************************************************************')
        self.comment(' EverEdit Syntax File')
        self.comment(' Language: '   + language)
        self.comment(' Author: '     + author)
        self.comment(' Maintainer: ' + maintainer)
        self.comment('*******************************************************************************')
        self.newline()
        
    def Include(self, value):
        self.write('Include("' + value + '")\n')
        
    def Set(self, var, value):
        self.write('Set ' + var + ' = ' + str(value) + '\n')
        return variable(var, self.buffer)
        
    def Call(self, value):
        self.write('Call ' + str(value) + '\n')
        
    def CreateParser(self):
        return 'CreateParser()'
        
def create_jass_mac(filename, value):
    import os
    try:
        os.makedirs(os.path.dirname(filename))
    except WindowsError:
        pass
    f = file(filename, 'w')
    f.write(value)
    f.close()
