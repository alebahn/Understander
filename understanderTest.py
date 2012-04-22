'''
Created on Mar 16, 2011

@author: aaron
'''
from linkgrammar import lp
from understander import parseThrough
from understanding import conversation, number, numberError, time, conjugate, \
    adverb, plural, entity
import datetime
import understander
import unittest

class fakeFile(object):
    def __init__(self,test):
        self.record=[]
        self.test=test
    def write(self,str):
        self.record.append(str)
    def getLast(self):
        if len(self.record)==0:
            self.test.fail("output not written to")
        elif self.record[len(self.record)-1]=="\n":
            return self.record[len(self.record)-2]
        else:
            return self.record[len(self.record)-1]
        #return self.record[len(self.record)-index-1]

class Test(unittest.TestCase):
    parser=lp()
    
    def setUp(self):
        self.debug=False #turn off debugging output
        self.ff=fakeFile(self)
        self.sf=fakeFile(self)
        self.current=conversation(self.ff, "")  #initialize the context
    
    def tearDown(self):
        pass
    
    def testParseThrough(self):
        s="I am happy"
        parseThrough(s,True,self.current,self.ff)
        
        s="have a cake"
        parseThrough(s,True,self.current,self.ff)
        
        s="who are you"
        parseThrough(s,True,self.current,self.ff)
    
    def testBadSentences(self):
        s="I be of are cool"
        linkage=understander.parseString(s, self.debug)
        self.assertIsNone(linkage)
        
#        s="I haeve a cat"
#        linkage=understander.parseString(s, self.debug, file=self.ff)
#        self.assertIsNotNone(linkage)
#        self.assertEqual(self.ff.getLast(), "I do not recognize 'haeve'.")
        
        s="I have several caers"
        linkage=understander.parseString(s, self.debug, file=self.ff)
        self.assertIsNotNone(linkage)
        self.assertEqual(self.ff.getLast(), "I do not recognize 'caers'.")
        
        s="I have cats"
        linkage=understander.parseString(s, self.debug)
        self.assertIsNotNone(linkage)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        self.assertRaises(KeyError,understander.parseDeclarative,links, words, combinations,self.current)
        
        s="screw you"
        linkage=understander.parseString(s, self.debug)
        self.assertIsNotNone(linkage)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        try:
            understander.parseImperative(links, words, combinations,self.current)
            self.fail("no exception raised")
        except AttributeError as e:
            self.assertEqual(e.args[0], "I can not screw.")
        
        s="what is my decl"
        linkage=understander.parseString(s, self.debug, file=self.ff)
        self.assertIsNotNone(linkage)
        self.assertEqual(self.ff.getLast(), "I am assuming 'decl' should be 'deal.n'.")
        links,words=understander.parseLinkage(linkage)
        try:
            understander.generateCombinations(links, words,self.current)
            self.fail("no exception raised")
        except Exception as e:
            self.assertEqual(e.args[0], "You do not have a deal.")
    
    def testClasifySentence(self):
        s="I am happy"
        linkage=understander.parseString(s, self.debug)
        links=understander.parseLinkage(linkage)[0]
        classification=understander.clasifySentence(links)
        self.assertEqual(classification, "declarative")
        
        s="yellow is a color"
        linkage=understander.parseString(s, self.debug, 1)
        links=understander.parseLinkage(linkage)[0]
        classification=understander.clasifySentence(links)
        self.assertEqual(classification, "declarative")
        
        s="eat cake"
        linkage=understander.parseString(s, self.debug)
        links=understander.parseLinkage(linkage)[0]
        classification=understander.clasifySentence(links)
        self.assertEqual(classification, "imperative")
        
        s="who are you"
        linkage=understander.parseString(s, self.debug)
        links=understander.parseLinkage(linkage)[0]
        classification=understander.clasifySentence(links)
        self.assertEqual(classification, "interrogative")
        
        s="how are you"
        linkage=understander.parseString(s, self.debug)
        links=understander.parseLinkage(linkage)[0]
        classification=understander.clasifySentence(links)
        self.assertEqual(classification, "interrogative")
        
        s="are you happy"
        linkage=understander.parseString(s, self.debug)
        links=understander.parseLinkage(linkage)[0]
        classification=understander.clasifySentence(links)
        self.assertEqual(classification, "interrogative")
        
        s="for whom are you working"
        linkage=understander.parseString(s, self.debug)
        links=understander.parseLinkage(linkage)[0]
        classification=understander.clasifySentence(links)
        self.assertEqual(classification, "interrogative")
    
    def testHave(self):
        s="I have a ball"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations,self.current)
        
        self.assertEqual(str(self.current["me"].ball),"a ball")
        self.assertEqual(self.current["me"].ball.possessor,self.current["me"].antecedent)
        
        s="do I have a ball"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertEqual(str(result), "yes")
        
        s="I do not have a ball"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations,self.current)
        
        s="do I have a ball"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertEqual(str(result), "no")
    
    def testPosessions1(self):
        s="what do I have"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertEqual(str(result), "nothing")
        
        s="I have a ball"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations,self.current)
        
        s="what do I have"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertEqual(str(result), "a ball")
        
        s="I have a cat"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations,self.current)
        
        s="what are my possessions"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertIn(str(result), ("a ball and a cat","a cat and a ball"))
        
        s="I have a bat"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations,self.current)
        
        s="what do I have"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertIn(str(result), ("a ball, a cat, and a bat","a cat, a ball, and a bat",
                                    "a bat, a cat, and a ball","a bat, a ball, and a cat",
                                    "a ball, a bat, and a cat","a cat, a bat, and a ball"))
        
    def testImperative(self):
        s="have a ball"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseImperative(links, words, combinations,self.current)
        
        s="do you have a ball"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertEqual(str(result), "yes")
        
        s="do have a cake"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseImperative(links, words, combinations,self.current)
        
        s="do you have a cake"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertEqual(str(result), "yes")
    
    def testNameAndPosessives(self):
        s="I have a cat"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations,self.current)
        
        s="my cat's name is Daisy"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations,self.current)
        
        s="is my cat's name Daisy"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertEqual(str(result), "yes")
        
        s="my cat's name is beautiful"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations,self.current)
        
        s="is my cat's name Daisy"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertEqual(str(result), "yes")
        
        s="is my cat's name beautiful"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertEqual(str(result), "yes")
        
        s="my cat's name is not Daisy"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations,self.current)
        self.assertEqual(self.ff.getLast(), "What is it then?")
        
    def testPossession1(self):
        s="I do not have a cat"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations,self.current)
        self.assertTrue(self.ff.getLast(), "Of course!")
        
        s="I have a cat"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations,self.current)
        
        s="who has my cat"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertEqual(str(result), "you")
        
        s="you have my cat"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations,self.current)
        
        s="who has a cat"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertEqual(str(result), "me")
        
    def testPossession2(self):
        s="I do not have the cat"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations,self.current)
        self.assertTrue(self.ff.getLast(), "Of course!")
        
        s="I have the cat"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations,self.current)
        
        s="do I have the cat"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertEqual(str(result), "yes")
        
        s="I do not have the cat"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations,self.current)
        
        s="do I have the cat"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertEqual(str(result), "no")
        
    def testMultiplePossession1(self):
        s="I have a dog"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations,self.current)
        
        s="I have a dog"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations,self.current)
        self.assertEqual(self.ff.getLast(), "Of course!")
        
#    def testMultiplePossession2(self):
#        s="I have a dog"
#        linkage=understander.parseString(s, self.debug)
#        links,words=understander.parseLinkage(linkage)
#        combinations=understander.generateCombinations(links, words,self.current)
#        understander.parseDeclarative(links, words, combinations,self.current)
#        
#        s="I have a yellow dog"
#        linkage=understander.parseString(s, self.debug)
#        links,words=understander.parseLinkage(linkage)
#        combinations=understander.generateCombinations(links, words,self.current)
#        understander.parseDeclarative(links, words, combinations,self.current)
#        
#        s="what do I have"
#        linkage=understander.parseString(s, self.debug)
#        links,words=understander.parseLinkage(linkage)
#        combinations=understander.generateCombinations(links, words,self.current)
#        result=understander.parseInterogative(links, words, combinations, self.current)
#        self.assertEqual(str(result), "a dog")
#        
#        s="is my dog yellow"
#        linkage=understander.parseString(s, self.debug)
#        links,words=understander.parseLinkage(linkage)
#        combinations=understander.generateCombinations(links, words,self.current)
#        result=understander.parseInterogative(links, words, combinations, self.current)
#        self.assertEqual(str(result), "yes")
    
    def testBe(self):
        s="a cat is an animal"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations,self.current)
        
        s="a cat is an animal"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations,self.current)
        self.assertEqual(self.ff.getLast(), "Of course it is!")
        
        s="a cat is not an animal"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        try:
            understander.parseDeclarative(links, words, combinations,self.current)
            self.fail("exception not raised")
        except Exception as e:
            self.assertEqual(e.args[0], "What is it then?")
        
        s="is a cat an animal"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertEqual(str(result), "yes")
        
        s="what is a cat"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertEqual(str(result), "a cat")
        
        s="I have the cat"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations,self.current)
        
        s="is my cat the cat"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertEqual(str(result), "yes")
        
        s="are you me"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertEqual(str(result), "no")
    
    def testRedefinition1(self):
        s="I have a friend"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations,self.current)
        
        s="a friend is a person"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations,self.current)
        
        s="Bob is a person"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations,self.current)
        
        s="Bob has a dog"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations,self.current)
        
        s="Bob is happy"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations,self.current)
        
        s="my friend is Bob"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations,self.current)
        
        s="does my friend have a dog"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertEqual(str(result), "yes")
        
        s="is my friend happy"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertEqual(str(result), "yes")
    
    def testRedefinition2(self):
        s="I have a friend"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations,self.current)
        
        s="a friend is a person"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations,self.current)
        
        s="Bob is a person"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations,self.current)
        
        s="Bob is my friend"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations,self.current)
        
        s="who has Bob"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertEqual(str(result), "you")
    
    def testRedefinition3(self):
        s="I have a dog"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations,self.current)
        
        s="my dog is the dog"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations,self.current)
        
        s="who has the dog"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertEqual(str(result), "you")
    
    def testEasterEgg(self):
        s="create Vibranium"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        result=understander.parseImperative(links, words, combinations,self.current)
        self.assertEqual(result, "Congratulations sir, you have created a new element.")
    
    def testInheritance1(self):
        s="a cat is an animal"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations,self.current)
        
        s="a cat is a person"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        try:
            understander.parseDeclarative(links, words, combinations,self.current)
            self.fail("Exception not raised")
        except Exception as e:
            self.assertEqual(e.args[0], "How can a cat be a person?")
        
        s="I have a cat"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations,self.current)
        
        s="do I have a cat"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertEqual(str(result), "yes")
        
        s="do I have an animal"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertEqual(str(result), "yes")
        
        s="what is my animal"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertEqual(str(result), "a cat")
        
        s="do I have an entity"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertEqual(str(result), "yes")
    
    def testInheritance2(self):
        s="an admin is a user"
        linkage=understander.parseString(s, self.debug, file=self.ff)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations,self.current)
        
        s="I am an admin"
        linkage=understander.parseString(s, self.debug, file=self.ff)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations,self.current)
        
        s="am I an admin"
        linkage=understander.parseString(s, self.debug, file=self.ff)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertEqual(str(result), "yes")
    
    def testPronouns(self):
        s="I have a cat"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations, self.current)
        
        s="what is it"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertEqual(str(result), "a cat")
        
        s="its name is Daisy"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations, self.current)
        
        self.assertEqual(str(self.current["me"].cat.name), "Daisy")
        
        s="what is its name"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertEqual(str(result), "Daisy")
        
        s="I have a female"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations, self.current)
        
        s="her name is Sally"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations, self.current)
        
        s="what is her name"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertEqual(str(result), "Sally")
        
    def testAdjective1(self):
        s="am I happy"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertEqual(str(result), "no")
        
        s="I am happy"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations, self.current)
        
        self.assertIn("happy",self.current["me"].properties)
        self.assertFalse(list(self.current["me"].properties)[0]==())
        
        s="am I happy"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertEqual(str(result), "yes")
        
        s="I am not happy"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations, self.current)
        
        s="am I happy"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertEqual(str(result), "no")
        
    def testAdjective2(self):
        s="I have a happy dog"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations, self.current)
        
        s="do I have a happy dog"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertEqual(str(result), "yes")
        
        s="is my dog happy"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertEqual(str(result), "yes")
    
    def testAdjective3(self):
        s="I am happy"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations, self.current)
        
        s="am I happy"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertEqual(str(result), "yes")
        
        s="I am sad"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations, self.current)
        
        s="am I happy"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertEqual(str(result), "no")
    
    def testAdjectiverecall(self):
        s="I have a cat"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations, self.current)
        
        s="who has a black cat"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertEqual(str(result), "no one")
        
        s="my cat is black"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations, self.current)
        
        s="who has a black cat"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertEqual(str(result), "you")
    
    def testAdverbEquality(self):
        adv1=adverb("angrily",self.current)
        adv2=adverb("angrily",self.current)
        self.assertTrue(adv1==adv2)
    
    def testPrepOf(self):
        s="I have a dog"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations, self.current)
        
        s="the name of my dog is Max"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations, self.current)
        
        s="what is the name of my dog"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertEqual(str(result), "Max")
        
        s="what is my dog's name"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertEqual(str(result), "Max")
        
    def testLocation(self):
        s="I am at the mall"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations, self.current)
        
        s="where am I"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertEqual(str(result), "the mall")
        
        s="what is my location"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertEqual(str(result), "the mall")
        
    def testTime1(self):
        s="I have an appointment"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations, self.current)
        
        s="my appointment is at ten o'clock"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations, self.current)
        
        s="when is my appointment"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertEqual(str(result), "10:00 AM")
        
        s="what is the time of my appointment"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertEqual(str(result), "10:00 AM")
        
    def testTime2(self):
        s="I have a party"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations, self.current)
        
        s="my party is at five forty-five"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations, self.current)
        
        s="when is my party"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertEqual(str(result), "05:45 AM")
        
    def testTime3(self):
        s="I have an event"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations, self.current)
        
        s="my event is at seven oh nine PM"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations, self.current)
        
        s="when is my event"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertEqual(str(result), "07:09 PM")
    
    def testTime4(self):
        s="I have an event"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations, self.current)
        
        s="my event is at 5:45 PM"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations, self.current)
        
        s="when is my event"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertEqual(str(result), "05:45 PM")
    
    def testTime5(self):
        s="I have an event"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations, self.current)
        
        s="my event is at 5"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations, self.current)
        
        s="when is my event"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertEqual(str(result), "05:00 AM")
        
    def testDate1(self):
        s="I have an event"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations, self.current)
        
        s="my event is on July fifth"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations, self.current)
        
        s="when is my event"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertEqual(str(result), "July 05")
    
    def testDate2(self):
        s="I have an event"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations, self.current)
        
        s="my event is on April 27, 2008"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations, self.current)
        
        s="when is my event"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertEqual(str(result), "April 27, 2008")
    
    def testDateTime1(self):
        s="I have an event"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations, self.current)
        
        s="my event is on February 19, 2011"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations, self.current)
        
        s="my event is at 9:16 AM"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations, self.current)
        
        s="when is my event"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertEqual(str(result), "09:16 AM, on February 19, 2011")
    
    def testDateTime2(self):
        s="I have an event"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations, self.current)
        
        s="my event is at eight"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations, self.current)
        
        s="my event is on November 28, 1998"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations, self.current)
        
        s="when is my event"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertEqual(str(result), "08:00 AM, on November 28, 1998")
    
    def testDateTime1Line(self):
        s="I have an appointment on January first at six forty-five PM"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations, self.current)
        
        s="when is my appointment"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertEqual(str(result), "06:45 PM, on January 01")
    
    def testDateTimeTwoLines(self):
        s="I have an event"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations, self.current)
        
        s="my event is at 6 on December first, twenty thirteen"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations, self.current)
        
        s="when is my event"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertEqual(str(result), "06:00 AM, on December 01, 2013")
    
    def testDeleteTemp(self):
        s="I fall with a dog"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        try:
            understander.parseDeclarative(links, words, combinations, self.current)
            self.fail("test invalid; exception not raised")
        except AttributeError as e:
            pass    #make execution halt unexpectedly
        
        self.current.clearTemp()
        
        self.assertEqual(len(self.current._temp), 0)
    
    def testPlural1(self):
        s="I have a cat"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations, self.current)
        
        s="who has a cat"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertEqual(str(result), "you")
        
        s="who has a dog"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertEqual(str(result), "no one")
    
    def testPlural2(self):
        try:
            plural("numbers",self.current,range(5))
            self.fail("no exception raised")
        except Exception as e:
            self.assertEqual(e.args[0], "not an entity")
    
    def testPlural3(self):
        pl=plural("things",self.current,[entity(str(n),self.current) for n in range(5)])
        self.assertEqual(len(pl), 5)
        
    def testMultiples1(self):
        s="I have five cats"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations, self.current)
        
        s="what do I have"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertEqual(str(result), "five cats")
        
    def testMultiples2(self):
        s="I have one dog"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations, self.current)
        
        s="what do I have"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertEqual(str(result), "one dog")
    
    def testMultiples3(self):
        s="I have five fish"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations, self.current)
        
        s="I have a cat"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations, self.current)
        
        s="what do I have"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertIn(str(result), ("five fish and a cat","a cat and five fish"))
        
        s="I have zero fish"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations, self.current)
        
        s="what do I have"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertEqual(str(result), "a cat")
    
    def testUser(self):
        s="a friend is a user"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations, self.current)
        
        s="I have a friend"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations, self.current)
        
        s="my friend's name is Bob"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations, self.current)
        
        s="is Bob a user"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertEqual(str(result), "yes")
        
        s="who is Bob"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertEqual(str(result), "Bob")
    
    def testComputer(self):
        s="I have a computer"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations, self.current)
        
        s="my computer's name is Hactar"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations, self.current)
        
        s="what is my computer"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertEqual(str(result), "me")
        
    def testHelpingVerb(self):
        s="I do have a cake"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations, self.current)
        
        s="do I have a cake"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertEqual(str(result), "yes")
    
    def testPossessionError(self):
        s="what is my ball"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        try:
            understander.generateCombinations(links, words,self.current)
            self.fail("Attribute error not thrown")
        except AttributeError as e:
            self.assertEqual(e.args[0], "You do not have a ball.")
    
    def testTwoWord(self):
        s="I have a ski jacket"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations, self.current)
        
        s="what do I have"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertEqual(str(result), "a ski jacket")
            
    
    def testColor1(self):
        s="I am yellow"
        linkage=understander.parseString(s, self.debug, 1)
        self.assertIsNotNone(linkage)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations, self.current)
        
        s="am I yellow"
        linkage=understander.parseString(s, self.debug, 1)
        self.assertIsNotNone(linkage)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertEqual(str(result), "yes")
    
    def testColor2(self):
        s="yellow is a color"
        linkage=understander.parseString(s, self.debug,1)
        self.assertIsNotNone(linkage)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations, self.current)
        
        s="I have a yellow dog"
        linkage=understander.parseString(s, self.debug)
        self.assertIsNotNone(linkage)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations, self.current)
        
        s="is my dog yellow"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertEqual(str(result), "yes")
        
        s="what color is my dog"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertEqual(str(result), "yellow")
    
    def testEmotion(self):
        s="happy is an emotion"
        linkage=understander.parseString(s, self.debug)
        self.assertIsNotNone(linkage)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations, self.current)
        
        s="I am happy"
        linkage=understander.parseString(s, self.debug)
        self.assertIsNotNone(linkage)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        understander.parseDeclarative(links, words, combinations, self.current)
        
        s="what emotion am I"
        linkage=understander.parseString(s, self.debug)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertEqual(str(result), "happy")

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()