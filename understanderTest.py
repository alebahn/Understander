'''
Created on Mar 16, 2011

@author: aaron
'''
import unittest
from linkgrammar import lp
from understanding import conversation
import understander

class Test(unittest.TestCase):
    def setUp(self):
        self.debug=False #turn off debugging output
        self.parser=lp()   #initialize the parser
        self.current=conversation()  #initialize the context
    
    def tearDown(self):
        pass
    
    def testHave(self):
        s="I have a ball"
        linkage=understander.parseString(s, self.debug)
        self.assertIsNotNone(linkage)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        classification=understander.clasifySentence(links)
        self.assertEqual(classification, "declarative")
        understander.parseDeclarative(links, words, combinations,self.current)
        
        self.assertEqual(str(self.current["me"].ball),"ball")
        self.assertEqual(self.current["me"].ball.possessor,self.current["me"].antecedent)
        
        s="do I have a ball"
        linkage=understander.parseString(s, self.debug)
        self.assertIsNotNone(linkage)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        classification=understander.clasifySentence(links)
        self.assertEqual(classification, "interrogative")
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertEqual(str(result), "yes")
        
    def testImperative(self):
        s="have a ball"
        linkage=understander.parseString(s, self.debug)
        self.assertIsNotNone(linkage)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        classification=understander.clasifySentence(links)
        self.assertEqual(classification, "imperative")
        understander.parseImperative(links, words, combinations,self.current)
        
        s="do you have a ball"
        linkage=understander.parseString(s, self.debug)
        self.assertIsNotNone(linkage)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        classification=understander.clasifySentence(links)
        self.assertEqual(classification, "interrogative")
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertEqual(str(result), "yes")
    
    def testNameAndPosessives(self):
        s="I have a cat"
        linkage=understander.parseString(s, self.debug)
        self.assertIsNotNone(linkage)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        classification=understander.clasifySentence(links)
        self.assertEqual(classification, "declarative")
        understander.parseDeclarative(links, words, combinations,self.current)
        
        s="my cat's name is Daisy"
        linkage=understander.parseString(s, self.debug)
        self.assertIsNotNone(linkage)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        classification=understander.clasifySentence(links)
        self.assertEqual(classification, "declarative")
        understander.parseDeclarative(links, words, combinations,self.current)
        
        s="is my cat's name Daisy"
        linkage=understander.parseString(s, self.debug)
        self.assertIsNotNone(linkage)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        classification=understander.clasifySentence(links)
        self.assertEqual(classification, "interrogative")
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertEqual(str(result), "yes")
    
    def testBe1(self):
        s="a cat is an animal"
        linkage=understander.parseString(s, self.debug)
        self.assertIsNotNone(linkage)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        classification=understander.clasifySentence(links)
        self.assertEqual(classification, "declarative")
        understander.parseDeclarative(links, words, combinations,self.current)
        
        s="is a cat an animal"
        linkage=understander.parseString(s, self.debug)
        self.assertIsNotNone(linkage)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        classification=understander.clasifySentence(links)
        self.assertEqual(classification, "interrogative")
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertEqual(str(result), "yes")
    
    def testInheritance(self):
        s="a cat is an animal"
        linkage=understander.parseString(s, self.debug)
        self.assertIsNotNone(linkage)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        classification=understander.clasifySentence(links)
        self.assertEqual(classification, "declarative")
        understander.parseDeclarative(links, words, combinations,self.current)
        
        s="I have a cat"
        linkage=understander.parseString(s, self.debug)
        self.assertIsNotNone(linkage)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        classification=understander.clasifySentence(links)
        self.assertEqual(classification, "declarative")
        understander.parseDeclarative(links, words, combinations,self.current)
        
        s="do I have a cat"
        linkage=understander.parseString(s, self.debug)
        self.assertIsNotNone(linkage)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        classification=understander.clasifySentence(links)
        self.assertEqual(classification, "interrogative")
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertEqual(str(result), "yes")
        
        s="do I have an animal"
        linkage=understander.parseString(s, self.debug)
        self.assertIsNotNone(linkage)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        classification=understander.clasifySentence(links)
        self.assertEqual(classification, "interrogative")
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertEqual(str(result), "yes")
        
        s="do I have an entity"
        linkage=understander.parseString(s, self.debug)
        self.assertIsNotNone(linkage)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        classification=understander.clasifySentence(links)
        self.assertEqual(classification, "interrogative")
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertEqual(str(result), "yes")
    
    def testPronouns(self):
        s="I have a cat"
        linkage=understander.parseString(s, self.debug)
        self.assertIsNotNone(linkage)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        classification=understander.clasifySentence(links)
        self.assertEqual(classification, "declarative")
        understander.parseDeclarative(links, words, combinations, self.current)
        
        s="its name is Daisy"
        linkage=understander.parseString(s, self.debug)
        self.assertIsNotNone(linkage)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        classification=understander.clasifySentence(links)
        self.assertEqual(classification, "declarative")
        understander.parseDeclarative(links, words, combinations, self.current)
        
        self.assertEqual(str(self.current["me"].cat.name), "Daisy")
        
        s="what is its name"
        linkage=understander.parseString(s, self.debug)
        self.assertIsNotNone(linkage)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        classification=understander.clasifySentence(links)
        self.assertEqual(classification, "interrogative")
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertEqual(str(result), "Daisy")
        
    def testAdjective1(self):
        s="am I happy"
        linkage=understander.parseString(s, self.debug)
        self.assertIsNotNone(linkage)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        classification=understander.clasifySentence(links)
        self.assertEqual(classification, "interrogative")
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertEqual(str(result), "no")
        
        s="I am happy"
        linkage=understander.parseString(s, self.debug)
        self.assertIsNotNone(linkage)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        classification=understander.clasifySentence(links)
        self.assertEqual(classification, "declarative")
        understander.parseDeclarative(links, words, combinations, self.current)
        
        s="am I happy"
        linkage=understander.parseString(s, self.debug)
        self.assertIsNotNone(linkage)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        classification=understander.clasifySentence(links)
        self.assertEqual(classification, "interrogative")
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertEqual(str(result), "yes")
        
    def testAdjective2(self):
        s="I have a happy dog"
        linkage=understander.parseString(s, self.debug)
        self.assertIsNotNone(linkage)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        classification=understander.clasifySentence(links)
        self.assertEqual(classification, "declarative")
        understander.parseDeclarative(links, words, combinations, self.current)
        
        s="do I have a happy dog"
        linkage=understander.parseString(s, self.debug)
        self.assertIsNotNone(linkage)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        classification=understander.clasifySentence(links)
        self.assertEqual(classification, "interrogative")
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertEqual(str(result), "yes")
        
        s="is my dog happy"
        linkage=understander.parseString(s, self.debug)
        self.assertIsNotNone(linkage)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        classification=understander.clasifySentence(links)
        self.assertEqual(classification, "interrogative")
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertEqual(str(result), "yes")
    
    def testPrepOf(self):
        s="I have a dog"
        linkage=understander.parseString(s, self.debug)
        self.assertIsNotNone(linkage)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        classification=understander.clasifySentence(links)
        self.assertEqual(classification, "declarative")
        understander.parseDeclarative(links, words, combinations, self.current)
        
        s="the name of my dog is Max"
        linkage=understander.parseString(s, self.debug)
        self.assertIsNotNone(linkage)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        classification=understander.clasifySentence(links)
        self.assertEqual(classification, "declarative")
        understander.parseDeclarative(links, words, combinations, self.current)
        
        s="what is the name of my dog"
        linkage=understander.parseString(s, self.debug)
        self.assertIsNotNone(linkage)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        classification=understander.clasifySentence(links)
        self.assertEqual(classification, "interrogative")
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertEqual(str(result), "Max")
        
        s="what is my dog's name"
        linkage=understander.parseString(s, self.debug)
        self.assertIsNotNone(linkage)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        classification=understander.clasifySentence(links)
        self.assertEqual(classification, "interrogative")
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertEqual(str(result), "Max")
        
    def testLocation(self):
        s="I am at the mall"
        linkage=understander.parseString(s, self.debug)
        self.assertIsNotNone(linkage)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        classification=understander.clasifySentence(links)
        self.assertEqual(classification, "declarative")
        understander.parseDeclarative(links, words, combinations, self.current)
        
        s="where am I"
        linkage=understander.parseString(s, self.debug)
        self.assertIsNotNone(linkage)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        classification=understander.clasifySentence(links)
        self.assertEqual(classification, "interrogative")
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertEqual(str(result), "the mall")
        
        s="what is my location"
        linkage=understander.parseString(s, self.debug)
        self.assertIsNotNone(linkage)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        classification=understander.clasifySentence(links)
        self.assertEqual(classification, "interrogative")
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertEqual(str(result), "the mall")
        
    def testTime(self):
        s="I have an appointment"
        linkage=understander.parseString(s, self.debug)
        self.assertIsNotNone(linkage)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        classification=understander.clasifySentence(links)
        self.assertEqual(classification, "declarative")
        understander.parseDeclarative(links, words, combinations, self.current)
        
        s="my appointment is at ten o'clock"
        linkage=understander.parseString(s, self.debug)
        self.assertIsNotNone(linkage)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        classification=understander.clasifySentence(links)
        self.assertEqual(classification, "declarative")
        understander.parseDeclarative(links, words, combinations, self.current)
        
        s="when is my appointment"
        linkage=understander.parseString(s, self.debug)
        self.assertIsNotNone(linkage)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        classification=understander.clasifySentence(links)
        self.assertEqual(classification, "interrogative")
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertEqual(str(result), "ten o'clock")
        
        s="what is the time of my appointment"
        linkage=understander.parseString(s, self.debug)
        self.assertIsNotNone(linkage)
        links,words=understander.parseLinkage(linkage)
        combinations=understander.generateCombinations(links, words,self.current)
        classification=understander.clasifySentence(links)
        self.assertEqual(classification, "interrogative")
        result=understander.parseInterogative(links, words, combinations, self.current)
        self.assertEqual(str(result), "ten o'clock")
    
#    def testColor(self):
#        s="I have a yellow dog"
#        linkage=understander.parseString(s, self.debug)
#        self.assertIsNotNone(linkage)
#        links,words=understander.parseLinkage(linkage)
#        combinations=understander.generateCombinations(links, words,self.current)
#        classification=understander.clasifySentence(links)
#        self.assertEqual(classification, "declarative")
#        understander.parseDeclarative(links, words, combinations, self.current)
#        
#        s="what color is my dog"
#        linkage=understander.parseString(s, self.debug)
#        self.assertIsNotNone(linkage)
#        links,words=understander.parseLinkage(linkage)
#        combinations=understander.generateCombinations(links, words,self.current)
#        classification=understander.clasifySentence(links)
#        self.assertEqual(classification, "interrogative")
#        result=understander.parseInterogative(links, words, combinations, self.current)
#        self.assertEqual(str(result), "yellow")

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()