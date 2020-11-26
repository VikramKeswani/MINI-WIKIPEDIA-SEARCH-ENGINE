				## WIKIPEDIA SEARCH ENGINE ##
The mini project involves building a search engine on the Wikipedia Data Dump without using any external index. For this project, we use the data dump of size ~73 GB. The search results return in real time. Multi-word and multi-field search on Wikipedia Corpus is implemented.

You also need to rank the documents and display only the top 10 most relevant documents.

Key challenge
To implement multi level data indexing to provide on demand search results(i.e in less than a sec) in memory through disk reads.

How things are done:
Etree is used to parse the XML Corpus without loading the entire corpus in memory. This helps parse the corpus with minimum memory. After parsing the following morphological operations are performed to obtain clean vocabulary.

Stemming : It is done using snowfall stemmer part of nltk library of python.

Casefolding : Casefolding is easily done through lower().

Tokenisation : Tokenisation is done using regular expressions.

Stop Word Removal: Stop words are removed by referring a stop word list that is maintained in a seperate file.

Term filter : This removes some of the common terms that are found in abundance in all the pages. These include terms like redirect,URL,png, HTTP etc.

NOTE One major optimization is done in stemming to reduce time of indexing is that, till 50000 document any repeatative word is not again stemmed,i.e we have used dynamic programming based approach here because stemming is time consuming and this has reduced indexing time to half.

As a part of Primary Inverted Index we have 4 files
. titlePosting :It contain docid and tf-idf of word part of document title with respect to a document.

. CategoryPosting :It contain docid and tf-idf of word part of category field with respect to a document.

. InfoBoxPosting :It contain docid and tf-idf of corresponding word part of infobox fild with respect to a document.

. textPosting: :It contain docid and tf-idf of corresponding word part of text,references and external links with respect to a document.

In order for O(1) access of title we have maintained another file that keep track of title corresponding to docId.

Secondary Index:

. WordPosition :It keep the track of posting list of word in title,infobox,text and category and allow as O(1) access to them and worked as a secondary index above field wise inverted index.

	  `XYX:{d:45454,t:45142,c:4587574,i:4545870}`
Ranking Factor While building index ranking of top 10 document corresponding to a word is done using td-idf and build a champion list and write into file.

Merging all temporary indexes using block based external merge sort algorithm We have made

Term Field Abbreviations For Search:
. Infobox abbreviated as infobox

. Body abbreviated as body

. Title abbreviated as title

. External Link abbreviated as ext

. References abbreviated as ref

. Category abbreviated as category

Query Format
. Field Query : title:abc body:xyz category:xxy infobox:dde ext:ref ref:ext

. Normal Query : word1 wor2 word3

How Searching in Less than a sec
. For normal query process word by word.For each word read its posting list from all 4 index file(if present in all four),this will be done in O(logn) where n is size of wordPosition dictionary and wrt to all different word queried final tf-idf is calculated for each document based on query and than top 10 documents are returned.If 2 word of query are part of same document than the tf-idf of the document is combination of tf-idf of document with respect to individual word.

. For field query instead of going through all 4 index file we will only look into the file corresponding to queried field and rest all process goes same as normal query.