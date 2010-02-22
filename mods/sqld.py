#-*- coding:utf-8 -*-
'''
Created on 2010-2-6

@author: from ec
'''
import re
import time
import locale

class Token:
    def __init__(self,a,b,c=None ):
        if c is None:
            self.startIndex = a
            self.endIndex = b
        else:
            self.style = a
            self.startIndex = b
            self.endIndex = c
    
    def isValid(self):
        return (self.startIndex != -1) or (self.endIndex != -1)

    def reset(self, style=None, startIndex=None, endIndex=None):
        if style is None:
            self.style = -1
            self.startIndex = -1
            self.endIndex = -1
        else:
            self.style = style
            self.startIndex = startIndex
            self.endIndex = endIndex

    def getLength(self):
        return self.endIndex - self.startIndex

    def intersects(self, startOffset,   endOffset):
        return ((self.startIndex <= self.startOffset) and (self.endIndex >= self.endOffset)) or \
               ((self.startIndex <= self.startOffset) and (self.endIndex <= self.endOffset)) or \
               ((self.startIndex >= self.startOffset) and (self.endIndex <= self.endOffset))

    def contains(self, startOffset=None,  endOffset=None):
        if endOffset is None:
            return self.contains(startOffset   , startOffset)
        else:
            return (self.startIndex <= startOffset) and (self.endIndex >= endOffset)
    
    def getStartIndex(self):
        return self.startIndex

    def setStartIndex(self, startIndex):
        self.startIndex = startIndex

    def getEndIndex(self):
        return self.endIndex

    def setEndIndex(self, endIndex):
        self.endIndex = endIndex

    def getStyle(self):
        return self.style

    def setStyle(self, style):
        self.style = style

    def equals(self, object):
        if issubclass(object.__class == self.__class):
            return object.getStartIndex() == self.startIndex and \
                   object.getEndIndex() == self.endIndex and \
                   object.getStyle() == self.style
        
        return False
    
    def __str__(self):
        sb = 'Token - style: %s startIndex: %s endIndex: %s' % (self.style,self.startIndex,self.endIndex)
        return sb

class QueryTypes:
    ALL_UPDATES = 80;
    # An SQL INSERT statement
    INSERT = 80;
    # An SQL UPDATE statement
    UPDATE = 81;
    # An SQL DELETE statement
    DELETE = 82;
    # An SQL SELECT statement

    SELECT = 10;
    # A DESCRIBE statement - table meta data
    DESCRIBE = 16;
    # An SQL EXPLAIN statement
    EXPLAIN = 15;
    # An SQL EXECUTE statement (procedure)
    EXECUTE = 11;
    # An SQL DROP TABLE statement
    DROP_TABLE = 20;
    # An SQL CREATE TABLE statement
    CREATE_TABLE = 21;
    # An SQL ALTER TABLE statement
    ALTER_TABLE = 22;
    # An SQL CREATE SEQUENCE statement
    CREATE_SEQUENCE = 23;
    # An SQL CREATE FUNCTION statement
    CREATE_FUNCTION = 26;
    # An SQL CREATE PROCEDURE statement
    CREATE_PROCEDURE = 25;
    # An SQL GRANT statement
    GRANT = 27;
    # An SQL GRANT statement
    CREATE_SYNONYM = 28;
    # An unknown SQL statement
    UNKNOWN = 99;
    # A commit statement
    COMMIT = 12;
    # A rollback statement
    ROLLBACK = 13;
    # A connect statement
    CONNECT = 14;
    
    
class TokenTypes:
    OPEN_COMMENT = "/*"
    CLOSE_COMMENT = "*/"
    SINGLE_LINE_COMMENT_STRING = "--"
    SINGLE_LINE_COMMENT_REGEX = "--.*$"

    QUOTE_REGEX = "\'((?>[^\']*+)(?>\'{2}[^\']*+)*+)\'|\'.*"
    NUMBER_REGEX = "\\b(([0-9]+)\\.?[0-9]*)\\b"
    BRACES_REGEX = "\\(|\\{|\\[|\\)|\\]|\\}"
    OPERATOR_REGEX ="(\\;|\\.|\\,|~|\\?|\\:|" + \
                    "\\+|\\-|\\&|\\||\\\\|\\!" + \
                    "|\\=|\\*|\\^|%|\\$|/|\\<|\\>)+"
    MATCHERS =[
        "keyword",
        "operator",
        "number",
        "literals",
        "braces",
        "string",
        "single-line-comment"
        ]
    KEYWORD_MATCH = 0
    OPERATOR_MATCH = 1
    NUMBER_MATCH = 2
    LITERALS_MATCH = 3
    BRACES_MATCH = 4
    SINGLE_LINE_COMMENT_MATCH = 6
    STRING_MATCH = 5
    UNRECOGNIZED = 0
    WORD = 1
    NUMBER = 2
    COMMENT = 3
    KEYWORD = 4
    KEYWORD2 = 5
    LITERAL = 6
    STRING = 7
    OPERATOR = 8
    BRACKET = 9
    SINGLE_LINE_COMMENT = 10
    BRACKET_HIGHLIGHT = 11
    BRACKET_HIGHLIGHT_ERR = 12

    typeNames =[
        "bad token",
        "normal",
        "number",
        "comment",
        "keyword",
        "keyword 2",
        "literal",
        "string",
        "operator",
        "bracket",
        "single line comment",
        "bracket highlight at cursor",
        "bracket highlight at cursor error"
        ]



class QueryTokenizer:
    def __init__(self, debug=False):
        #self.__QUOTE_REGEX= "'((?>[^']*+)(?>':2}[^']*+)*+)'|'.*"
        self.__QUOTE_REGEX = ''''(([^']*)('')*)*'|"(([^"]*)("")*)*"'''
        self.__QUOTE_REGEX1 = "'(([^']*)('')*)*'"
        #self.__MULTILINE_COMMENT_REGEX= "/\\*((?>[^\\*/]*+)*+)\\*/|/\\*.*"
        self.__MULTILINE_COMMENT_REGEX = "/\*.*?\*/"

        self.__stringTokens = []
        self.__stringMatcher = re.compile(self.__QUOTE_REGEX , 0)
        self.__stringMatcher1 = re.compile(self.__QUOTE_REGEX1 , 0)
        self.__singleLineCommentTokens = []
        self.__singleLineCommentMatcher = re.compile(TokenTypes.SINGLE_LINE_COMMENT_REGEX, re.M)
        self.__multiLineCommentTokens = []
        self.__multiLineCommentMatcher = re.compile(self.__MULTILINE_COMMENT_REGEX, re.M | re.DOTALL)
        self.debug = debug

    def tokenize(self, query, encodeto=locale.getdefaultlocale()[1], split_char = ";", beforepos=0):
        '''split sql statement
        @param query: 
        @param encodeto: 
        @param split_char: default ';'
        @param beforepos: 0
        @return: list []
        '''
        assert type(query) in [type(''), type(u'')]
        if self.debug:
            t11 = time.time()
        self.__extractQuotedStringTokens(query)
        if self.debug:
            t12 = time.time()
            print 'id:', id(self.__stringTokens), 'len:', len(self.__stringTokens)#, self.__stringTokens
            print "---time extractQuoteString:", t12 - t11
        self.__extractSingleLineCommentTokens(query)
        if self.debug:
            t13 = time.time()
            print 'id:', id(self.__singleLineCommentTokens), 'len:', len(self.__singleLineCommentTokens)#, self.__singleLineCommentTokens
            print '---time extractSingleLineComment:', t13 - t12
        self.__extractMultiLineCommentTokens(query)
        if self.debug:
            t14 = time.time()
            print 'id:', id(self.__multiLineCommentTokens), 'len:', len(self.__multiLineCommentTokens)#, self.__multiLineCommentTokens
            print '---time extractMultiLineComment:', t14 - t13

        sqlss = self.__deriveQueries(query, encodeto, split_char, beforepos)
        if self.debug:
            t15 = time.time()
            print 'id:', id(sqlss), 'len:', len(sqlss)
            print '------time split sqlss:', t15 - t14
        return sqlss

    def __extractQuotedStringTokens(self, query):
        for __i in range(len(self.__stringTokens)):
            self.__stringTokens.pop(0)
        fs = self.__stringMatcher.finditer(query, 0)
        try:
            while True:
                ne = fs.next()
                self.__stringTokens.append((TokenTypes.STRING, ne.start(), ne.end()))
        except StopIteration:
            pass

    def __extractSingleLineCommentTokens(self, query):
        self.__addTokensForMatcherWhenNotInString(self.__singleLineCommentMatcher, query, self.__singleLineCommentTokens)
 
    def __extractMultiLineCommentTokens(self, query):
        self.__addTokensForMatcherWhenNotInString(self.__multiLineCommentMatcher, query, self.__multiLineCommentTokens)

    def __addTokensForMatcherWhenNotInString(self, matcher, query, tokens):
        for __i in range(len(tokens)):
            tokens.pop(0)
        fs = matcher.finditer(query, 0)
        try:
            while True:
                ne = fs.next()
                start = ne.start()
                end = ne.end()
                endOffset = end
                if self.__isSingleLineMatcher(matcher):
                    endOffset = start + 2
                if (not self.__withinQuotedString(start, endOffset)):
                    tokens.append((TokenTypes.COMMENT, start, end))
        except StopIteration:
            pass
        
    def __deriveQueries(self, query, encodeto, split_char, beforepos):
        sqlss = []
        split_char_len = len(split_char)

        index = -split_char_len
        lastIndex = 0
        while True:
            index = query.find(split_char, index + split_char_len)
            if (index != -1):
                if (self.__notInAnyToken(index)):
                    sql = query[lastIndex:index]
                    if sql.strip():
                        u8strlen = len(sql)
                        try:
                            sql2 = sql.encode(encodeto)
                            lostrlen = (len(sql2)-u8strlen)*2 + u8strlen
                        except:
                            lostrlen = u8strlen
                        sqlss.append((sql.strip(), beforepos, beforepos+lostrlen+split_char_len))
                        beforepos += lostrlen+split_char_len
                    lastIndex = index + split_char_len
            else:
                sql = query[lastIndex:]
                if sql.strip():
                    u8strlen = len(sql)
                    try:
                        sql2 = sql.encode(encodeto)
                        lostrlen = (len(sql2)-u8strlen)*2 + u8strlen
                    except:
                        lostrlen = u8strlen
                    sqlss.append((sql.strip(), beforepos, beforepos+lostrlen+split_char_len))
                    beforepos += lostrlen+split_char_len
                break

        return sqlss

    def __notInAnyToken(self, index):
        return  not (self.__withinMultiLineComment(index, index)) \
            and not (self.__withinSingleLineComment(index, index)) \
            and not (self.__withinQuotedString(index, index))

    def __withinMultiLineComment(self, start, end):
        return self.__contains(self.__multiLineCommentTokens, start, end)

    def __withinSingleLineComment(self, start, end):
        return self.__contains(self.__singleLineCommentTokens, start, end)

    def __withinQuotedString(self, start, end):
        return self.__contains(self.__stringTokens, start, end)

    def __containso(self, tokens, start, end):
        for token in tokens:
            #if (token.contains(start, end)): 
            if token[1] <= start and token[2] >= end:
                print token,start,end
                return True
        return False

    def __contains(self, tokens, start, end):
        if len(tokens) == 0 or start < tokens[0][1] or end >= tokens[-1][2]:
            return False
        else:
            return self.__contains_2p(tokens, 0, len(tokens), start)

    def __contains_2p(self, tokens, begin, end, pos):
        stats = tokens[begin][1] <= pos < tokens[begin][2]
        #if self.debug:
        #    idd=id(tokens)
        #    if idd==id(self.__stringTokens):ids=" '****' "
        #    elif idd==id(self.__singleLineCommentTokens):ids=' --#### '
        #    else: ids=' /*==*/ '
        #    print '  %s : in <%s>[%d:%d]: %s \t%d \tcond:[%d] %s' % \
        #        (stats, ids, begin, end, tokens[begin], pos, \
        #         begin+int((end-begin)/2), tokens[begin+int((end-begin)/2)])
        if stats or end - begin <= 1:
            return stats
        else:
            mid = int((end - begin) / 2)
            if tokens[begin + mid][1] < pos:
                return self.__contains_2p(tokens, begin + mid, end, pos)
            else:
                return self.__contains_2p(tokens, begin + 1, end - mid, pos)

    def removeAllCommentsFromQuery(self, query):
        newQuery = self.removeMultiLineComments(query)
        return self.removeSingleLineComments(newQuery)

    def removeMultiLineComments(self, query):
        return self.__removeTokensForMatcherWhenNotInString(self.__multiLineCommentMatcher, query)

    def removeSingleLineComments(self, query):
        return self.__removeTokensForMatcherWhenNotInString(self.__singleLineCommentMatcher, query)

    def removeAllQuoteString(self, query, onlySingleQuote=False):
        '''remove singleQuote and/or doubleQuote substring on query
        @param query:
        @param onlySingleQuote: default False
        '''
        assert type(query) in [type(''), type(u'')]
        if onlySingleQuote: mat = self.__stringMatcher1
        else:               mat = self.__stringMatcher
        start = 0; end = 0
        sb = query
        try:
            while True:
                fs = mat.finditer(sb, 0)
                ne = fs.next(); start = ne.start(); end = ne.end()
                sb = sb[:start] + sb[end:]
        except StopIteration:
            pass
        return sb.strip()

    def __removeTokensForMatcherWhenNotInString(self, matcher, query):
        start = 0; end = 0; endOffset = 0
        sb = query
        fs = matcher.finditer(query, 0)
        try:
            while True:
                ne = fs.next(); start = ne.start(); end = ne.end()
                self.__extractQuotedStringTokens(sb)
                if (self.__isSingleLineMatcher(matcher)):
                    endOffset = start + 2
                else:
                    endOffset = end
                if (not self.__withinQuotedString(start, endOffset)):
                    sb = sb[:start] + sb[end:]
                    fs = matcher.finditer(sb, 0)
                else:
                    start = end
        except StopIteration:
            pass
        return sb.strip()

    def __isSingleLineMatcher(self, matcher):
        return (matcher == self.__singleLineCommentMatcher)

if __name__ == '__main__':
    az= QueryTokenizer()
    sql = """

select  'a ;'  --a;sf 
,msg,/*ad1;  --'a 'f*/
time
from te;
  --asdf
select  'a;ck' ,/*ad' asdf 'f*/  tabschema,/*2adf*/tabname 
 from syscat.tables;
select /*3adf*/ 'a;ng' ,procschema/* / a*adf*/,procname from

/*4adf*/
 syscat.procedures, syscat.procedures, 
   syscat.procedures, syscat.procedures;
aa ;
bb --a
"""

    tz = az.tokenize(sql)
    for i in tz:
        print '----------------\norigin SQL: [%s]' % i[0]
        print '----------------\ndevied SQL: [%s]' % az.removeAllCommentsFromQuery(i[0])
#        print i.getOriginalQuery()
#        print i.getDerivedQuery()

