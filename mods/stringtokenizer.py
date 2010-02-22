#-*- coding:utf-8 -*-
''' look like java.util.StringTokenizer
Created on 2010-2-9
@author: 
'''
class StringTokenizer:
    def __init__(self, s, s1=None, flag=False):
        if s1 is None:s1 = " \t\n\r\f"

        self.delimiterCodePoints = []

        self.currentPosition = 0
        self.newPosition = -1
        self.delimsChanged = False
        self.str = s
        self.maxPosition = len(s)
        self.delimiters = s1
        self.retDelims = flag

    def __skipDelimiters(self, i):
        if self.delimiters == '':
            raise Exception('NullPointer')
        j = i
        while True:
            if self.retDelims or j >= self.maxPosition:
                break
            c = self.str[j]
            if c not in self.delimiters:
                break
            j += 1
            continue
        return j

    def __scanToken(self, i):
        j = i
        while True:
            if j >= self.maxPosition:
                break
            c = self.str[j]
            if c in self.delimiters:
                break
            j += 1
            continue

        if self.retDelims and i == j:
            c1 = self.str[j]
            if c1 in self.delimiters:
                j += 1
        return j

    def __isDelimiter(self, i):
        return i in self.delimiterCodePoints

    def hasMoreTokens(self):
        self.newPosition = self.__skipDelimiters(self.currentPosition)
        return self.newPosition < self.maxPosition

    def nextToken(self, s=None):
        if s is None:
            self.currentPosition = self.newPosition < 0 or self.__skipDelimiters(self.currentPosition) if self.delimsChanged else self.newPosition
            self.delimsChanged = False
            self.newPosition = -1
            if(self.currentPosition >= self.maxPosition):
                raise Exception('NoSuchElementException')
            else:
                i = self.currentPosition
                self.currentPosition = self.__scanToken(self.currentPosition)
                #print 'pos: %s %s' % (i, self.currentPosition)
                return self.str[i:self.currentPosition]
        else:
            self.delimiters = s
            self.delimsChanged = True
            self.setMaxDelimCodePoint()
            return self.nextToken()

    def hasMoreElements(self):
        return self.hasMoreTokens()

    def nextElement(self):
        return self.nextToken()

    def countTokens(self):
        i = 0
        j = self.currentPosition
        while True:
            if j >= self.maxPosition:
                break
            j = self.__skipDelimiters(j)
            if j >= self.maxPosition:
                break
            j = self.__scanToken(j)
            i += 1
        return i

if __name__ == '__main__':
    ss = StringTokenizer("asfd!@#$%^&*(){}{[]./<:\"asfasf as2534%^&*df asfd()asd{}", "!\"'@#$%^&*() (", True)
    while ss.hasMoreTokens():
        t = ss.nextToken()
        print t
    print 'end'
