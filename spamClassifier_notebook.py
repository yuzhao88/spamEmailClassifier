
# coding: utf-8

# In[1]:

import os, sys
import math
import numpy as np
lib_path = os.path.abspath(os.path.join('D:\projects\spamEmailClassifier'))
sys.path.append(lib_path)
from Preprocesser import * 
from NaiveBayes import *


# In[2]:

trainingSetSpamFileList, testSetSpamFileList, trainingSetNonSpamFileList, testSetNonSpamFileList = getTrainingTestSet("D:\\projects\\spamEmailClassifier\\spamDataset", "D:\\projects\\spamEmailClassifier\\nonspamDataset")
trainingSpamTokenList, testSpamTokenList, trainingNonSpamTokenList, testNonSpamTokenList = getNormalizedEmailList(trainingSetSpamFileList, testSetSpamFileList, trainingSetNonSpamFileList, testSetNonSpamFileList)


# In[ ]:




# In[3]:

wordList, wordDistributionInSpam, wordDistributionInNonSpam, spamProbability =  getSpamWordList(trainingSpamTokenList,trainingNonSpamTokenList, 4, 9, 3, 99)
print len(wordList)


# ### Prediction 

# In[4]:

p,x,y = predict(trainingSpamTokenList, wordDistributionInSpam, wordDistributionInNonSpam, spamProbability)
s =  sum(p) / float(len(p))
print "training set spam: ", s
p,x,y = predict(trainingNonSpamTokenList, wordDistributionInSpam, wordDistributionInNonSpam, spamProbability)
ns =  1 - sum(p) / float(len(p))
print "training set non-spam: ", ns
print "training set overall: ", s * spamProbability + ns * (1 - spamProbability)

print ""
p,x,y = predict(testSpamTokenList, wordDistributionInSpam, wordDistributionInNonSpam, spamProbability)
s =  sum(p) / float(len(p))
print "test set spam: ", s
p,x,y = predict(testNonSpamTokenList, wordDistributionInSpam, wordDistributionInNonSpam, spamProbability)
ns =  1 - sum(p) / float(len(p))
print "test set non-spam: ", ns
print "test set overall: ", s * spamProbability + ns * (1 - spamProbability)


# In[5]:

myEmails = ["I like ml", "here is a good offer to make millions dollars from littel investment", "what are you doing"]
x = map(lambda x : getTokensFromStr(x), myEmails)
p,xs,yds = predict(x, wordDistributionInSpam, wordDistributionInNonSpam, spamProbability)
print p


# # Skkit-learn Naive Bayes

# In[15]:

from sklearn.feature_extraction.text import CountVectorizer
def readFileListAndNormalize(fileList):
    res = []
    for i in fileList:
        with open(i, 'r') as file :
            data=file.read()
            res = res + [data]
    return res


# In[39]:

trainingSpamEmails = readFileListAndNormalize(trainingSetSpamFileList)
testSpamEmails = readFileListAndNormalize(testSetSpamFileList)
trainingNonSpamEmails = readFileListAndNormalize(trainingSetNonSpamFileList)
testNonSpamEmails = readFileListAndNormalize(testSetNonSpamFileList)


# In[40]:

count_vect = CountVectorizer()


# In[62]:

X_train_counts = count_vect.fit_transform(trainingSpamEmails + trainingNonSpamEmails)


# In[63]:

print X_train_counts[0].shape


# In[64]:

from sklearn.feature_extraction.text import TfidfTransformer
tfidf_transformer = TfidfTransformer()
tf_transformer = TfidfTransformer(use_idf=False).fit(X_train_counts)
X_train_tfidf = tfidf_transformer.fit_transform(X_train_counts)


# In[65]:

target = map (lambda x : 1, trainingSpamEmails)
target += map(lambda x : 0, trainingNonSpamEmails)
print len(target), len(trainingSpamEmails) + len(trainingNonSpamEmails)


# In[77]:

from sklearn.naive_bayes import MultinomialNB
from sklearn.naive_bayes import BernoulliNB
clf = BernoulliNB().fit(X_train_tfidf, target)


# ### predict new emails

# In[78]:

X_train_spam_count =  count_vect.transform(trainingSpamEmails)
X_train_nonspam_count =  count_vect.transform(trainingNonSpamEmails)
X_train_spam_tfidf =  tfidf_transformer.transform(X_train_spam_count)
X_train_nonspam_tfidf =  tfidf_transformer.transform(X_train_nonspam_count)

X_test_spam_count =  count_vect.transform(testSpamEmails)
X_test_nonspam_count =  count_vect.transform(testNonSpamEmails)
X_test_spam_tfidf =  tfidf_transformer.transform(X_test_spam_count)
X_test_nonspam_tfidf =  tfidf_transformer.transform(X_test_nonspam_count)


# In[79]:

X_train_spam_predicted = clf.predict(X_train_spam_tfidf) 
print "training spam set: ", float(np.sum(X_train_spam_predicted)) / len(X_train_spam_predicted)

X_train_nonspam_predicted = clf.predict(X_train_nonspam_tfidf) 
print "training nonspam set: ", float(np.sum(X_train_nonspam_predicted)) / len(X_train_nonspam_predicted)


# In[80]:

X_test_spam_predicted = clf.predict(X_test_spam_tfidf) 
print "test spam set: ", float(np.sum(X_test_spam_predicted)) / len(X_test_spam_predicted)

X_test_nonspam_predicted = clf.predict(X_test_nonspam_tfidf) 
print "test nonspam set: ", float(np.sum(X_test_nonspam_predicted)) / len(X_test_nonspam_predicted)


# In[ ]:




# ### Instead of using tfidf, simply use my wordList