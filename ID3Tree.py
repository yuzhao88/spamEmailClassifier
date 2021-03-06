__author__ = 'Yu Zhao'

# use trainingMatrix.tolist() as traning vectors and y.tolist() as lables
import math
import operator
from random import randint
def calInformationCon(labels):
    labelCounts = {}
    totalCount = 0
    for i in labels:
        totalCount += 1
        if i in labelCounts:
            labelCounts[i] += 1
        else:
            labelCounts[i] = 1

    infoCont = 0.0
    for key in labelCounts:
        prob = float(labelCounts[key]) / totalCount
        infoCont += -1 * prob * math.log(prob, 2)
    return infoCont

def splitDataByFeaturePosAndFeatureFilter(dataSet, labels, featurePos, f):
    retDataSet = []
    retLabel = []
    i = 0
    for row in dataSet:
        if f(row[featurePos]):
            reduced = row[:featurePos]
            reduced.extend(row[featurePos + 1:])
            retDataSet.append(reduced)
            retLabel += [labels[i]]
        i += 1
    return retDataSet, retLabel

def chooseBestFeatureIndexToSplit(dataSet, labels, featureToConsiderIndexList):
    bestFeature = -1
    bestEntropy = -1
    for i in featureToConsiderIndexList:
        featureVals = [row[i] for row in dataSet]
        featureSet = set(featureVals)
        newEntropy = 0.0
        for featureVal in featureSet:
            splitData, splitLabels = splitDataByFeaturePosAndFeatureFilter(dataSet, labels, i, lambda x : x == featureVal)
            prob = float(len(splitData)) / len(dataSet)
            newEntropy += prob * calInformationCon(splitLabels)
            if newEntropy > bestEntropy:
                bestEntropy = newEntropy
                bestFeature = i
    return bestFeature

def bootstrapTrainingData(dataSet, labels, sampleSize):
    res = []
    resLabel = []
    for i in range(sampleSize):
        r =  randint(0, len(dataSet) - 1)
        res += [dataSet[r]]
        resLabel += [labels[r]]
    return res, resLabel

def sampleFeatureIndex(featureLen, size):
    res = []
    if featureLen == 1:
        for i in range(size):
            res += [0]
        return res
    featureIndexList = range(featureLen)
    for i in range(size):
        r = randint(0, len(featureIndexList) - 1)
        res += [featureIndexList[r]]
        del(featureIndexList[r])
    return res

def createTree(dataSet, labels, wordList, numFeatureToConsider):
    res = {}
    if labels.count(labels[0]) == len(labels):
        if labels[0] == 1:
            res[-1] = 1
        else:
            res[-1] = -1
        return res
    if len(dataSet[0]) == 1 or numFeatureToConsider == 0:  # only one feature left, return majority Count
        distinctElements = set(i[0] for i in dataSet)
        labelCount = {}
        for i in distinctElements:
            if i in labelCount:
                labelCount[i] += 1
            else:
                labelCount[i] = 1

        sortedByValue = sorted(labelCount.iteritems(), key = operator.itemgetter(1), reverse=True)
        if sortedByValue[0][0] == 1:
            res[-1] = 1
        else:
            res[-1] = -1
        return res

    else:
        featureListByIndex = sampleFeatureIndex(len(wordList), numFeatureToConsider)
        splitFeatureIndex = chooseBestFeatureIndexToSplit(dataSet, labels, featureListByIndex)
        id3Tree = {wordList[splitFeatureIndex]:{}}
        splitFeatureVals = set([ row[splitFeatureIndex] for row in dataSet])
        for i in splitFeatureVals:
            subData, subLabels = splitDataByFeaturePosAndFeatureFilter(dataSet, labels, splitFeatureIndex, lambda x: x == i)
            nextWordList = wordList[:splitFeatureIndex] + wordList[splitFeatureIndex+1:]
            id3Tree[wordList[splitFeatureIndex]][i] = createTree(subData, subLabels, nextWordList, numFeatureToConsider - 1)
        return id3Tree

def predict(emailVector, tree, wordList):
    if -1 in tree:
        return tree[-1]
    else:
        for splitWord in tree:
            wordIndex = wordList.index(splitWord)
            if emailVector[wordIndex] in tree[splitWord]:
                value = emailVector[wordIndex]
                return predict(emailVector, tree[splitWord][value], wordList)

def createForrest(dataSet, labels, numTrees, bootstrapSampleSize, numFeatures, wordList):
    trees = []
    for i in range(numTrees):
        bootstrapDataSet, bootStrapLabels = bootstrapTrainingData(dataSet, labels, bootstrapSampleSize)
        tree = createTree(bootstrapDataSet, bootStrapLabels, wordList, numFeatures)
        trees += [tree]
    return trees

def forrestPredict(emailVector, trees, wordList):
    res = []
    for tree in trees:
        res += [ predict(emailVector, tree, wordList)  ]
    countSpam = len(  [i for i in res if i == 1] )
    countNonSpam = len(res) - countSpam
    if countSpam > countNonSpam:
        return 1
    else:
        return -1

def dumpToFile(data, fileName):
    import pickle
    fw = open(fileName, 'w')
    pickle.dump(data, fw)
    fw.close()

def grabDataFromFile(fileName):
    import pickle
    fw = open(fileName)
    return pickle.load(fw)

def getPredictionAccuracyUsingTrees(trees, data, label, wordList):
    predictList = []
    for i in data:
        t = forrestPredict(i, trees, wordList)
        if t is None:
            predictList += [ '-9' ]
        else:
            predictList += [t ]
    pred = [label[i] == predictList[i] for i in range(len(predictList))]
    return float(sum(pred)) / len(pred)

def sklearnRandomForest():
    trainingDataSet = grabDataFromFile('trainingDataSet')
    trainingLabels = grabDataFromFile('trainingLabels')
    testDataSet = grabDataFromFile('testDataSet')
    testLabels = grabDataFromFile('testLabels')
    wordList = grabDataFromFile('wordList_145')

    from sklearn.ensemble import RandomForestClassifier


    trainPreds = []
    testPreds = []
    for numTree in range(1, 50, 2):
        clf = RandomForestClassifier(n_estimators=numTree,  n_jobs= 8, max_features=100)
        clf = clf.fit(trainingDataSet, trainingLabels)

        p = clf.predict(testDataSet)
        trainPred = [ p[i] == trainingLabels[i] for i in range(len(trainingDataSet)) ]
        trainPreds += [float(sum(trainPred)) / len(trainPred)]


        #print numTree, 'train', float(sum(trainPred)) / len(trainPred)

        p = clf.predict(testDataSet)
        testPred = [ p[i] == testLabels[i] for i in range(len(testDataSet)) ]

        testPreds += [float(sum(testPred)) / len(testPred)]
        #print numTree, 'test', float(sum(testPred)) / len(testPred)
    import matplotlib.pyplot as plt
    print len(range(1, 50, 2)), len(trainPreds), len(testPreds)
    plt.scatter(range(1, 50, 2), trainPreds, color = 'b')
    plt.scatter(range(1, 50, 2), testPreds, color = 'r')
    plt.show()



def main():
    trainingDataSet = grabDataFromFile('trainingDataSet')
    trainingLabels = grabDataFromFile('trainingLabels')
    testDataSet = grabDataFromFile('testDataSet')
    testLabels = grabDataFromFile('testLabels')
    wordList = grabDataFromFile('wordList_145')
    #
    # trees = createForrest(trainingDataSet, trainingLabels, numTrees=2, bootstrapSampleSize=500, numFeatures=80, wordList = wordList)

    trees = grabDataFromFile('forest_20_trees')

    trainingPred = getPredictionAccuracyUsingTrees(trees, trainingDataSet, trainingLabels, wordList)
    testPred = getPredictionAccuracyUsingTrees(trees, testDataSet, testLabels, wordList)
    print 'Training set accuracy: ', trainingPred
    print 'Test set accuracy: ', testPred

if __name__ == "__main__":
    sklearnRandomForest()