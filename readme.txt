How to run :
create a folder paste wiki_indexer.py and wiki_search.py

FOR INDEXING
RUN : python3 wiki_indexer.py [path location of folder where xml files present]
ex:  python3 wiki_indexer.py wiki/dump/


FOR Searching:
RUN : python3 wiki_search.py [path location of queries.txt]


format of queries.txt
3, t:World Cup i:2019 c:Cricket
value of k-> 3(top 3 documents)
query     -> 't:World Cup i:2019 c:Cricket'


OUTPUT:
queries_op.txt having result in format



Indeing:
parsing each xml file: 
    creating index files of 1 lakh words each 
after parsing , we get multiple file of 1 lakh words each, these files are sorted but they are not 
sorted with others
Applied merge sort for every 2 file 
After merging we get one huge file,huge file is difficult to open and close again,
so we split big file in chunk of 1000 each 
and for each staring word of file,
we make entry in secondary file (intutuion : to make search efficient)

splitted files will be present in './index/'
along with that I have created one pickle file for title which holds [pageNo -> title]


Searching:
use tfidf for ranking mechanism
take query
check whether query is fieldquery or not:
if not fieldquery:
tokenize(data) [lowercase->stemming->stopwords]
    for each word:
        get the posting list for each word
        get the documents where word is present
            get the frequency of that word in that document 
                    calculate tfidf for each docid
                        get the topk docid acc to their tfidf score
                            get the title for corresponding docid
else
    for each filed perform same operation :(change get the docid where word is present in that field)
    get the list for each field
    perform intersection of list and produce result
    if result less than topk documents 
    perform union

postingList Format:
coalici:d3666b3 d3973b1 d4955b1 
word 'coalici' occur in 3 documents with docID[3666,3973,4955]
occurence of 'coalici' in docID '3666' is 3



Further improvement :
    mutti-threading for each xml file 
    k-way parallel merge sort 