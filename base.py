#!/usr/bin/env python3
from enum import Flag, auto

class OpList(Flag):
    add = auto()
    sub = auto()
    mul = auto()
    div = auto()
    openbr = auto()
    closebr = auto()
    lt = auto()
    le = auto()
    eq = auto()
    ne = auto()
    ge = auto()
    gt = auto()
    med = auto()
    sum = auto()

ops = {
        '<': OpList.lt,
        '>': OpList.gt,
        '=': OpList.eq,
        '!=': OpList.ne,
        '<=': OpList.le,
        '>=': OpList.ge,
        '+': OpList.add,
        '-': OpList.sub,
        '*': OpList.mul,
        '/': OpList.div,
        }


class ControlRule():
    def __init__(self,a,b,rule):
        #if type(a) is ControlRule:
        #    self.a = a.rid()
        #else:
        self.a = a
        #if type(b) is ControlRule:
        #    self.b = b.rid()
        #else:
        self.b = b
        self.rule = rule

    def op(self):
        if self.rule == OpList.add:
            return self.a+self.b
        if self.rule == OpList.sub:
            return self.a-self.b
        if self.rule == OpList.mul:
            return self.a*self.b
        if self.rule == OpList.div:
            return self.a/self.b
        if self.rule == OpList.lt:
            return self.a<self.b
        if self.rule == OpList.le:
            return self.a<=self.b
        if self.rule == OpList.eq:
            return self.a==self.b
        if self.rule == OpList.ne:
            return self.a!=self.b
        if self.rule == OpList.ge:
            return self.a>=self.b
        if self.rule == OpList.gt:
            return self.a>self.b
        if self.rule == OpList.med:
            s = 0
            for v in a:
                s+=v
            return s/b
        if self.rule == OpList.sum:
            s = 0
            for v in a:
                s+=v
            return s

class ControlObject():
    def __init__(self):
        self.value = None
    def __getitem__(self,index):
        if index is not None:
            return str(self.value[index])
        else:
            return self.value
    def __repr__(self):
        return self

    def __add__(self,other):
        if type(other) is ControlObject:
            return self.value + other.value
        else:
            return self.value + other
    def __sub__(self,other):
        if type(other) is ControlObject:
            return self.value - other.value
        else:
            return self.value - other
    def __mul__(self,other):
        if type(other) is ControlObject:
            return self.value * other.value
        else:
            return self.value * other
    def __truediv__(self,other):
        if type(other) is ControlObject:
            return self.value / other.value
        else:
            return self.value / other
    def __lt__(self,other):
        if type(other) is ControlObject:
            return self.value < other.value
        else:
            return self.value < other
    def __le__(self,other):
        if type(other) is ControlObject:
            return self.value <= other.value
        else:
            return self.value <= other
    def __eq__(self,other):
        if type(other) is ControlObject:
            return self.value == other.value
        else:
            return self.value == other
    def __ne__(self,other):
        if type(other) is ControlObject:
            return self.value != other.value
        else:
            return self.value != other
    def __ge__(self,other):
        if type(other) is ControlObject:
            return self.value >= other.value
        else:
            return self.value >= other
    def __gt__(self,other):
        if type(other) is ControlObject:
            return self.value > other.value
        else:
            return self.value > other


def ret(s):
    if type(s) is bool:
        return s
    s = str(s)
    if s.isdigit():
        return float(s)
    if '.' in s:
        nodot = s.replace('.','')
        if nodot.isdigit():
            return float(s)
    for cc in (['*','/'],['-','+'],['<','>','=','<=','>=','!=']):
        for c in cc:
            left, op, right = s.partition(c)
            if op == '*':
                return ret(left) * ret(right)
            elif op == '/':
                return ret(left) / ret(right)
            elif op == '+':
                return ret(left) + ret(right)
            elif op == '-':
                return ret(left) - ret(right)
            elif op == '<':
                return ret(left) < ret(right)
            elif op == '>':
                return ret(left) > ret(right)
            elif op == '<=':
                return ret(left) <= ret(right)
            elif op == '>=':
                return ret(left) >= ret(right)
            elif op == '=':
                return ret(left) == ret(right)
            elif op == '=!':
                return ret(left) != ret(right)

class Rule():
    def __init__(self,value,index=None):
        self.value = value
        self.index = index
    def __getitem__(self,index):
        return self.value[index]
    def __repr__(self):
        if type(self.value) is not str:
            r = self.value
            return str(r.value)
        r = self.value
        return str(r)
    def __eq__(self,other):
        if self.index is not None:
            return str(self.value[self.index]) == other
        else:
            return str(self.value) == other

class Control():
    def __init__(self):
        self.rules = {}
        self.edittrule = None
        self.editname = None
    def add_object(self,o,i=None):
        self.editrule.append(Rule(o,i))
    def del_last(self):
        if len(self.editrule):
            del self.editrule[-1]
    def new_rule(self,name):
        self.editrule = []
        self.editname = name
    def edit_rule(self,rulename):
        self.editrule = self.rules[rulename]
        self.editname  = rulename
    def add_rule(self):
        self.rules[self.editname] = self.editrule
    def del_rule(self,rulename):
        del(self.rules[rulename])
    def importrules(self,rules,map):
        i = 0
        for rule in rules:
            self.editname = 'RULE'+str(i)
            self.editrule = []
            rs = rule.split(' ')
            for r in rs:
                if r in list(map.keys()):
                    if '@' in r:
                        self.add_object(map[r],r.split('@')[1])
                    else:
                        self.add_object(map[r])
                else:
                    self.add_object(r)
            self.add_rule()
            i+=1
            #add importhelper (with maps of DEVICENAMES)
            # so import knows what is objects/values

    def rid(self,rulename):
        r = self.rules[rulename]
        if r.index('->') is not None:
            rs = r[:r.index('->')]
            cseq = r[r.index('->')+1:]
        s = ''
        for o in rs:
            if o.index is not None:
                s+=str(o.value[o.index])
            else:
                s+=str(o.value)
        cond = ret(s)
        if cond == True:
            target = None
            for c in cseq:
                if type(c.value) is str and target is not None:
                    if c == 'UP':
                        target.up()
                    if c == 'DOWN':
                        target.down()
                else:
                    target = c.value
