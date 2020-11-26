
import sys
import time
import os
import xml.sax
import re
from collections import defaultdict
import math
import bisect
import nltk
from nltk.stem import *
from nltk.stem.snowball import SnowballStemmer
from nltk.tokenize import RegexpTokenizer
import pickle
from nltk.stem.porter import *
from nltk.stem import PorterStemmer as porter
from Stemmer import Stemmer
import operator
from math import log


stopwords=["a", "about", "above", "above", "across", "after", "afterwards", "again",
           "against", "all", "almost", "alone", "along", "already", "also","although",
           "always","am","among", "amongst", "amoungst", "amount",  "an", "and", "another",
           "any","anyhow","anyone","anything","anyway", "anywhere", "are", "around", "as",
           "at", "back","be","became", "because","become","becomes", "becoming", "been",
           "before", "beforehand", "behind", "being", "below", "beside", "besides",
           "between", "beyond", "bill", "both", "bottom","but", "by", "call", "can",
           "cannot", "cant", "co", "con", "could", "couldnt", "cry", "de", "describe",
           "detail", "do", "done", "down", "due", "during", "each", "eg", "eight", "either",
           "eleven","else", "elsewhere", "empty", "enough", "etc", "even", "ever", "every",
           "everyone", "everything", "everywhere", "except", "few", "fifteen", "fify", "fill",
           "find", "fire", "first", "five", "for", "former", "formerly", "forty", "found",
           "four", "from", "front", "full", "further", "get", "give", "go", "had", "has",
           "hasnt", "have", "he", "hence", "her", "here", "hereafter", "hereby", "herein",
           "hereupon", "hers", "herself", "him", "himself", "his", "how", "however", "hundred",
           "ie", "if", "in", "inc", "indeed", "interest", "into", "is", "it", "its", "itself",
           "keep", "last", "latter", "latterly", "least", "less", "ltd", "made", "many", "may",
           "me", "meanwhile", "might", "mill", "mine", "more", "moreover", "most", "mostly",
           "move", "much", "must", "my", "myself", "name", "namely", "neither", "never",
           "nevertheless", "next", "nine", "no", "nobody", "none", "noone", "nor", "not",
           "nothing", "now", "nowhere", "of", "off", "often", "on", "once", "one", "only",
           "onto", "or", "other", "others", "otherwise", "our", "ours", "ourselves", "out",
           "over", "own","part", "per", "perhaps", "please", "put", "rather", "re", "same",
           "see", "seem", "seemed", "seeming", "seems", "serious", "several", "she", "should",
           "show", "side", "since", "sincere", "six", "sixty", "so", "some", "somehow", "someone",
           "something", "sometime", "sometimes", "somewhere", "still", "such", "system", "take",
           "ten", "than", "that", "the", "their", "them", "themselves", "then", "thence", "there",
           "thereafter", "thereby", "therefore", "therein", "thereupon", "these", "they", "thickv",
           "thin", "third", "this", "those", "though", "three", "through", "throughout", "thru",
           "thus", "to", "together", "too", "top", "toward", "towards", "twelve", "twenty", "two",
           "un", "under", "until", "up", "upon", "us", "very", "via", "was", "we", "well", "were",
           "what", "whatever", "when", "whence", "whenever", "where", "whereafter", "whereas",
           "whereby", "wherein", "whereupon", "wherever", "whether", "which", "while", "whither",
           "who", "whoever", "whole", "whom", "whose", "why", "will", "with", "within", "without",
           "would", "yet", "you", "your", "yours", "yourself", "yourselves"
]



dbfile = open('titles/titleMap', 'rb')      
db = pickle.load(dbfile) 
dbfile.close()

stemmer = Stemmer('porter')


def tokenizeWords(data):
    # data = data.lower()
    tokenizer = RegexpTokenizer(r'[a-zA-Z0-9]+')
    return tokenizer.tokenize(data)

def cleanData(data):
  # Tokenisation -> lower -> stopWords -> stemming
  data = data.lower()
  data = tokenizeWords(data)
 
  words = []
  for token in data:
      token = (token)
      if len(token) <= 1 or token in stopwords:
          continue
      words.append(stemmer.stemWord(token))
  return words


class SearchEngine:
    
    def __init__(self):
        self.nonfieldQuery = 0
        self.tokensToSearch = []
        self.wordDocumentId = {}
        self.freq_of_word_in_Doc_id = {}
        self.SecondaryIndexlist = []
        self.getSeconaryIndexList()
        self.totalDocuments = len(db)
        self.wordIdDict = {}
        self.topK = None
        self.interSectionList_of_doc = []
        self.tfIDF = {}
        self.query_types = None
        self.query_values = None
        
    
    
    def createTokens(self,searchQuery):
        
        if ":" in  searchQuery:
            self.nonfieldQuery = 0
        else:
            self.nonfieldQuery = 1

        if self.nonfieldQuery == 1:
            self.tokensToSearch += cleanData(searchQuery)
        else:
            self.query_types,self.query_values = self.splitFieldQuery(searchQuery)
            
    
    
    
    def splitFieldQuery(self,search_query):
        query_tokens = search_query.split(":")
        query_types = []
        query_values = []
        i=0
        for token in query_tokens:
            if i == 0:
                query_types.append(token[0:1])
                i += 1
                continue
            if i == len(query_tokens)-1:
                query_values.append(token)
                i += 1
                continue
            query_types.append(token[token.rfind(" ")+1:len(token)][0:1])
            query_values.append(token[0:token.rfind(" ")])
            i+=1
        return query_types,query_values

    
    
    
    
    def getSeconaryIndexList(self):
        secondaryIndexPath = "index/" + "secondaryIndex.txt"
        secIdx = open(secondaryIndexPath,'r')
        for  word in secIdx:
            self.SecondaryIndexlist.append(word[:-1])
            
            
    
    def getPostingList(self,word):
        file_index = bisect.bisect(self.SecondaryIndexlist, word)
        if file_index > 0 :
            file_index -= 1
        filePath = "index/index_" + str(file_index) + ".txt"
        file     = open(filePath,'r')
        for line in file:
            if line[:line.find(":")] == word:
                return line[line.find(":")+1:-1]
        return
    
    def getFieldSpecific(self,postingList,field):
        docFreq = None
        if field == 'i':
            docFreq = re.findall(r'i[0-9]+',postingList)
        elif field == 'r':
            docFreq = re.findall(r'r[0-9]+',postingList)
        elif field == 'b':
            docFreq = re.findall(r'b[0-9]+',postingList)
        elif field == 'c':
            docFreq = re.findall(r'c[0-9]+',postingList)
        elif field == 't':
            docFreq = re.findall(r't[0-9]+',postingList)
        return docFreq
        
    
    def splitPostingList(self,postingList,field):
        docIdList = []
        docidFreq = {}
        postingList  = postingList.split(' ')
        for i in postingList:
            docId = re.findall(r'd[0-9]+',i)
            if(docId):
                docId = docId[0][1:]
                docFreq = self.getFieldSpecific(i,field)  #function for [i b g r t]
                if(docFreq):
                    docFreq = docFreq[0][1:]
                    docIdList.append(docId)
                    docidFreq[docId] =  docFreq
        return docIdList , docidFreq
        
            
        
        
    def getIntersection(self,wordDocumentId):
        result = None
        for key in wordDocumentId.keys():
            result=wordDocumentId[key]
            break
        for eachterm in wordDocumentId.keys():
            result = list(set(result).intersection(wordDocumentId[eachterm]))
        return result
    
    def getUnion(self,wordDocumentId):
        result = None
        for key in wordDocumentId.keys():
            result=wordDocumentId[key]
            break
        for eachterm in wordDocumentId.keys():
            result = list(set(result).union(wordDocumentId[eachterm]))
        return result
	

    
    def tfidfPreMethod(self,field):
        for word in self.tokensToSearch:
            postingList = self.getPostingList(word)
            if(postingList):
                self.wordDocumentId[word] , self.freq_of_word_in_Doc_id[word]  = self.splitPostingList(postingList,field)
                if (len(self.wordDocumentId[word]) > 0):
                    self.wordIdDict[word] = log(self.totalDocuments/len(self.wordDocumentId[word]))
        self.interSectionList_of_doc = self.getIntersection(self.wordDocumentId)
        
        if(len(self.interSectionList_of_doc)< self.topK):
            self.interSectionList_of_doc = self.getUnion(self.wordDocumentId)
	
     

    def calculateTfidfScoreforEachWord(self):
        if(len(self.interSectionList_of_doc)==0):
            return 
        for docId in self.interSectionList_of_doc:
            resultantScore = 0
            for word in self.freq_of_word_in_Doc_id:
                value = 0
                if docId in self.freq_of_word_in_Doc_id[word].keys():
                    frequency = self.freq_of_word_in_Doc_id[word][docId]
                    
                    if int(frequency) > 0 :
                        frequency = 1 + log(int(frequency))
                    else:
                        frequency = 0
                    
                    value = frequency * self.wordIdDict[word]
                
                resultantScore += value
        
            self.tfIDF[docId] = resultantScore
            
    def sortByScores(self,docScoreDict):
        temp = dict(sorted(docScoreDict.items(), key=operator.itemgetter(1),reverse=True))
        return list(temp.keys())
    
    def TopKdoc(self):
        sortedList = self.sortByScores(self.tfIDF)
        if len(sortedList) > self.topK:
            return sortedList[:self.topK]
        else:
            return sortedList
    
    def getTitles(self,docList):
        titles = []
        for docID in docList:
            titles.append(db[int(docID)])
        return titles


def writeInFile(result,fp):
    for i in result:
        titlename = db[int(i)]
        docId    = str(i)
        towrite =  docId + "," +titlename + '\n'
        fp.write(towrite)  



def getquery(line):
    line= line.split(',')
    k = line[0].strip()
    query = line[1].strip()
    return k , query



rf = open(sys.argv[1],'r')
fp = open("2019201058_queries_op.txt​",'w')
while True:
    line = rf.readline()
    if not line:
        break
    k , input_query_non_field = getquery(line)
    startTime = time.time()
    
    if ":" in input_query_non_field:
        se = SearchEngine()
        se.topK = int(k)
        query_types,query_values = se.splitFieldQuery(input_query_non_field)
        listForDifferentQuries = []
        for i in range(len(query_types)):
            object1 = SearchEngine()
            object1.topK = int(k)
            query = query_values[i]
            object1.createTokens(query)
            object1.tfidfPreMethod(query_types[i])
            object1.calculateTfidfScoreforEachWord()
            result = object1.TopKdoc()
            resultList = result
            if (len(resultList)>0):
                listForDifferentQuries.append(resultList)
            result = None	
            for listq in listForDifferentQuries:
                result = listq
                break
            for listq in listForDifferentQuries:
                result = list(set(result).intersection(listq))
            if(len(result) < object1.topK):
                result = None
                for listq in listForDifferentQuries:
                    result = listq
                    break
                for listq in listForDifferentQuries:
                    result = list(set(result).union(listq))
        if(len(result)>object1.topK):
            result = result[:object1.topK]
        writeInFile(result,fp)
        finalTime = time.time() - startTime
        averageTime = finalTime/int(k)
        timeToWrite = str(finalTime) +" " + str(averageTime) + '\n'
        fp.write(timeToWrite)
    else:
        se = SearchEngine() 
        se.topK = int(k)
        se.createTokens(input_query_non_field)
        se.tfidfPreMethod('b')
        se.calculateTfidfScoreforEachWord()
        result = se.TopKdoc()
        writeInFile(result,fp)
        finalTime = time.time() - startTime
        averageTime = finalTime/int(k)
        timeToWrite = str(finalTime) +" " + str(averageTime) + '\n'
        fp.write(timeToWrite)
    fp.write('\n')
fp.close()
rf.close()



