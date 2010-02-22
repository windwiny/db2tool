#-*- coding:utf-8 -*-
'''
Created on 2010-2-8
@author: 
'''
import re
import StringIO
import stringtokenizer

class SQLFormatter:
    def __init__(self, sql):
        assert type(sql) in [type(''), type(u'')]
        self.TOKEN_CHARS = "()+*/-=<>'`\"[],"
        self.WHITESPACE = " \n\r\f\t"
        self.BEGIN_CLAUSES = set()
        self.END_CLAUSES = set()
        self.LOGICAL = set()
        self.QUANTIFIERS = set()
        self.DML = set()
        self.MISC = set()
    
        self.BEGIN_CLAUSES.add("left")
        self.BEGIN_CLAUSES.add("right")
        self.BEGIN_CLAUSES.add("inner")
        self.BEGIN_CLAUSES.add("outer")
        self.BEGIN_CLAUSES.add("group")
        self.BEGIN_CLAUSES.add("order")

        self.END_CLAUSES.add("where")
        self.END_CLAUSES.add("set")
        self.END_CLAUSES.add("having")
        self.END_CLAUSES.add("join")
        self.END_CLAUSES.add("from")
        self.END_CLAUSES.add("by")
        self.END_CLAUSES.add("join")
        self.END_CLAUSES.add("into")
        self.END_CLAUSES.add("union")
        
        self.LOGICAL.add("and")
        self.LOGICAL.add("or")
        self.LOGICAL.add("when")
        self.LOGICAL.add("else")
        self.LOGICAL.add("end")
        
        self.QUANTIFIERS.add("in")
        self.QUANTIFIERS.add("all")
        self.QUANTIFIERS.add("exists")
        self.QUANTIFIERS.add("some")
        self.QUANTIFIERS.add("any")
        
        self.DML.add("insert")
        self.DML.add("update")
        self.DML.add("delete")
        
        self.MISC.add("select")
        self.MISC.add("on")
        #//MISC.add("values")
        
        self.indentString = "    "
        self.initial = "\n    "
    
        self.beginLine = True
        self.afterBeginBeforeEnd = False
        self.afterByOrSetOrFromOrSelect = False
        self.afterValues = False
        self.afterOn = False
        self.afterBetween = False
        self.afterInsert = False
    
        self.inFunction = 0
        self.parensSinceSelect = 0
    
        self.parenCounts = []
        self.afterByOrFromOrSelects = []
    
        self.indent = 1
    
        self.result = ''
        self.tokens= None
        self.lastToken=''
        self.token=''
        self.lcToken=''
        
        self.sql=''
        
        self.createTable=False
        self.alterTable=False
        self.commentOn=False
        
        self.sql = self.__removeBreaks(sql)
        self.recreateT = re.compile('^\s*CREATE\s+TABLE\s+',      re.I|re.M|re.DOTALL)
        self.recreateS = re.compile('^\s*CREATE\s+SUMMARY\s+',    re.I|re.M|re.DOTALL)
        self.recreateV = re.compile('^\s*CREATE\s+VIEW\s+',       re.I|re.M|re.DOTALL)
        self.recreateP = re.compile('^\s*CREATE\s+PROCEDURES\s+', re.I|re.M|re.DOTALL)
        self.recreateF = re.compile('^\s*CREATE\s+FUNCTION\s+',   re.I|re.M|re.DOTALL)
        self.realterT =  re.compile('^\s*ALTER\s+TABLE\s+',       re.I|re.M|re.DOTALL)
        self.recommentOn = re.compile('^\s*COMMENT\s+ON\s+',      re.I|re.M|re.DOTALL)

        if  self.recreateT.search(sql):
            self.createTable = True
            self.tokens = self.__createTableTokenizer()
        elif self.realterT.search(sql):
            self.alterTable = True
            self.tokens = self.__alterTableTokenizer()
        elif self.recommentOn.search(sql):
            self.commentOn = True
            self.tokens = self.__commentOnTokenizer()
        else:
            self.tokens = self.__statementTokenizer()         


    def __removeBreaks(self, text):
        self.tokens = stringtokenizer.StringTokenizer(text,"\n",True)
        sb = ''
        while self.tokens.hasMoreTokens():
            token = self.tokens.nextToken()
            if token == '\n':
                sb += token
            else:
                token = token.strip()
                if token:
                    sb += token
                    lastChar = token[-1]
                    if lastChar not in self.TOKEN_CHARS:
                        sb += ' '
        return sb
    
    def __createTableTokenizer(self):
        return stringtokenizer.StringTokenizer(self.sql, "(,)'[]\"\n\r", True)

    def __alterTableTokenizer(self):
        return stringtokenizer.StringTokenizer(self.sql, " (,)'[]\"\n\r", True)

    def __commentOnTokenizer(self):
        return stringtokenizer.StringTokenizer(self.sql, " '[]\"\n\r", True)

    def __statementTokenizer(self):
        return stringtokenizer.StringTokenizer(self.sql, self.TOKEN_CHARS+self.WHITESPACE, True)

    def setInitialString(self, initial):
        self.initial = initial;
        return self
    
    def setIndentString(self, indent):
        self.indentString = indent
        return self
    
    def format(self):
        try:
            formattedSql = ''
            if (self.createTable):
                formattedSql = self.__formatCreateTable();
            elif (self.alterTable):
                formattedSql = self.__formatAlterTable();
            elif (self.commentOn):
                formattedSql = self.__formatCommentOn();
            else:
                formattedSql = self.__formatStatement();
            #TODO:
            formattedSql = self.__removeFirstFourChars(formattedSql);
            return formattedSql.strip()
        except Exception as ee:
            print ee
            return self.sql
    
    #// hack for now...    
    def __removeFirstFourChars(self, formattedSql):
        beginIndex = 4
        fourChars = "    "
        self.result = ''
        self.tokens = stringtokenizer.StringTokenizer(formattedSql, '\n', True)
        while self.tokens.hasMoreTokens():
            token = self.tokens.nextToken()
            if (token.startswith(fourChars)):
                self.result += token[beginIndex:]
            else:
                self.result += token
        return self.result

    def __formatStatement(self):
        ##print '-------------',self.tokens.currentPosition,self.tokens.maxPosition
        self.result+=self.initial
#        q1=False
#        q2=False
#        t1=''
#        while(self.tokens.hasMoreTokens()):
#            token = self.tokens.nextToken()
#            self.lcToken = token.lower () 
#            if q1 or "'"==token:
#                t1 += token;
#                if q1 and "'"==token:
#                    q1=False #// cannot handle single quotes
#                if not q1:q1=True
#            elif q2 or "\"" ==token:
#                t1 += token
#                if q2 and "\""==token:
#                    q2=False #// cannot handle single quotes
#                if not q2:q2=True
#            if q1 or q2 :continue
#            if t1:
#                token = t1
#                t1=''
        while self.tokens.hasMoreTokens():
            self.token = self.tokens.nextToken()
            self.lcToken = self.token.lower ()
            #print '<<<%s>>>' % self.token
            if "'" == self.token:
                while self.tokens.hasMoreTokens():  # ??? while True: bug
                    t1 = self.tokens.nextToken()
                    self.token += t1
                    if "'" == t1: break
                else:self.__misc()
            elif "\"" == self.token:
                while self.tokens.hasMoreTokens():  # some up
                    t1 = self.tokens.nextToken()
                    self.token += t1
                    if "\"" == t1: break
                else:self.__misc()
            if self.afterByOrSetOrFromOrSelect and "," == self.token:
                self.__commaAfterByOrFromOrSelect()
            elif self.afterOn and "," == self.token:
                self.__commaAfterOn()
            elif "(" == self.token:
                self.__openParen()
            elif ")" == self.token:
                self.__closeParen()
            elif self.lcToken in self.BEGIN_CLAUSES:
                self.__beginNewClause()
            elif self.lcToken in self.END_CLAUSES:
                self.__endNewClause()
            elif "select" == self.lcToken:
                self.__select()
            elif self.lcToken in self.DML:
                self.__updateOrInsertOrDelete();
            elif "values" == self.lcToken:
                self.__values()
            elif "on" == self.lcToken:
                self.__on()
            elif self.afterBetween and self.lcToken == "and":
                self.__misc()
                self.afterBetween = False
            elif self.lcToken in self.LOGICAL:
                self.__logical()
            elif self.token == '\n':
                pass
            elif self.token in self.WHITESPACE:
                if self.result[-1] not in self.WHITESPACE:
                    self.__white()
            elif self.token == '-': # -- comment
                t=''
                if self.tokens.hasMoreTokens():
                    t = self.tokens.nextToken()
                    if t == '-':
                        while self.tokens.hasMoreTokens():
                            t1 = self.tokens.nextToken()
                            t += t1
                            if t1 in ['\n','\r','\r\n']:break
                self.token += t.rstrip()+'\n'
                self.__misc()
            elif self.token == '/': # /* */ comment
                t=''
                if self.tokens.hasMoreTokens():
                    t = self.tokens.nextToken()
                    if t == '*':
                        while self.tokens.hasMoreTokens():
                            t1 = self.tokens.nextToken()
                            t += t1
                            if t1 == '*':
                                if self.tokens.hasMoreTokens():
                                    t1 = self.tokens.nextToken()
                                    t += t1
                                    if t1 == '/':
                                        break
                self.token += t.rstrip()+'\n'
                self.__misc()
            else:
                self.__misc()

            if self.token not in self.WHITESPACE:
                self.lastToken = self.lcToken

        return self.result

    def __commaAfterOn(self):
        self.__out()
        self.indent -= 1
        self.__newline()
        self.afterOn = False
        self.afterByOrSetOrFromOrSelect = True

    def __commaAfterByOrFromOrSelect(self):
        self.__out()
        self.__newline()

    def __logical(self):
        if "end" == self.lcToken: self.indent -= 1
        self.__newline()
        self.__out()
        self.beginLine = False

    def __on(self):
        self.indent += 1
        self.afterOn = True
        self.__newline()
        self.__out()
        self.beginLine = False

    def __misc(self):
        #self.result += ' '
        self.__out();
        if "between" == self.lcToken:
            self.afterBetween = True
        if self.afterInsert:
            self.__newline()
            self.afterInsert = False
        else:
            self.beginLine = False
            if "case" == self.lcToken:
                self.indent += 1

    def __white(self):
        if not self.beginLine:
            self.result += " "
    
    def __updateOrInsertOrDelete(self):
        self.__out()
        self.indent += 1
        self.beginLine = False
        if "update" == self.lcToken: self.__newline()
        if "insert" == self.lcToken: self.afterInsert = True

    def __select(self):
        self.__out()
        self.indent += 1
        self.__newline()
        self.parenCounts.append(self.parensSinceSelect)
        self.afterByOrFromOrSelects.append(self.afterByOrSetOrFromOrSelect)
        self.parensSinceSelect = 0
        self.afterByOrSetOrFromOrSelect = True

    def __out(self):
        self.result += self.token

    def __endNewClause(self):
        if not self.afterBeginBeforeEnd:
            self.indent -= 1
            if  self.afterOn:
                self.indent -= 1
                self.afterOn = False
            if not self.afterInsert:
                self.__newline()
        self.__out();
        if "union" != self.lcToken: self.indent += 1
        self.__newline()
        self.afterBeginBeforeEnd = False
        self.afterByOrSetOrFromOrSelect = self.lcToken in ['by', 'set', 'from']

    def __beginNewClause(self):
        if not self.afterBeginBeforeEnd:
            if  self.afterOn:
                self.indent -= 1
                self.afterOn = False
            self.indent -= 1
            self.__newline()
        self.__out()
        self.beginLine = False
        self.afterBeginBeforeEnd = True

    def __values(self):
        self.indent -= 1
        self.__newline()
        self.__out()
        self.indent += 1
        self.__newline()
        self.afterValues = True

    def __closeParen(self):
        self.parensSinceSelect -= 1
        if self.parensSinceSelect < 0:
            self.indent -= 1
            self.parensSinceSelect = int(self.parenCounts.pop(len(self.parenCounts) - 1))
            self.afterByOrSetOrFromOrSelect = self.afterByOrFromOrSelects.pop(len(self.afterByOrFromOrSelects) - 1)
        if self.inFunction > 0 :
            self.inFunction -= 1
            self.__out()
        else:
            if not self.afterByOrSetOrFromOrSelect:
                self.indent -= 1
                self.__newline()
            self.__out();
        self.beginLine = False

    def __openParen(self):
        if (self.__isFunctionName(self.lastToken) or self.inFunction > 0):
            self.inFunction += 1
        self.beginLine = False
        if  self.inFunction > 0 :
            self.__out()
        else:
            self.__out()
            if not self.afterByOrSetOrFromOrSelect:
                self.indent += 1
                self.__newline()
                self.beginLine = True
        self.parensSinceSelect += 1

    def __isFunctionName(self, tok):
        begin = tok[0]
        isIdentifier = begin in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_"' # or '"'==begin;
        return isIdentifier and \
                tok not in self.LOGICAL and \
                tok not in self.END_CLAUSES and \
                tok not in self.QUANTIFIERS and \
                tok not in self.DML and \
                tok not in self.MISC

    def __isWhitespace(self, token):
        return token in self.WHITESPACE 
    
    def __newline(self):
        self.result += "\n"
        self.result += self.indentString * self.indent
        self.beginLine = True

#    /**
#     * Format an SQL statement using simple rules:
#     *  a) Insert newline after each comma;
#     *  b) Indent three spaces after each inserted newline;
#     * If the statement contains single/double quotes return unchanged,
#     * it is too complex and could be broken by simple formatting.
#     */
    def __formatCommentOn(self):
        result = "\n    "
        quoted = False
        while self.tokens.hasMoreTokens():
            token = self.tokens.nextToken()
            result += token
            if self.__isQuote(token):
                quoted = not quoted
            elif not quoted :
                if "is" == token :
                    result += "\n       "
        return result

    def __formatAlterTable(self):
        formattedSql = self.sql
        formattedSql = formattedSql.replace("\n", " ").replace("\r\n", " ").replace("\r", " ")
        return formattedSql;
        
#        /*
#        StringBuilder result = new StringBuilder(60).append("\n    ");
#
#        boolean quoted = false;
#        while (tokens.hasMoreTokens()):
#            String token = tokens.nextToken();
#            if (__isQuote(token)):
#                quoted = !quoted;
#            }
#            else if (!quoted):
#                if (isBreak(token)):
#                    result.append("\n        ");
#                }
#            }
#            result.append(token);
#        }
#        
#        return result.toString();
#        */

    def __formatCreateTable(self):
        indentOne = "\n    "
        indentTwo = "\n        "

        result = indentOne

        depth = 0
        quoted = False

        while self.tokens.hasMoreTokens():
            token = self.tokens.nextToken()
            if self.__isQuote(token) :
                quoted = not quoted
                result += token
            elif quoted :
                result += token
            else:
                if ")" == token:
                    depth -= 1
                    if depth == 0 :
                        result += indentOne
                if token.startswith(" ") and result[-1] in self.WHITESPACE:
                    token = token.strip()

                result += token
                if "," == token and depth == 1:
                    result += indentTwo

                if "(" == token:
                    depth += 1
                    if depth == 1 :
                        result += indentTwo

        return result

    def __lastCharAsString(self, sb):
        return sb[-1] 
    
#    /*
#    private boolean isBreak(String token):
#        return "drop".equals(token) ||
#            "add".equals(token) || 
#            "references".equals(token) || 
#            "foreign".equals(token) ||
#            "on".equals(token);
#    }
#    */

    def __isQuote(self, tok):
        return tok in r'''"`'[]'''

if __name__ =='__main__':        
        queries =[
                "select column1, column2 from table;",
                "CREATE TABLE public.candidate_request (candidate_request_id int8 NOT NULL, job int8, candidate int8, contact int8, job_application_details int8, message varchar(1000), status bpchar(3), datetime_created timestamptz DEFAULT now(), version_no int8 DEFAULT 1);",
                "insert into tableName (column1, column2) values ('1', '2', 'aa);",
                "update \" d\".\"astableName\" set column1 = 'value1', " + \
                "column2 = 'valueXX' where columnX='Y' and id in (select id from table2);"
                ]

        for query in queries :
            print
            print(SQLFormatter(query).format() )      

        print 'end.'




