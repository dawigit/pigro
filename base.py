class BaseUtil():
    def connect(self,cb,mode,args=None):
        self.cb = cb
        self.mode = mode
        self.args = args

    def connector(self,args,value,index):
        self.set(value)
