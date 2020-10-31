#!/usr/bin/env python3
from enum import Flag, auto
from datetime import datetime
import re

S_CLOCK = "⏰"

class OpList(Flag):
    add = auto()
    sub = auto()
    mul = auto()
    div = auto()
    opp = auto()
    clp = auto()
    lt = auto()
    le = auto()
    eq = auto()
    ne = auto()
    ge = auto()
    gt = auto()

ops = {
        '(': OpList.opp,
        ')': OpList.clp,
        '*': OpList.mul,
        '/': OpList.div,
        '+': OpList.add,
        '-': OpList.sub,
        '<': OpList.lt,
        '>': OpList.gt,
        '=': OpList.eq,
        '!=': OpList.ne,
        '<=': OpList.le,
        '>=': OpList.ge,
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
            return self.value[index]
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


class Rule():
    def __init__(self,value,index=None):
        self.value = value
        self.index = index
    def __getitem__(self,index):
        return self.value[index]
    def __repr__(self):
        if type(self.value) is float:
            return str(self.value)
        elif type(self.value) is int:
            return str(self.value)
        else:
            return self.value
    def __eq__(self,other):
        if self.index is not None:
            v = self.value[self.index]
            return str(v) == other
            #return str(self.value,self.index) == other
        else:
            return str(self.value) == other

class Control():
    def __init__(self):
        self.rules = {}
        self.edittrule = None
        self.editname = None
        self.editbackup = None
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
        self.editbackup = self.rules[rulename]
        del self.rules[rulename]
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

    def rid(self,rulename):
        r = self.rules[rulename]
        if len(r) == 0:
            return
        if r.index('->') is not None:
            rs = r[:r.index('->')]
            cseq = r[r.index('->')+1:]
        s = ''
        for o in rs:
            if o.index is not None:
                s+=str(o.value[o.index])
            else:
                if hasattr(o.value,'get_selected_value'):
                    s+=str(o.value.get_selected_value())
                else:
                    st = str(o.value)
                    if st in ['and','or']:
                        s+=' '+st+' '
                    elif S_CLOCK in st:
                        tv = []
                        for sts in st[1:].split('-'):
                            if ':' in sts:
                                tv.append(int(sts.split(':')[0])*60+int(sts.split(':')[1]))
                            else:
                                tv.append(int(sts)*60)
                        t = datetime.now()
                        tnow = t.hour*60+t.minute
                        if len(tv) == 2:
                            if tv[1] < tv[0]:
                                tv[1]+=(24*60)
                            if tnow >= tv[0] and tnow <= tv[1]:
                                s+=' True '
                            else:
                                s+=' False '
                    else:
                        s+=st

        se = re.findall('\([^\(].+?\)',s)
        for sr in se:
            srr = ret(sr[1:-1])

            s = s.replace(sr,str(srr))
        cond = ret(s)


        if cond == True:
            target = None
            for c in cseq:
                if type(c.value) is str and target is not None:
                    if c == 'UP':
                        target.up()
                    elif c == 'DOWN':
                        target.down()
                    else:
                        cd = float(c.value)
                        cd = int(float(cd))
                        target.set(int(cd/10))
                else:
                    target = c.value

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
    for cc in (['AND','OR'],['<','>','=','<=','>=','!='],['*','/'],['-','+']):
        for c in cc:
            left, op, right = s.partition(c)
            #if left is None:
            #    return None
            #if right is None:
            #    return None
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
            elif op == 'AND':
                return ret(left) and ret(right)
            elif op == 'OR':
                return ret(left) or ret(right)
