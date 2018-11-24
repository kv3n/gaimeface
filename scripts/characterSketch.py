from __future__ import print_function
from watson_developer_cloud import NaturalLanguageUnderstandingV1
from watson_developer_cloud.natural_language_understanding_v1 import Features, EntitiesOptions, KeywordsOptions
from watson_developer_cloud.natural_language_understanding_v1 \
  import Features, EmotionOptions
from watson_developer_cloud import ToneAnalyzerV3

from stanfordcorenlp import StanfordCoreNLP
import logging
import json
import numpy as np
import ast
import glove
import math

from sklearn.feature_extraction.text import CountVectorizer
import argparse


from scipy.spatial.distance import cosine


# If service instance provides API key authentication
# service = NaturalLanguageUnderstandingV1(
#     version='2018-03-16',
#     ## url is optional, and defaults to the URL below. Use the correct URL for your region.
#     url='https://gateway.watsonplatform.net/natural-language-understanding/api',
#     iam_apikey='your_apikey')


cnt = 1

def sigmoid(x):
    result = (1 / (1 + math.exp(-x)))
    return result


def cosdist(word1, word2, vocab, vecs):
    cosdisRes = 0
    vec1 = []
    vec2 = []
    try:
        vec1 = vecs[vocab.index(word1)]
        vec2 = vecs[vocab.index(word2)]
    except:
        #print("no query: ", word1, " : ", word2)
        return 0.5
    cosdisRes = cosine(vec1[1].tolist(), vec2[1].tolist())
    return 1 - cosdisRes

def cosdist0(vec, word2, vocab, vecs):
    print(word2)
    cosdisRes = 0
    vec1 = vec
    vec2 = []
    try:
        vec2 = vecs[vocab.index(word2)]
    except:
        #print("no query: ",  word2)
        return 0.5
    #print("vec1: ", vec1)
    #print("vec2: ", vec2[1].tolist())
    cosdisRes = cosine(vec2[1].tolist(), vec1)
    return 1 - cosdisRes

def param2_generator(EventList, expList, ObjEntityList, EntityList, unsortedRelationList, vocab, vecs):

    """
    idx = 0
    freq = 1
    totalEmotion = 0

    #ObjEntityList is not sorted
    for i in ObjEntityList:
        if 'footbal' in i["strr"] or 'quaterback' in i["strr"]:
            totalEmotion = totalEmotion + i['joy'] + i['fear'] + i['anger'] + i['sadness'] + i['disgust']
            freq = freq + 5 * i['freq']
            if 'fan' in i['strr']:
                totalEmotion = totalEmotion + i['joy'] + i['fear'] + i['anger'] + i['sadness'] + i['disgust']
                freq = freq + 5 * i['freq']
            rel = RelationList[idx]
            if 'play' in rel['strr'] or 'cheer' in rel['strr']:
                totalEmotion = totalEmotion + rel['joy'] + rel['fear'] + rel['anger'] + rel['sadness'] + rel['disgust']
                freq = freq + 5 * rel['freq']
        idx = idx + 1
    param2 = totalEmotion / freq

    return
    """
    print("Relations: ", unsortedRelationList)
    entityExpVect = expList[0]
    relationExpVect = expList[1]
    decorationExpVect = expList[2]

    frequency = 0
    val = 0

    for r in unsortedRelationList:
        subidx = r["subidx"]
        eveidx = r["eveIdx"]
        #print("eveid: ", eveidx)
        #print("subid: ", subidx)
        this_Event = EventList[eveidx]
        this_subEvent = this_Event.subEvents[subidx]

        tokens = this_subEvent.PreprocessedTokenList
        #print("tokens: ", tokens)
        factorCount = 0

        isSatisfyingRel = False
        isSatisfyingEnt = False
        isSatisfyingDec = False

        for to in tokens:
            distRvMax = 0
            distEvMax = 0
            distDecMax = 0
            for rv in relationExpVect:
                distRv = cosdist0(rv, to["ctx"], vocab, vecs)
                if distRv > 0.7:
                    if distRvMax < distRv:
                        distRvMax = distRv
                        isSatisfyingRel = True
                        #print("related token: ", to["ctx"])
            for ev in entityExpVect:
                distEv = cosdist0(ev, to["ctx"], vocab, vecs)
                if distEv > 0.7:
                    if distEvMax < distEv:
                        distEvMax = distEv
                        isSatisfyingEnt = True
                        #print("related token: ", to["ctx"])
            for dv in decorationExpVect:
                distDec = cosdist0(dv, to["ctx"], vocab, vecs)
                if distDec > 0.7:
                    if distDecMax < distDec:
                        distDecMax = distDec
                        isSatisfyingDec = True
                        #print("related token: ", to["ctx"])
        if isSatisfyingEnt and isSatisfyingRel:
            frequency = frequency + 1
            val = val + (distRvMax + distEvMax)
            factorCount = factorCount + 1
            if isSatisfyingDec:
                factorCount = factorCount + 2

    if frequency == 0:
        frequency = 1
    val = val/(2*frequency)

    amplifyingFactor = 1.2
    val = val*pow(amplifyingFactor, factorCount)
    val = sigmoid(val - 0.5)

    return val

def most_similar(word, vocab, vecs, topn=10):
    query = []
    try:
        query = vecs[vocab.index(word)]
    except:
        return
    #query = vecs[word]

    result = []
    #print(type(vecs[535][1]))

    #print("idx!: ", vocab.index(word))

    for idx, vec in enumerate(vecs):
        if idx is not vocab.index(word):
            result.append((vocab[idx], 1 - cosine(query[1].tolist(), vec[1].tolist())))
    result = sorted(result, key=lambda x: x[1], reverse=True)
    return result[:topn]


class StanfordNLP:
    def __init__(self, host='http://localhost', port=9000):
        self.nlp = StanfordCoreNLP(host, port=port,
                                   timeout=30000)  # , quiet=False, logging_level=logging.DEBUG)
        self.props = {
            'annotators': 'tokenize,ssplit,pos,lemma,ner,parse,depparse,dcoref,relation',
            'pipelineLanguage': 'en',
            'outputFormat': 'json'
        }

    def word_tokenize(self, sentence):
        return self.nlp.word_tokenize(sentence)

    def pos(self, sentence):
        return self.nlp.pos_tag(sentence)

    def ner(self, sentence):
        return self.nlp.ner(sentence)

    def parse(self, sentence):
        print(sentence)
        return self.nlp.parse(sentence)

    def dependency_parse(self, sentence):
        return self.nlp.dependency_parse(sentence)

    def coref(self, sentence):
        props = {'annotators': 'coref', 'pipelineLanguage': 'en'}
        return self.nlp.annotate(sentence, properties=props)

    def annotate(self, sentence):
        return json.loads(self.nlp.annotate(sentence, properties=self.props))

    def OpenIE(self, sentence):
        props = {'annotators': 'openie', 'pipelineLanguage': 'en'}
        strr = self.nlp.annotate(sentence, properties=props)
        return json.loads(strr)

    def giveSentences(self, sentence):
        #props = {'pipelineLanguage': 'en', 'outputFormat': 'xml'}
        res = json.loads(self.nlp.annotate(sentence, properties=self.props))
        #print(type(res))
        #print(res["sentences"])

        l = []
        l2 = []
        for s in res["sentences"]:
            l.append(" ".join([t["word"] for t in s["tokens"]]))
            l2.append(s["parse"])
        return [l, l2]


    @staticmethod
    def tokens_to_dict(_tokens):
        tokens = defaultdict(dict)
        for token in _tokens:
            tokens[int(token['index'])] = {
                'word': token['word'],
                'lemma': token['lemma'],
                'pos': token['pos'],
                'ner': token['ner']
            }
        return tokens

    def wordsToSentenceAnnotator(self, tokens):
        return json.loads(self.nlp)

"""
def wrbExtraction(sentence):

    dep = sentence.depParse[:]
    TokenTemp = sentence.PreprocessedTokenList[:]
    wrbDict = []
    #aclList = [[-1] * len(TokenTemp) for i in range(len(TokenTemp))]
    wrbList = [[]] * len(TokenTemp)

    for k in dep:
        e = {}
        e["type"] = k[0]
        e["gov"] = k[1] - 1
        e["dep"] = k[2] - 1
        #e["idx"] = cnt #if the id is less than 0, means it is not related with acl clauses
        #e["parenIdx"] = -1
        wrbDict.append(e)
        if 'advcl' in e["type"]:
            wrbList[(e["dep"])].append(e["dep"])  #advcl dependent (starting points)

    #the goal must be building the full acllist
    for i in wrbDict:
        if wrbList[i["dep"]] != []:
            #need more exclusion conditions
            #Stack.append(i)
            DFS_Traversal_Wrb(i["dep"], i, wrbDict, wrbList)
    sentence.wrbList = wrbList
    return


def aclExtraction(sentence):

    dep = sentence.depParse[:]
    TokenTemp = sentence.PreprocessedTokenList[:]
    aclDict = []
    #aclList = [[-1] * len(TokenTemp) for i in range(len(TokenTemp))]
    aclList = [[]] * len(TokenTemp)

    for k in dep:
        e = {}
        e["type"] = k[0]
        e["gov"] = k[1] - 1
        e["dep"] = k[2] - 1
        #e["idx"] = cnt #if the id is less than 0, means it is not related with acl clauses
        #e["parenIdx"] = -1
        aclDict.append(e)
        if 'acl' in e["type"]:
            aclList[(e["gov"])].append(e["gov"])  #Nouns with acl

    #the goal must be building the full acllist
    for i in aclDict:
        if aclList[i["gov"]] != []:
            #need more exclusion conditions
            #Stack.append(i)
            DFS_Traversal_Acl(i["gov"], i, aclDict, aclList)
    sentence.aclList = aclList
    return

def ccompExtraction(sentence):

    dep = sentence.depParse[:]
    TokenTemp = sentence.PreprocessedTokenList[:]
    ccompDict = []
    #aclList = [[-1] * len(TokenTemp) for i in range(len(TokenTemp))]
    ccompList = [[]] * len(TokenTemp)

    for k in dep:
        e = {}
        e["type"] = k[0]
        e["gov"] = k[1] - 1
        e["dep"] = k[2] - 1
        #e["idx"] = cnt #if the id is less than 0, means it is not related with acl clauses
        #e["parenIdx"] = -1
        ccompDict.append(e)
        if 'advcl' in e["type"]:
            ccompList[(e["dep"])].append(e["dep"])  #advcl dependent (starting points)

    #the goal must be building the full acllist
    for i in ccompDict:
        if ccompList[i["dep"]] != []:
            #need more exclusion conditions
            #Stack.append(i)
            DFS_Traversal_Ccomp(i["dep"], i, ccompDict, ccompList)
    sentence.thatClauseDep = ccompList
    return


def DFS_Traversal_Ccomp(Dependent, ccompDict, ccompList):

    for i in ccompDict:
        if Dependent == i["gov"]:
            #i["idx"] = cnt
            #i["parenIdx"] = aclIdx
            if 'ccomp' in i["type"]:
                if i["dep"] not in ccompList[Dependent]:
                    ccompList[Dependent].append(i["dep"])
                    ccompList[Dependent].sort()
                NewDependent = i["dep"]
                DFS_Traversal_Wrb(NewDependent, i, ccompDict, ccompList)
            else:
                if i["dep"] not in ccompList[Dependent]:
                    ccompList[Dependent].append(i["dep"])
                    ccompList[Dependent].sort()
                #Must be sorted though
                DFS_Traversal_Wrb(Dependent, ccompDict, ccompList)

    ccompList[Dependent].append(Dependent)
    return

#Same logic between Wrb and Ccomp Extractor

def DFS_Traversal_Wrb(Dependent, WrbDict, WrbList):

    for i in WrbDict:
        if Dependent == i["gov"]:
            #i["idx"] = cnt
            #i["parenIdx"] = aclIdx
            if 'advcl' in i["type"]:
                if i["dep"] not in WrbList[Dependent]:
                    WrbList[Dependent].append(i["dep"])
                    WrbList[Dependent].sort()
                NewDependent = i["dep"]
                DFS_Traversal_Wrb(NewDependent, WrbDict, WrbList)
            else:
                if i["dep"] not in WrbList[Dependent]:
                    WrbList[Dependent].append(i["dep"])
                    WrbList[Dependent].sort()
                #Must be sorted though
                DFS_Traversal_Wrb(Dependent, WrbDict, WrbList)

    WrbList[Dependent].append(Dependent)
    return


def DFS_Traversal_Acl(Governer, aclElem, AclDict, AclList):
    Dependent = aclElem["dep"]
    #aclIdx = aclElem["idx"]
    #cnt = 0

    for i in AclDict:
        if Dependent == i["gov"]:
            #i["idx"] = cnt
            #i["parenIdx"] = aclIdx
            if 'acl' in i["type"]:
                if i["gov"] not in AclList[Governer]:
                    AclList[Governer].append(i["gov"])
                    AclList[Governer].sort()
                NewGoverner = i["gov"]
                DFS_Traversal_Acl(NewGoverner, i, AclDict, AclList)
            else:
                if i["gov"] not in AclList[Governer]:
                    AclList[Governer].append(i["gov"])
                    AclList[Governer].sort()
                #Must be sorted though
                DFS_Traversal_Acl(Governer, i, AclDict, AclList)

    AclList[Governer].append(Dependent)
    return
"""

def ConstructingBlockTrees(sentence):

    dep = sentence.depParse
    initBlockIdx = -1
    for j in dep:
        if j[1] == 0:
            initBlockIdx = j[2] #dependent of ROOT node
            break

    initBlock = BlockNode(initBlockIdx) #Dependent of Root
    initBlock.ParentBlockIdx = -1
    initBlock.thisType = 'I'
    #init' init Block
    #Filling the init Block with Contents
    sentence.BlockTreeNodes.append(initBlock)
    sentence.BlockTreeNodes_idx.append(initBlockIdx)
    #print("param: ", initBlockIdx)
    #print(sentence.PreprocessedTokenList)
    #print(sentence.depParse)
    FillingUpBlock_DFS(initBlock, sentence, initBlockIdx)  #1

    #for k in initBlock.getToeknCtx():
    #    sentence.PreprocessedTokenList[k]

def FillingUpBlock_DFS(blockNode, sentence, PrevTokenIdx):
    dep = sentence.depParse
    for i in dep:
            if 'acl' not in i[0] and 'advcl' not in i[0] and 'ccomp' not in i[0] and i[1] == PrevTokenIdx:
                blockNode.addTokenIdx(i[1] - 1)
                FillingUpBlock_DFS(blockNode, sentence, i[2]) #2
            elif i[1] == PrevTokenIdx:
                e = {}
                if 'acl' in i[0]:
                    e["depType"] = 'A'
                    e["TokenIdx"] = PrevTokenIdx - 1 # i[1]
                elif 'advcl' in i[0]:
                    e["depType"] = 'V'
                    e["TokenIdx"] = PrevTokenIdx - 1 # i[1]
                elif 'ccomp' in i[0]:
                    e["depType"] = 'C'
                    e["TokenIdx"] = PrevTokenIdx - 1 # i[1]


                blockNode.specialTokenCtx.append(e)
                blockNode.thisType = e["depType"]
                blockNode.addTokenIdx(i[1] - 1)
                newBlock = BlockNode(i[2]) ##
                blockNode.add_child(newBlock)
                sentence.BlockTreeNodes.append(newBlock)
                sentence.BlockTreeNodes_idx.append(i[2]) ##
                FillingUpBlock_DFS(newBlock, sentence, i[2])
    blockNode.addTokenIdx(PrevTokenIdx - 1)
        #Current Governer == prev Dependent
    return

def EncodingSentence(sentence):

    EncodedText = [] #list of strings from the bottom to top
    BlockIdx = sentence.BlockTreeNodes_idx

    print("Encodes Block idx: ", BlockIdx)
    Block = sentence.BlockTreeNodes
    for b in Block:
        if b.visited == True:
            continue
        else:
            strr = EncodingBlock_rec(b, EncodedText, Block, sentence)
            EncodedText.append(strr)

    sentence.EncodedSentences = EncodedText[:]
    #Need to traverse the Block Tree.
    return

def EncodingBlock_rec(b, EncodedText, Block, i):
    #print("Now it encodes Block! : ", b.TokenCtx)

    b.visited = True
    st = b.specialTokenCtx
    strr = ""

    cnt  =0
    for cc in b.TokenCtx:
        #print("Cnt: ", cnt)
        cnt = cnt + 1
        #print("PrePorcT", len(i.PreprocessedTokenList), "cc: ", cc)
        strr = strr + i.PreprocessedTokenList[cc]["ctx"]
        strr = strr + " "
        for k in st:
            if k["TokenIdx"] == 'cc':
                newB = BlockIdx_to_Blcok(k["TokenIdx"], Block)
                strTemp = EncodingBlock_rec(newB, EncodedText, Block, i)
                if k["depType"] == 'A':
                    #Affect Entity Emotions
                    i.PreprocessedTokenList[cc]["decoration"] = strTemp
                elif k["depType"] == 'V':
                    EncodedText.append(strTemp)
                elif k["depType"] == 'C':
                    EncodedText.append(strTemp)
                    strr = strr + "NN_"
                    strr = strr + str(k["TokenIdx"])

    #print("strr: ", strr)
    return strr

def BlockIdx_to_Blcok(idx, list):
    for ii in list:
        if ii.BlockIdx == idx:
            return ii


class BlockNode(object):
    def __init__(self, idx):
        self.BlockIdx = idx #for init block, it is 0 (Root) This is supposed to be root token idx
        self.TokenCtx = []

        self.ParentBlockIdx = -1 #For Init Block (Root Node) (0 -> -1 fitting in the list idx)

        self.children = []
        self.childrenIdx = []
        self.specialTokenCtx = [] #part of the TokenCtx (Entrance to Child Block
                                    # elem = {depType: (A or V or C), TokenIdx: }
        self.visited = False
        self.thisType = 'I' #I : init, V:Advcl, A, C
    def add_child(self, obj):
        self.childrenIdx.append(obj.BlockIdx)
        self.children.append(obj)
        obj.ParentBlockIdx = self.BlockIdx

    def getChildBlcok(self):
        return self.children
    def getToeknCtx(self):
        return self.TokenCtx

    def addTokenIdx(self, idx):
        if idx not in self.TokenCtx:
            self.TokenCtx.append(idx)   #3
            self.TokenCtx.sort()
        return

class Sentence:
    def __init__(self, text):
        self.Text = text
        self.type = 0
        self.TokenList = []
        self.depParse = []

        self.BlockTreeNodes = [] #BlockNode
        self.BlockTreeNodes_idx = []

        self.PreprocessedText = ""
        self.PreprocessedTokenList = []

        self.Relations = []
        self.Entities = []
        self.subEvents = []

        self.EncodedSentences = []
        self.Extracted_Information = []


def isQuoted(sentence):
    if sentence.TokenList[0]["pos"] == '``':
        return True
    else:
        return False


def Extract_IE_FromNounTokens(Token, i):
    Decoration = Token["decoration"]
    if Decoration != "":

        s_3 = Sentence(Decoration)
        posList = sNLP.pos(text)
        for k in posList:
            e = {}
            e["ctx"] = k[0]
            e["pos"] = k[1]
            e["neg"] = 0  # not neg
            e["tense"] = -1
            e["decoration"] = ""
            e["AltName"] = ""  # seperated by ,
            s_3.TokenList.append(e)
            s_3.PreprocessedTokenList.append(e)
            # s.TokenList = sNLP.pos(text)
        s_3.Text = Decoration
        s_3.PreprocessedTokenList[0] = Token
        if isQuoted(s_3):
            s_3.type = 1  # event type "quot"
        s_3.depParse = sNLP.dependency_parse(j)
        TensePreprocess(s_3)

        if s_3.type != 1:
            InversionTransformer(s_3)  # Should be applied on tree structures
        
        #FirstFormStablizer(s_3)
        strr = ""
        for k in s_3.PreprocessedTokenList:
            t = k["ctx"] + " "
            strr = strr + t

        s_3.PreprocessedText = strr
        i.subEvents.append(s_3)
        return
    else:
        return


def FirstFormStablizer(sentence):
    transformedSentence = ""
    #return transformedSentence
    none = "#NONE"
    tokens = sentence.PreprocessedTokenList
    deps = sentence.depParse
    thereIsObj = False
    idx = 0
    idxRoot = 0
    for i in deps:
        if "ROOT" == i[0]:
            idxRoot = i[2]
        if "obj" in i[0]:
            thereIsObj = True
            break
        idx = idx + 1
    if thereIsObj:
        return
    else:
        e = {}
        e["ctx"] = none
        e["pos"] = "NN"
        e["neg"] = 0  # not neg
        e["tense"] = -1
        e["decoration"] = ""
        e["AltName"] = ""  # seperated by ,
        sentence.PreprocessedTokenList.insert(idxRoot, e)
        strr = ""
        for k in sentence.PreprocessedTokenList:
            t = k["ctx"] + " "
            strr = strr + t
        sentence.PreprocessedText = strr

        return



def InversionTransformer(sentence):
    transformedSentence = ""
    DEP = sentence.depParse
    ThereIsObj = False
    ThereISubj = False
    none = "#NONE"
    idx = 0
    for d in DEP:
        if d[0] == 'ROOT':
            idxRoot = d[2]
        idx = idx + 1
        if 'subj' in d[0]:
            ThereISubj = True
        if 'obj' in d[0]:
            ThereIsObj = True
    e = {}
    e["ctx"] = none
    e["pos"] = "NN"
    e["neg"] = 0  # not neg
    e["tense"] = -1
    e["decoration"] = ""
    e["AltName"] = ""  # seperated by ,

    print("Senten: ", sentence.PreprocessedText)
    print(ThereIsObj)
    print(ThereISubj)
    if ThereIsObj and not ThereISubj:
        sentence.PreprocessedTokenList.insert(idxRoot - 1, e)
        strr = ""
        for k in sentence.PreprocessedTokenList:
            t = k["ctx"] + " "
            strr = strr + t
        sentence.PreprocessedText = strr
        return
    if ThereISubj and not ThereIsObj:
        sentence.PreprocessedTokenList.insert(idxRoot, e)
        strr = ""
        for k in sentence.PreprocessedTokenList:
            t = k["ctx"] + " "
            strr = strr + t
        sentence.PreprocessedText = strr
        return
    return

def NegationAndDetPreprocessing(sentence):
    depP = sentence.depParse
    #sentence.PreprocessedText = sentence.Text[:]
    sentence.PreprocessedTokenList = sentence.TokenList[:]
    for i in depP:
        if i[0] == 'neg':
            governer = i[1] - 1
            dependent = i[2] - 1 #Neg Indx
            sentence.PreprocessedTokenList[governer]["neg"] = 1
            sentence.PreprocessedTokenList[dependent]["ctx"] = "NEGATION_"
        elif i[0] == 'det':
            dependent = i[2] - 1 #Neg Indx
            sentence.PreprocessedTokenList[dependent]["ctx"] = "DET_"
    for k in sentence.PreprocessedTokenList:
        if k["ctx"] == "DET_" or k["ctx"] == "NEGATION_":
            sentence.PreprocessedTokenList.remove(k)
    isBeGoingTo = False
    idx = 0
    length = len(sentence.PreprocessedTokenList) - 1
    for k in sentence.PreprocessedTokenList:
        if k["ctx"] == 'is' or k["ctx"] == "'s" or k["ctx"] == 'am' or k["ctx"] == "'m" or \
                k["ctx"] == "are" or k["ctx"] == "'re":
            if idx + 3 <= length:
                e1 = sentence.PreprocessedTokenList[idx + 1]
                e2 = sentence.PreprocessedTokenList[idx + 2]
                e3 = sentence.PreprocessedTokenList[idx + 3]
                if e1["ctx"] == 'going' and e2["ctx"] == 'to' and e3['pos'] == 'VB':
                    e ={}
                    e["ctx"] = "will"
                    e["pos"] = "MD"
                    e["neg"] = 0  # not neg
                    e["tense"] = -1
                    del sentence.PreprocessedTokenList[idx]
                    del sentence.PreprocessedTokenList[idx]
                    del sentence.PreprocessedTokenList[idx]
                    sentence.PreprocessedTokenList.insert(idx, e)
                    length = len(sentence.PreprocessedTokenList) - 1
        idx = idx + 1

    strr = ""
    for k in sentence.PreprocessedTokenList:
        t = k["ctx"] + " "
        strr = strr + t

    sentence.PreprocessedText = strr

    #Replace be going to -> will
    #return transformedSentence

def Tense(sentence, auxList, governer):
    cond = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    for k in auxList:
        e = sentence.PreprocessedTokenList[k]["ctx"]
        if e == 'will':
            cond[0] = 1
        elif e == 'have':
            cond[1] = 1
        elif e == 'had':
            cond[2] = 1
        elif e == 'would':
            cond[3] = 1
        elif e == 'has':
            cond[4] = 1
        elif e == 'is' or e == "'s" or e == 'am' or e == "'m" or e == 'are' or e == "'re":
            cond[10] = 1
        elif e == 'was' or e == 'were':
            cond[11] = 1
        elif sentence.PreprocessedTokenList[k]["pos"] == 'VB':
            cond[12] = 1
        elif e == 'been':
            cond[13] = 1

    #print(sentence.TokenList[governer])
    if sentence.PreprocessedTokenList[governer]["pos"] == 'VBP' or \
            sentence.PreprocessedTokenList[governer]["pos"] == 'VBZ':
        cond[5] = 1
    if sentence.PreprocessedTokenList[governer]["pos"] == 'VBG':
        cond[6] = 1 # ing
    if sentence.PreprocessedTokenList[governer]["pos"] == 'VBD':
        cond[7] = 1 #Past tense
    if sentence.PreprocessedTokenList[governer]["pos"] == 'VBN':
        cond[8] = 1 #Hve - Past tense
    if sentence.PreprocessedTokenList[governer]["pos"] == 'VB':
        cond[9] = 1 #Hve - Past tense

    #print("cond: ", cond)
    if cond[5] == 1:
        return 0
    elif cond[7] == 1:
        return 1 #simple past
    elif cond == [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0]:
        return 2 #Future - Sure
    elif cond == [0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0]:
        return 3 #Future - Careful
    elif cond == [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0]:
        return 4 #ing present
    elif cond == [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0]:
        return 5 #ing past
    elif cond == [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0]:
        return 6  # will be ing
    elif cond == [0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0] or cond == [0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0]:
        return 7 # have, has p.p
    elif cond == [0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0]:
        return 8  # had p.p
    elif cond == [1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0]:
        return 9  #will have p.p
    elif cond == [0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1] or cond == [0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 1]:
        return 10  # have/has been ing
    elif cond == [0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1]:
        return 11  # had been ing
    elif cond == [1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1]:
        return 12  # will have been ing
        #e["ctx"] = k[0]
        #e["pos"] = k[1]
    return -1

def TensePreprocess(sentence):
    #tense = 0~11
    depP = sentence.depParse
    governer = 1
    length = len(depP)
    cnt = -1
    for i in depP:
        cnt = cnt + 1
        if i[0] == 'aux' and i[0] != 'neg':
            governer = i[1] - 1
            auxList = []
            #print("depP", depP)
            #print("Token", sentence.PreprocessedTokenList)
            #print("length", length)
            for ii in range(cnt, length):
                elem = depP[ii]
                if elem[1] - 1 == governer and (elem[0] == 'aux' and elem[0] != 'neg'):
                    dependent = elem[2] - 1
                    auxList.append(dependent)
            #print("Tokens: ", sentence.PreprocessedTokenList)
            #print("param: ", auxList, governer)
            tense = Tense(sentence, auxList, governer)
            #if tense == going to then apply it onto the verb next to TO
            #print("tense: ", tense)
            sentence.PreprocessedTokenList[governer]["tense"] = tense
            for k in auxList:
                sentence.PreprocessedTokenList[k]["ctx"] = "AUX_"

    for i in sentence.PreprocessedTokenList:
        if i["ctx"] == "AUX_":
            sentence.PreprocessedTokenList.remove(i)

    #print("TL: ", sentence.depParse)
    #print("AA: ", sentence.PreprocessedText)
    strr = ""
    for k in sentence.PreprocessedTokenList:
        strr = strr + k["ctx"]
        strr = strr + " "
    sentence.PreprocessedText = strr
    #print("DD: ", sentence.PreprocessedText)

"""
def advModModifier(sentence):
    return
"""

#ADV mode Done in the context
#PARAMETERS
def gettingFootballParameters(sortedLists, EntityList, RelationList, EntityListOther, RelationListOther, teamName
                              , EventList, TargetList, unsortedEntityList,
                              unsortedRelationList, ObjEntityList, expList, vocab, vecs):


    joyEntities = sortedLists[0]
    hateEntities = sortedLists[1]
    joyRelations = sortedLists[2]
    hateRelations = sortedLists[3]

    # How much other’s perception affects your perception?  O
    FearTarget = 0
    AngerTarget = 0
    DisgustTartget = 0
    JoyTarget = 0
    SadnessTarget = 0

    FearOthers = 0
    AngerOthers = 0
    DisgustOthers = 0
    JoyOthers = 0
    SadnessOthers = 0

    for i in EntityList:
        FearTarget = FearTarget + i['fear']
        SadnessTarget = i['sadness'] + SadnessTarget
        JoyTarget = i['joy'] + JoyTarget
        DisgustTartget = i['disgust'] + DisgustTartget
        AngerTarget = AngerTarget + i['anger']

    for i in RelationList:
        FearTarget = FearTarget + i['fear']
        SadnessTarget = i['sadness'] + SadnessTarget
        JoyTarget = i['joy'] + JoyTarget
        DisgustTartget = i['disgust'] + DisgustTartget
        AngerTarget = AngerTarget + i['anger']

    for i in EntityListOther:
        FearOthers = FearOthers + i['fear']
        SadnessOthers = i['sadness'] + SadnessOthers
        JoyOthers = i['joy'] + JoyOthers
        DisgustOthers = i['disgust'] + DisgustOthers
        AngerOthers = AngerOthers + i['anger']

    for i in RelationListOther:
        FearOthers = FearOthers + i['fear']
        SadnessOthers = i['sadness'] + SadnessOthers
        JoyOthers = i['joy'] + JoyOthers
        DisgustOthers = i['disgust'] + DisgustOthers
        AngerOthers = AngerOthers + i['anger']

    param1_1 = 0
    param1_2 = 0
    param1_3 = 0
    param1_4 = 0
    param1_5 = 0

    if FearOthers > FearTarget:
        param1_1 = FearTarget/FearOthers
    else:
        param1_1 = FearOthers/FearTarget

    if JoyOthers > JoyTarget:
        param1_2 = JoyTarget / JoyOthers
    else:
        param1_2 = JoyOthers/JoyTarget

    if AngerOthers > AngerTarget:
        param1_3 = AngerTarget / AngerOthers
    else:
        param1_3 = AngerOthers / AngerTarget

    if DisgustOthers > DisgustTartget:
        param1_4 = DisgustTartget/ DisgustOthers
    else:
        param1_4 = DisgustOthers / DisgustTartget

    if SadnessOthers > SadnessTarget:
        param1_5 = SadnessTarget / SadnessOthers
    else:
        param1_5 = SadnessOthers / SadnessTarget

    param1 = (param1_1 + param1_2 + param1_3 + param1_4 + param1_5)/5

    addupNegative = 0
    # Has any significant development happened to your team that you feel positively about? O
    freq = 1
    for i in EntityListOther:
        if teamName == i['strr']:
            addupNegative = addupNegative + i['fear'] + i['anger'] + i['sadness'] + i['disgust']
            freq = freq + i['freq']
    for j in EntityList:
        if teamName == j['strr']:
            addupNegative = addupNegative + j['fear'] + j['anger'] + j['sadness'] + j['disgust']
            freq = freq + j['freq']

    param3 = addupNegative / freq
    #playerList

    # Has any significant development happened to your team that you feel negatively about? O
    addupJoy = 0
    # Has any significant development happened to your team that you feel positively about? O
    freq = 1
    for i in EntityListOther:
        if teamName == i['strr']:
            addupJoy = addupJoy + i['joy']
            freq= i['freq']
    for j in EntityList:
        if teamName == j['strr']:
            addupJoy = addupJoy + j['joy']
            freq = freq + j['freq']

    param4 = addupJoy / freq

    # How intense are your reactions to football related events? O

    totalEmotion = 0
    freq = 0
    for t in TargetList:
        for j in EntityList:
            if t == j['strr']:
                totalEmotion = totalEmotion + j['joy'] + j['fear'] + j['anger'] + j['sadness'] + j['disgust']
                freq = freq + 5*j['freq']

    param5 = totalEmotion/freq


    # How much do you value past events when deciding goals for current events? X
    freq = 1
    freq2 = 1
    param6 = 0
    param7 = 0
    for e in RelationList:
        eveidx = e["eveIdx"]
        subidx = e['subidx']
        for i in EventList[eveidx].subEvents[subidx].PreprocessedTokenList:
            if i['ctx'] == e['strr']:
                if (i['tense'] == 1 or i['tense'] == 5 or i['tense'] == 11):
                    param6 = e['joy'] + e['fear'] + e['anger'] + e['sadness'] + e['disgust']
                    freq = freq + 5 * e['freq']
                elif i['tense'] == 10 or i['tense'] == 7: #middle
                    param6 = e['joy'] + e['fear'] + e['anger'] + e['sadness'] + e['disgust']
                    freq = freq + 10 * e['freq']
                    param7 = e['joy'] + e['fear'] + e['anger'] + e['sadness'] + e['disgust']
                    freq2 = freq2 + 10 * e['freq']
                elif i['tense'] == 1 or i['tense'] == 4:
                    param7 = e['joy'] + e['fear'] + e['anger'] + e['sadness'] + e['disgust']
                    freq2 = freq2 + 10 * e['freq']

    param6 = param6 / freq
    param7 = param7 / freq

    # Are your feelings regarding a game based on the present game or the teams history? (0 for present - 1
    # for history) 1 (Fundamentally)
    if param6 > param7:
        param7 = 0
    else:
        param7 = 1

    param9 = 0
    freq = 1
    # How good are you at coping? o
    subtractedNegative = 0
    for i in range(1, len(unsortedEntityList)):
        fear = unsortedEntityList[i]['fear']
        anger = unsortedEntityList[i]['anger']
        sadness = unsortedEntityList[i]['sadness']
        disgust = unsortedEntityList[i]['disgust']

        fear0 = unsortedEntityList[i-1]['fear']
        anger0 = unsortedEntityList[i-1]['anger']
        sadness0 = unsortedEntityList[i-1]['sadness']
        disgust0 = unsortedEntityList[i-1]['disgust']

        if fear < fear0:
            subtractedNegative = subtractedNegative+(fear0 - fear)
        if anger < anger0:
            subtractedNegative = subtractedNegative+(anger0 - anger)
        if sadness < sadness0:
            subtractedNegative = subtractedNegative+(sadness0 - sadness)
        if disgust < disgust0:
            subtractedNegative = subtractedNegative+(disgust0 - disgust)
        freq = freq + 4 * unsortedEntityList[i]['freq']

    #print("len ent: ", len(unsortedEntityList))
    #print("len rel: ", len(unsortedRelationList))
    #print(unsortedEntityList)
    for i in range(1, len(unsortedRelationList)):
        fear = unsortedRelationList[i]['fear']
        anger = unsortedRelationList[i]['anger']
        sadness = unsortedRelationList[i]['sadness']
        disgust = unsortedRelationList[i]['disgust']

        fear0 = unsortedRelationList[i-1]['fear']
        anger0 = unsortedRelationList[i-1]['anger']
        sadness0 = unsortedRelationList[i-1]['sadness']
        disgust0 = unsortedRelationList[i-1]['disgust']

        if fear < fear0:
            subtractedNegative = subtractedNegative+(fear0 - fear)
        if anger < anger0:
            subtractedNegative = subtractedNegative+(anger0 - anger)
        if sadness < sadness0:
            subtractedNegative = subtractedNegative+(sadness0 - sadness)
        if disgust < disgust0:
            subtractedNegative = subtractedNegative+(disgust0 - disgust)
        freq = freq + 4 * unsortedRelationList[i]['freq']

    param9 = subtractedNegative / freq

    # Are there any events regarding the team that may help you cope?X
    param8 = param9/(1 - param3)
    if param8 > 1:
        param8 = 1

    # What players of the team does the character like?O - joyEntities (Don't use)
    # What players of the team does the character dislike? (Rest are neutral I guess)O (Don't use)
    # Do you play football yourself?O - Don't use

    # What type of game would you like to see (blowout, fair game, doesn’t matter)?O
    idx = 0
    freq = 1
    freq2 = 1
    param10 = 0
    totalEmotion = 0
    totalEmotion2 = 0
    for i in EntityList:
        if 'blowout' in i["strr"]:
            totalEmotion = totalEmotion + i['joy']
            freq = freq + 5 * i['freq']
        if 'fair game' in i["strr"]:
            totalEmotion2 = totalEmotion2 + i['joy']
            freq2 = freq2 + 5 * i['freq']

    if totalEmotion2 != 0:
        dec = freq2*totalEmotion/(totalEmotion2*freq)
        if dec > 0.7:
            param10 = 1
        elif dec < 0.3:
            param10 = 0.5
        else:
            param10 = 0
    else:
        if totalEmotion != 0:
            param10 = 1
        else:
            param10 = 0

    # How much experience do you have with football? X/O
    param2 = param2_generator(EventList, expList, ObjEntityList, EntityList, unsortedRelationList,
                              vocab, vecs)

    return {"football": param2, "positive": param3, "negative": param4, "coping_team": param9, "coping": param8, "reaction": param5, "past": param6, "game_fair": param10}


def UpdateEmotionFactors(EntityList, RelationList, list, targetEmotion, DiscountFactor, eventIdx,
                         subeventIdx, ObjEntityList, EventList):

    for e in list:
        #print(e)
        relation = e["relation"]
        subject = e["subject"]
        object = e["object"]

        fear = targetEmotion['fear']
        joy = targetEmotion['joy']
        disgust = targetEmotion['disgust']
        anger = targetEmotion['anger']
        sad = targetEmotion['sadness']
        # elem = {"strr": relation, 'fear': fear, 'sadness': sad, 'joy': joy,
        #        'disgust': disgust, 'anger': anger}
        Exist = False
        ctxIdx = EventList[EventIdx].subEvents[subeventIdx].Relations[0]["TokenIdx"]
        neg = EventList[EventIdx].subEvents[subeventIdx].PreprocessedTokenList[ctxIdx]["neg"]

        for e in RelationList:
            if e["strr"] == relation:
                if neg == 1:
                    e['fear'] = e['fear'] + joy * DiscountFactor
                    e['sadness'] = e['sadness'] + joy * DiscountFactor
                    e['joy'] = e['joy'] + (fear + disgust + anger + sad)*DiscountFactor/4
                    e['disgust'] = e['disgust'] + joy * DiscountFactor
                    e['anger'] = e['anger'] + joy * DiscountFactor
                    e['freq'] = e['freq'] + 1
                    e['eveIdx'] = eventIdx
                    e['subidx'] = subeventIdx
                else:
                    e['fear'] = e['fear'] + fear * DiscountFactor
                    e['sadness'] = e['sadness'] + sad * DiscountFactor
                    e['joy'] = e['joy'] + joy * DiscountFactor
                    e['disgust'] = e['disgust'] + disgust * DiscountFactor
                    e['anger'] = e['anger'] + anger * DiscountFactor
                    e['freq'] = e['freq'] + 1
                    e['eveIdx'] = eventIdx
                    e['subidx'] = subeventIdx
                # RelationList.append(e)
                Exist = True
                break
        if not Exist:
            if neg == 1:
                e = {}
                e["strr"] = relation
                e['fear'] = joy * DiscountFactor
                e['sadness'] = joy * DiscountFactor
                e['joy'] = (sad + fear + disgust + anger)/4
                e['disgust'] = joy * DiscountFactor
                e['anger'] = joy * DiscountFactor
                e['freq'] = 1
                e['eveIdx'] = eventIdx
                e['subidx'] = subeventIdx
                RelationList.append(e)
            else :
                e = {}
                e["strr"] = relation
                e['fear'] = fear * DiscountFactor
                e['sadness'] = sad * DiscountFactor
                e['joy'] = joy * DiscountFactor
                e['disgust'] = disgust * DiscountFactor
                e['anger'] = anger * DiscountFactor
                e['freq'] = 1
                e['eveIdx'] = eventIdx
                e['subidx'] = subeventIdx
                RelationList.append(e)
            ek = {}
            ek["strr"] = object
            ek['fear'] = fear*DiscountFactor
            ek['sadness'] = sad*DiscountFactor
            ek['joy'] = joy*DiscountFactor
            ek['disgust'] = disgust*DiscountFactor
            ek['anger'] = anger*DiscountFactor
            ek['freq'] = 1
            ek['eveIdx'] = eventIdx
            ek['subidx'] = subeventIdx
            ObjEntityList.append(ek)

        Exist = False
        for e in EntityList:
            if e["strr"] == subject:
                e['fear'] = e['fear'] + fear*DiscountFactor
                e['sadness'] = e['sadness'] + sad*DiscountFactor
                e['joy'] = e['joy'] + joy*DiscountFactor
                e['disgust'] = e['disgust'] + disgust*DiscountFactor
                e['anger'] = e['anger'] + anger*DiscountFactor
                e['freq'] = e['freq'] + 1
                e['eveIdx'] = eventIdx
                e['subidx'] = subeventIdx
                # EntityList.append(e)
                Exist = True
                break
        if not Exist:
            e = {}
            e["strr"] = subject
            e['fear'] = fear*DiscountFactor
            e['sadness'] = sad*DiscountFactor
            e['joy'] = joy*DiscountFactor
            e['disgust'] = disgust*DiscountFactor
            e['anger'] = anger*DiscountFactor
            e['freq'] = 1
            e['eveIdx'] = eventIdx
            e['subidx'] = subeventIdx
            EntityList.append(e)

        Exist = False
        for e in RelationList:
            if e["strr"] == object:
                e['fear'] = e['fear'] + fear*DiscountFactor
                e['sadness'] = e['sadness'] + sad*DiscountFactor
                e['joy'] = e['joy'] + joy*DiscountFactor
                e['disgust'] = e['disgust'] + disgust*DiscountFactor
                e['anger'] = e['anger'] + anger*DiscountFactor
                e['freq'] = e['freq'] + 1
                e['eveIdx'] = eventIdx
                e['subidx'] = subeventIdx
                # EntityList.append(e)
                Exist = True
                break
        if not Exist:
            e = {}
            e["strr"] = object
            e['fear'] = fear*DiscountFactor
            e['sadness'] = sad*DiscountFactor
            e['joy'] = joy*DiscountFactor
            e['disgust'] = disgust*DiscountFactor
            e['anger'] = anger*DiscountFactor
            e['freq'] = 1
            e['eveIdx'] = eventIdx
            e['subidx'] = subeventIdx
            EntityList.append(e)
    return


def gaussian(x, mu, sig):
    return np.exp(-np.power(x - mu, 2.) / (2 * np.power(sig, 2.)))

def Entity_Relation_List_sorting(EntityList, RelationList):

    JoyEntities = EntityList[:]
    HateEntities = EntityList[:]
    for e in HateEntities:
        e["disgust"] = e["disgust"] + e["fear"] + e["anger"] + e["sadness"]/4
    sorted(JoyEntities, key=lambda k: k['joy'])
    sorted(HateEntities, key=lambda k: k['disgust'])

    JoyRelation = RelationList[:]
    HateRelation = RelationList[:]
    for e in HateRelation:
        e["disgust"] = e["disgust"] + e["fear"] + e["anger"] + e["sadness"]/4
    sorted(JoyRelation, key=lambda k: k['joy'])
    sorted(HateRelation, key=lambda k: k['disgust'])

    return [JoyEntities, HateEntities, JoyRelation, HateRelation]

def UpdateSideParts(EntityList, RelationList, targetEmotion, EventList, Cnt, eventIdx, subeventIdx, ObjEntityList):

    sig = 2
    mu = cnt

    for i in range(0, len(EventList)):
        if abs(i - Cnt) > 4:
            continue
        eventInstance = EventList[i]
        for e in eventInstance.subEvents:
            DiscountFactor = gaussian(i, mu, sig)
            IE_list = e.Extracted_Information
            # j.Extracted_Information = list[0]['openie']
            UpdateEmotionFactors(EntityList, RelationList, IE_list, targetEmotion, DiscountFactor,
                                 eventIdx, subeventIdx, ObjEntityList, EventList)

    return


def UpdateEmotionFactors_Others(EntityList, RelationList, list, targetEmotion, DiscountFactor, eventIdx, subeventIdx,
                                EventList):

    for e in list:
        #print(e)
        relation = e["relation"]
        subject = e["subject"]
        object = e["object"]

        fear = targetEmotion['fear']
        joy = targetEmotion['joy']
        disgust = targetEmotion['disgust']
        anger = targetEmotion['anger']
        sad = targetEmotion['sadness']
        # elem = {"strr": relation, 'fear': fear, 'sadness': sad, 'joy': joy,
        #        'disgust': disgust, 'anger': anger}
        Exist = False
        ctxIdx = EventList[EventIdx].subEvents[subeventIdx].Relations[0]["TokenIdx"]
        neg = EventList[EventIdx].subEvents[subeventIdx].PreprocessedTokenList[ctxIdx]["neg"]

        for e in RelationList:
            if e["strr"] == relation:
                if neg == 1:
                    e['fear'] = e['fear'] + joy * DiscountFactor
                    e['sadness'] = e['sadness'] + joy * DiscountFactor
                    e['joy'] = e['joy'] + (fear + disgust + anger + sad)*DiscountFactor/4
                    e['disgust'] = e['disgust'] + joy * DiscountFactor
                    e['anger'] = e['anger'] + joy * DiscountFactor
                    e['freq'] = e['freq'] + 1
                    e['eveIdx'] = eventIdx
                    e['subidx'] = subeventIdx
                else:
                    e['fear'] = e['fear'] + fear * DiscountFactor
                    e['sadness'] = e['sadness'] + sad * DiscountFactor
                    e['joy'] = e['joy'] + joy * DiscountFactor
                    e['disgust'] = e['disgust'] + disgust * DiscountFactor
                    e['anger'] = e['anger'] + anger * DiscountFactor
                    e['freq'] = e['freq'] + 1
                    e['eveIdx'] = eventIdx
                    e['subidx'] = subeventIdx
                # RelationList.append(e)
                Exist = True
                break
        if not Exist:
            if neg == 1:
                e = {}
                e["strr"] = relation
                e['fear'] = joy * DiscountFactor
                e['sadness'] = joy * DiscountFactor
                e['joy'] = (sad + fear + disgust + anger)/4
                e['disgust'] = joy * DiscountFactor
                e['anger'] = joy * DiscountFactor
                e['freq'] = 1
                e['eveIdx'] = eventIdx
                e['subidx'] = subeventIdx
                RelationList.append(e)
            else :
                e = {}
                e["strr"] = relation
                e['fear'] = fear * DiscountFactor
                e['sadness'] = sad * DiscountFactor
                e['joy'] = joy * DiscountFactor
                e['disgust'] = disgust * DiscountFactor
                e['anger'] = anger * DiscountFactor
                e['freq'] = 1
                e['eveIdx'] = eventIdx
                e['subidx'] = subeventIdx
                RelationList.append(e)

        Exist = False
        for e in EntityList:
            if e["strr"] == subject:
                e['fear'] = e['fear'] + fear*DiscountFactor
                e['sadness'] = e['sadness'] + sad*DiscountFactor
                e['joy'] = e['joy'] + joy*DiscountFactor
                e['disgust'] = e['disgust'] + disgust*DiscountFactor
                e['anger'] = e['anger'] + anger*DiscountFactor
                e['freq'] = e['freq'] + 1
                e['eveIdx'] = eventIdx
                e['subidx'] = subeventIdx
                # EntityList.append(e)
                Exist = True
                break
        if not Exist:
            e = {}
            e["strr"] = subject
            e['fear'] = fear*DiscountFactor
            e['sadness'] = sad*DiscountFactor
            e['joy'] = joy*DiscountFactor
            e['disgust'] = disgust*DiscountFactor
            e['anger'] = anger*DiscountFactor
            e['freq'] = 1
            e['eveIdx'] = eventIdx
            e['subidx'] = subeventIdx
            EntityList.append(e)

        Exist = False
        for e in RelationList:
            if e["strr"] == object:
                e['fear'] = e['fear'] + fear*DiscountFactor
                e['sadness'] = e['sadness'] + sad*DiscountFactor
                e['joy'] = e['joy'] + joy*DiscountFactor
                e['disgust'] = e['disgust'] + disgust*DiscountFactor
                e['anger'] = e['anger'] + anger*DiscountFactor
                e['freq'] = e['freq'] + 1
                e['eveIdx'] = eventIdx
                e['subidx'] = subeventIdx
                # EntityList.append(e)
                Exist = True
                break
        if not Exist:
            e = {}
            e["strr"] = object
            e['fear'] = fear*DiscountFactor
            e['sadness'] = sad*DiscountFactor
            e['joy'] = joy*DiscountFactor
            e['disgust'] = disgust*DiscountFactor
            e['anger'] = anger*DiscountFactor
            e['freq'] = 1
            e['eveIdx'] = eventIdx
            e['subidx'] = subeventIdx
            EntityList.append(e)
    return

def UpdateSideParts_Others(EntityList, RelationList, targetEmotion, EventList, Cnt, eventIdx, subeventIdx):

    sig = 2
    mu = cnt

    for i in range(0, len(EventList)):
        if abs(i - Cnt) > 4:
            continue
        eventInstance = EventList[i]
        for e in eventInstance.subEvents:
            DiscountFactor = gaussian(i, mu, sig)
            IE_list = e.Extracted_Information
            # j.Extracted_Information = list[0]['openie']
            UpdateEmotionFactors_Others(EntityList, RelationList, IE_list, targetEmotion, DiscountFactor, eventIdx,
                                 subeventIdx, EventList)

    return




if __name__ == '__main__':

    Target = ['I']
    Others = ['Other']

    entityExpword = ["football", "game", "fan", "team"]
    relationExpword = ["play", "cheer", "pull", "watch"]
    decorationExpword = ["lot", "plenty", "really"]


    embeddings_index = []  # dict()
    f = open('./glove.6B.50d.txt', 'r')
    wordVecap = []
    idx = 0
    for line in f:
        values = line.split()
        word = values[0]
        wordVecap.append(word)
        coefs = np.asarray(values[1:], dtype='float32')
        # embeddings_index[word] = coefs
        embeddings_index.append((idx, coefs))
        idx = idx + 1
    f.close()

    sNLP = StanfordNLP()
    text = """"""
    f = open('./character_corpus.txt', 'r')
    for ALine in f:
        text = text + ALine
    f.close()
    #print("Annotate:", sNLP.annotate(text))
    #print("POS:", sNLP.pos(text))
    #print("Tokens:", sNLP.word_tokenize(text))

    sentences = (sNLP.giveSentences(text))
    #for i in sentences[0]:
    #    print("Parse:", (sNLP.parse(i)))
    print(text)
    EventList = []
    for j in sentences[0]:
        Text = j
        j.replace("gonna", "going to")
        s = Sentence(j)
        posList = sNLP.pos(text)
        for k in posList:
            e = {}
            e["ctx"] = k[0]
            e["pos"] = k[1]
            e["neg"] = 0 #not neg
            e["tense"] = -1
            e["decoration"] = ""
            e["AltName"] = "" #seperated by ,
            s.TokenList.append(e)
            #s.TokenList = sNLP.pos(text)
        if isQuoted(s):
            s.type = 1 #event type "quot"
        h = j[:]
        DP = sNLP.dependency_parse(j)
        for n in DP:
            if n[0] == 'advmod':
                gov = n[1] - 1
                dep = n[2] - 1
                ctx = posList[gov][0]
                ctx2 = ctx + " to"
                h.replace(ctx, ctx2, 1)

        for jj in s.TokenList:
            if jj["ctx"] == 'was':
                jj["ctx"] = 'is'
                jj["tense"] = 1
                j.replace('was', 'is', 1)
        j = h
        s.Text = j
        s.depParse = sNLP.dependency_parse(j)
        EventList.append(s)


    for i in EventList:


        NegationAndDetPreprocessing(i) #done

        #Should think about the coref and its design

        i.depParse = sNLP.dependency_parse(i.PreprocessedText) #done
        #print("Sentence_PreprocessedText:", EventList[0].PreprocessedText)
        #print("newDepP:", i.depParse)

        #wrbExtraction(i) #done
        #aclExtraction(i) #done
        #ccompExtraction(i) #done

        ConstructingBlockTrees(i) #done

        #print("Blocks Tokens: ", i.BlockTreeNodes[0].TokenCtx)
        #print("Blocks IDices: ", i.BlockTreeNodes_idx)
        #for kk in i.BlockTreeNodes_idx:
        #    print("Block idx: ", kk, " -: ", BlockIdx_to_Blcok(kk, i.BlockTreeNodes).TokenCtx)


        EncodingSentence(i) #done
        print("Encoded Sentences: ", i.EncodedSentences)

        for j in i.EncodedSentences:
            s_2 = Sentence(j)
            posList = sNLP.pos(j)
            for k in posList:
                e = {}
                e["ctx"] = k[0]
                e["pos"] = k[1]
                e["neg"] = 0  # not neg
                e["tense"] = -1
                e["decoration"] = ""
                e["AltName"] = ""  # seperated by ,
                s_2.TokenList.append(e)
                s_2.PreprocessedTokenList.append(e)
                # s.TokenList = sNLP.pos(text)
            s_2.Text = j
            s_2.PreprocessedText = j
            if isQuoted(s_2):
                s_2.type = 1  # event type "quot"
            s_2.depParse = sNLP.dependency_parse(j)
            TensePreprocess(s_2)
            s_2.depParse = sNLP.dependency_parse(s_2.PreprocessedText)
            if s_2.type != 1:
                InversionTransformer(s_2) #Should be applied on tree structures
            else:
                InversionTransformer(s_2)

            s_2.depParse = sNLP.dependency_parse(s_2.PreprocessedText)
            FirstFormStablizer(s_2)
            """
            strr = ""
            for k in s_2.PreprocessedTokenList:
                t = k["ctx"] + " "
                strr = strr + t

            s_2.PreprocessedText = strr
            """
            i.subEvents.append(s_2)

        for t in i.PreprocessedTokenList:
            Extract_IE_FromNounTokens(t, i)


    #print("Sentence_Text:", EventList[0].Text)
    #print("Sentence_PreprocessedText:", EventList[0].PreprocessedText)
    #print("Sentence_Token:", EventList[0].TokenList)
    #print("Sentence_PreprocToken:", EventList[0].PreprocessedTokenList)

    #print("NER:", sNLP.ner(text))
    ##print("Parse:", (sNLP.parse(text)))
    #print("Dep Parse:", sNLP.dependency_parse(text))
    #print("Coreference:", sNLP.coref(text))


    service = NaturalLanguageUnderstandingV1(
        version='2018-03-16',
        url='https://gateway.watsonplatform.net/natural-language-understanding/api',
        username='35e3cfe1-1da8-4968-85d9-7ccd7de2a0f1',
        password='eN0OsLhEqkxZ')

    service2 = ToneAnalyzerV3(
        version='2018-06-15',
        url='https://gateway.watsonplatform.net/tone-analyzer/api',
        username='e958a321-3b12-4104-ac4c-c1a3c55d385c',
        password='wmVsLpwPDmHT'
    )

    response = service.analyze(
        text='Bruce Banner is the Hulk and Bruce Wayne is BATMAN!' 'Superman fears not Banner, but Wayne.',
        features=Features(entities=EntitiesOptions(sentiment=True),
                          keywords=KeywordsOptions()),
        emotion=EmotionOptions(
            targets=['Bruce'])
    ).get_result()

    """
    response2 = service2.tone(
        {'text': text},
        'application/json'
    ).get_result()
    """

    """
    for i in EventList:
        for j in i.subEvents:
            print("SubEvents: ", j.PreprocessedText)
    """

    SubjEntityList = []
    ObjEntityList = []

    RelationList = []
    EntityList = []

    RelationListOther = []
    EntityListOther = []

    entityExpVect = []
    relationExpVect = []
    decorationExpVect = []

    for elem in entityExpword:
        entityExpVect.append(embeddings_index[wordVecap.index(elem)][1].tolist())
    for elem in relationExpword:
        relationExpVect.append(embeddings_index[wordVecap.index(elem)][1].tolist())
    for elem in decorationExpword:
        decorationExpVect.append(embeddings_index[wordVecap.index(elem)][1].tolist())

    param2Words = [entityExpVect, relationExpVect, decorationExpVect]

    for k in EventList:
        for j in i.subEvents:

            #print("subEvent Text: ", j.PreprocessedText)

            text = j.PreprocessedText
            IE = sNLP.OpenIE(text)
            list = (IE['sentences'])
            j.Extracted_Information = list[0]['openie']
            tl = j.PreprocessedTokenList
            for ee in j.Extracted_Information:
                e = {}
                e["strr"] = ee["relation"]
                idx = 0
                for elem in tl:
                    if ee["relation"] == elem['ctx']:
                        e["TokenIdx"] = idx
                        break
                    idx = idx + 1
                j.Relations.append(e)
                e_2 = {}
                e_2["strr"] = ee["subject"]
                j.Entities.append(e_2)
                e_3 = {}
                e_3["strr"] = ee["object"]
                j.Entities.append(e_3)



    Cnt = 0
    EventIdx = 0
    for k in EventList:
        SubeventIdx = 0
        for j in i.subEvents:
            text = j.PreprocessedText
            IE = sNLP.OpenIE(text)
            list = (IE['sentences'])
            #print("Text: ", text)
            #print("IE: ", list[0]['openie'])

            j.Extracted_Information = list[0]['openie']

            response = service.analyze(
                text=text,
                features=Features(entities=EntitiesOptions(sentiment=True),
                                  keywords=KeywordsOptions(), emotion=EmotionOptions(targets=Target))
            ).get_result()

            response2 = service.analyze(
                text=text,
                features=Features(entities=EntitiesOptions(sentiment=True),
                                  keywords=KeywordsOptions(), emotion=EmotionOptions(targets=Others))
            ).get_result()

            if 'emotion' in response:
                #print("Overal Emotion", (response)['emotion'])
                if 'targets' in (response)['emotion']:
                    targetEmotion = (response)['emotion']['targets'][0]['emotion']  #'text' : I
                    #print("OtherEmotion: ", targetEmotion) #intended
                    UpdateEmotionFactors_Others(EntityListOther, RelationListOther, list[0]['openie'], targetEmotion, 1
                                                ,EventIdx, SubeventIdx, EventList)
                    UpdateSideParts_Others(EntityListOther, RelationListOther, targetEmotion, EventList, Cnt, EventIdx
                                           ,SubeventIdx)
                else:
                    print("No target_others!")
                    #docEmotion = (response)['emotion']['document']['emotion']
                    #print("TargetEmotion: ", docEmotion)

            if 'emotion' in response:
                if 'targets' in (response)['emotion']:
                    targetEmotion = (response)['emotion']['targets'][0]['emotion']  #'text' : I
                    #print("TargetEmotion: ", targetEmotion)
                    UpdateEmotionFactors(EntityList, RelationList, list[0]['openie'], targetEmotion, 1, EventIdx,
                                         SubeventIdx, ObjEntityList, EventList)
                    UpdateSideParts(EntityList, RelationList, targetEmotion, EventList, Cnt, EventIdx, SubeventIdx,
                                    ObjEntityList)
                else:
                    print("No target!")
                    #docEmotion = (response)['emotion']['document']['emotion']
                    #print("TargetEmotion: ", docEmotion)
                #print((response)['emotion']['target'])
            else:
                    print("Neutral!")
            Cnt = Cnt + 1
            print("\n")
            SubeventIdx = SubeventIdx + 1
        EventIdx = EventIdx + 1

    print("\n\n")
    print("Entity List: ", EntityList)
    print("Relation List: ", RelationList)

    unsortedEntityList = EntityList[:]
    unsortedRelationList = RelationList[:]
    #print("Unsorted Entity List: ", unsortedEntityList)
    sortedLists = Entity_Relation_List_sorting(EntityList, RelationList)

    teamName = ""
    playerList = [""]

    ParamList = gettingFootballParameters(sortedLists, EntityList, RelationList, EntityListOther,
                                          RelationListOther, teamName, EventList, Target, unsortedEntityList,
                                          unsortedRelationList, ObjEntityList, param2Words, wordVecap, embeddings_index)

    print(ParamList)






