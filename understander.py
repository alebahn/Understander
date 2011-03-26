#!/usr/bin/env python3
#from __future__ import print_function
from linkgrammar import lp, Sentence, Linkage #,clg,ParseOptions,Dictionary
from understanding import conversation, infinitive, adverb, stripSub, number, detectKind
import sys
#import linkgrammar
#import os
#import subprocess
#import festival

def findProblems(linkage,sent,outFile):     #TODO: replace [~] words and return error code
    for i, word in enumerate(linkage.get_words()):
        index=word.find('[~]')
        if index>-1:    #only works if spell checking is enabled
            print("I am assuming '"+sent[i]+"' should be '"+word.replace('[~]','')+"'.",file=outFile)
        index=word.find('[?]')
        if index>-1:
            print("I do not recognize '"+sent[i]+"'.",file=outFile)
        index=word.find('[!]')
        if index>-1:
            print("I do not recognize '"+sent[i]+"'.",file=outFile)
    

def parseString(s,debug,outFile=sys.stdout):
    sent = Sentence(s)
    if sent.parse():
        linkage = Linkage(0,sent)
        if debug:
            linkage.print_diagram()
        findProblems(linkage, sent, outFile)
        return linkage
    else:
        return None

def parseLinkage(linkage):
    links={}    #dictionary of links to lists of word tuples {linkname:{sublink:[(left,right,domains)]}
    words={}    #dictionary of words to lists of link tuples {word:[(linkname,sublink)]}
    for link in linkage:
        key="".join(char for char in link.label if char.isupper())
        subscript="".join(char for char in link.label if not char.isupper())
        if key in links.keys():
            if subscript in links[key].keys():
                links[key][subscript].append((link.lword,link.rword,link.domain_names))
            else:
                links[key][subscript]=[(link.lword,link.rword,link.domain_names)]
        else:
            links[key]={subscript:[(link.lword,link.rword,link.domain_names)]}
        if link.lword in words.keys():
            words[link.lword].append((key,subscript))
        else:
            words[link.lword]=[(key,subscript)]
        if link.rword in words.keys():
            words[link.rword].append((key,subscript))
        else:
            words[link.rword]=[(key,subscript)]
    del link
    return links,words

def printLinks(links):
    for key,keyGroup in links.items():
        for subkey,subkeyGroup in keyGroup.items():
            for link in subkeyGroup:
                print((key,subkey)+link)

def generateCombinations(links,words,current):
    combinations=dict((key,key) for key in words)
    #TODO: figure out a way to treat the versions that start with "ID"
    #TODO: remove spacer variable
    for name in ('AN','G','TM','TW','TY'): #combine some two-word items together
        if name in links:
            for group in links[name].values():
                for link in group:
                    lkey=link[0]
                    left=combinations[lkey]
                    rkey=link[1]
                    right=combinations[rkey]
                    combination=stripSub(left)+' '+stripSub(right)
                    for key in combinations:
                        if combinations[key]==left or combinations[key]==right:
                            combinations[key]=combination
    for name in ('YP','YS'):    #drop the 's of possessives
        if name in links:
            for group in links[name].values():
                for link in group:
                    for key in combinations:
                        if combinations[key]==combinations[link[1]]:
                            combinations[key]=combinations[link[0]];
    for name in ('NA','NN'):
        if name in links:
            for group in links[name].values():
                for link in group:
                    n1key=link[0]
                    num1=combinations[n1key]
                    n2key=link[1]
                    num2=combinations[n2key]
                    combination=current.number(num1,num2)
                    for key in combinations:
                        if combinations[key]==num1 or combinations[key]==num2:
                            combinations[key]=combination
    if 'ND' in links: #combine number-word
        for group in links['ND'].values():
            for link in group:
                nlink=link[0]
                num=combinations[nlink]
                okey=link[1]
                obj=combinations[okey]
                combination=str(num)+" "+str(obj)
                for key in combinations:
                    if combinations[key]==num or combinations[key]==obj:
                        combinations[key]=combination
    if 'D' in links:    #join determiners to noun
        for group in links['D'].values():
            for link in sorted(group):
                dlink=link[0]
                detr=combinations[dlink]
                nlink=link[1]
                noun=combinations[nlink]
                if all(lName[0]!="M" for lName in words[nlink]):
                    if str(detr) in ('a','an','the'):
                        combination=current.new(detr,noun)
                    elif detectKind(detr)==number:
                        combination=str(detr)+' '+str(noun)#TODO: actually do something
                    else:
                        combination=current.possession(detr,noun)
                    for key in combinations:
                        if combinations[key]==noun or combinations[key]==detr:
                            combinations[key]=combination
    if 'A' in links:    #apply adjectives before the rest of the sentence is parsed
        for group in links['A'].values():
            for link in sorted(group,reverse=True):
                akey=link[0]
                adj=combinations[akey]
                nkey=link[1]
                noun=combinations[nkey]
                combination=current.adjective(adj,noun)
                for key in combinations:
                    if combinations[key]==noun or combinations[key]==detr:
                        combinations[key]=combination
    if 'J' in links: #combine prepositional phrases
        for group in links['J'].values():
            for link in group:
                pkey=link[0]
                prep=combinations[pkey]
                okey=link[1]
                obj=combinations[okey]
                combination=current.prepPhrase(prep,obj)
                for key in combinations:
                    if combinations[key]==prep or combinations[key]==obj:
                        combinations[key]=combination
    if "M" in links:    #apply prep-phrases
        for group in links['M'].values():
            for link in group:
                nkey=link[0]
                noun=combinations[nkey]
                pkey=link[1]
                pPhrase=combinations[pkey]
                combination=current.adjective(pPhrase,noun)
#                pPhrase.modify(noun)
#                pPhrase=str(pPhrase)
#                combination=stripSub(noun)+" "+pPhrase
                for key in combinations:
                    if combinations[key]==noun or combinations[key]==pPhrase:
                        combinations[key]=combination
                
        
    return combinations

def clasifySentence(links):
    if 'Q' in links or 'W' in links and any(char in links['W'] for char in "qsj"):
        return "interrogative"
    elif 'W' in links and 'i' in links['W']:
        return "imperative"
    elif 'W' in links and 'd' in links['W']:
        return "declarative"
    
def parseInterogative(links,words,combinations,current):
    if 'S' in links:
        SV=links['S']
        subject=SV[list(SV.keys())[0]][0][0]
        verb=SV[list(SV.keys())[0]][0][1]
    elif 'SI' in links:
        SV=links['SI']
        subject=SV[list(SV.keys())[0]][0][1]
        verb=SV[list(SV.keys())[0]][0][0]
    elif 'SXI' in links:
        SV=links['SXI']
        subject=SV[list(SV.keys())[0]][0][1]
        verb=SV[list(SV.keys())[0]][0][0]
    verbLinks=words[verb]
    subject=combinations[subject]
    verb=combinations[verb]
    if any(tups[0]=='O' for tups in verbLinks):
        directObject=links['O'][[tups for tups in verbLinks if tups[0]=='O'][0][1]][0][1]
        directObject=combinations[directObject]
        directObject=current[directObject]
    elif any(tups[0]=='P' for tups in verbLinks):
        directObject=links['P'][[tups for tups in verbLinks if tups[0]=='P'][0][1]][0][1]
        directObject=combinations[directObject]
        directObject=current[directObject]
    elif any(tups[0]=='PF' for tups in verbLinks):
        directObject=links['PF'][[tups for tups in verbLinks if tups[0]=='PF'][0][1]][0][0]
        directObject=combinations[directObject]
        directObject=current[directObject]
    elif any(tups[0]=='I' for tups in verbLinks):
        inf=links['I'][[tups for tups in verbLinks if tups[0]=='I'][0][1]][0][1]
        infLinks=words[inf]
        inf=combinations[inf]
        if any(tups[0]=='O' for tups in infLinks):
            directObject=links['O'][[tups for tups in infLinks if tups[0]=='O'][0][1]][0][1]
        elif any(tups[0]=='B' for tups in infLinks):
            directObject=links['B'][[tups for tups in infLinks if tups[0]=='B'][0][1]][0][0]
        directObject=combinations[directObject]
        directObject=infinitive(current,inf,current[directObject])
    return current.verb(subject,verb).ask(directObject)

def parseImperative(links,words,combinations,current):
    subject="you"
    verbLink=links['W']
    verb=verbLink[list(verbLink.keys())[0]][0][1]
    directObject=None
    if any(tups[0]=='O' for tups in words[verb]):
        objectLinks=[tups for tups in words[verb] if tups[0]=='O']
        directObject=links['O'][objectLinks[0][1]][0][1]
        verb=combinations[verb]
        directObject=combinations[directObject]
        directObject=current[directObject]
    elif any(tups[0]== 'P' for tups in words[verb]):
        objectLinks=[tups for tups in words[verb] if tups[0]=='P']
        directObject=links['P'][objectLinks[0][1]][0][1]
        verb=combinations[verb]
        directObject=combinations[directObject]
        directObject=current[directObject]
    elif any(tups[0]=='I' for tups in words[verb]):
        inf=links['I'][[tups for tups in words[verb] if tups[0]=='I'][0][1]][0][1]
        infLinks=words[inf]
        inf=combinations[inf]
        if any(tups[0]=='O' for tups in infLinks):
            directObject=links['O'][[tups for tups in infLinks if tups[0]=='O'][0][1]][0][1]
        directObject=combinations[directObject]
        directObject=infinitive(current,inf,current[directObject])
    return current.verb(subject,verb).act(directObject)

def parseDeclarative(links,words,combinations,current):
    if 'S' in links:
        SV=links['S']
    elif 'SX' in links:
        SV=links['SX']
    subject=SV[list(SV.keys())[0]][0][0]
    verb=SV[list(SV.keys())[0]][0][1]
    verbLinks=words[verb]
    subject=combinations[subject]
    verb=combinations[verb]
    adv=None
    if any(tups[0]=='N' for tups in verbLinks):
        advLinks=[tups for tups in verbLinks if tups[0]=='N']
        adv=links['N'][advLinks[0][1]][0][1]
        adv=combinations[adv]
        adv=adverb(stripSub(adv),current)
    if any(tups[0]=='EB' for tups in verbLinks):
        advLinks=[tups for tups in verbLinks if tups[0]=='EB']
        adv=links['EB'][advLinks[0][1]][0][1]
        adv=combinations[adv]
        adv=adverb(stripSub(adv),current)
    directObject=None
    if any(tups[0]=='O' for tups in verbLinks):
        objectLinks=[tups for tups in verbLinks if tups[0]=='O']
        directObject=links['O'][objectLinks[0][1]][0][1]
        directObject=combinations[directObject]
        directObject=current[directObject]
    elif any(tups[0]== 'P' for tups in verbLinks):
        objectLinks=[tups for tups in verbLinks if tups[0]=='P']
        directObject=links['P'][objectLinks[0][1]][0][1]
        directObject=combinations[directObject]
        directObject=current[directObject]
    elif any(tups[0]=='I' for tups in verbLinks):
        inf=links['I'][[tups for tups in verbLinks if tups[0]=='I'][0][1]][0][1]
        infLinks=words[inf]
        inf=combinations[inf]
        if any(tups[0]=='O' for tups in infLinks):
            directObject=links['O'][[tups for tups in infLinks if tups[0]=='O'][0][1]][0][1]
##      elif any(tups[0]=='B' for tups in infLinks):
##          directObject=links['B'][[tups for tups in infLinks if tups[0]=='B'][0][1]][0][0]
        directObject=combinations[directObject]
        directObject=infinitive(current,inf,current[directObject])
    current.verb(subject,verb)(directObject,adv=adv)

if __name__ == "__main__":
    debug=False  #turn on/off debugging output
    parser=lp() #initialize the parser
    current=conversation(sys.stdout)  #initialize the context
    #talker=festival.open()
    
    while True:
        s=input(">> ")
        words=s.split(' ')
        linkage=parseString(s, debug)
        if linkage:
            links,words=parseLinkage(linkage)
            try:
                if debug:
                    printLinks(links)
                combinations=generateCombinations(links, words,current)
                sentenceType=clasifySentence(links)
                if sentenceType=="interrogative":
                    response=parseInterogative(links, words, combinations,current)
                    print(response)
                    #talker.say(response)
                elif sentenceType=="imperative":
                    response=parseImperative(links, words, combinations,current)
                    print(response)
                    #talker.say(response)
                elif sentenceType=="declarative":
                    parseDeclarative(links, words, combinations,current)
            except KeyError as value:   #conjugate 'be' for argument
                response="What is "+stripSub(value.args[0])+"?"
                print(response)
                #talker.say(response)
                if debug:
                    raise
            except AttributeError as value:
                print(str(value.args[0]))
                #talker.say(str(value.args[0]))
                if debug:
                    raise
            except Exception as value:
                print(str(value.args[0]))
                if debug:
                    raise
        #hereafter are grammatically incorrect commands
        elif 'run' in words:
            print(words)
        elif 'exit' in words:
            print(words)
        elif 'debug' in words:
            debug=not debug
        else:
            print("My responses are limited. Please use precise English")
    # For now explicitly delete the linkage
    del linkage
