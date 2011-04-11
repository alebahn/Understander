'''
Created on Apr 4, 2011

@author: aaron
'''
import unittest
from understanderTest import fakeFile
from understanding import *


class Test(unittest.TestCase):

    def testCreatePronoun(self):
        ff=fakeFile(self)
        current=conversation(ff)  #initialize the context
        result=createPronoun("me",current)
        self.assertEqual(type(result),personal)
        self.assertEqual(object.__getattribute__(result,"name"), "I")
        self.assertEqual(result.decl, 1)
        
        result=createPronoun("who",current)
        self.assertEqual(type(result),question)
        self.assertEqual(object.__getattribute__(result,"name"), "who")
        self.assertEqual(result.decl, 0)
    
    def testStripSub(self):
        self.assertEqual(stripSub("I.p"),"I")
        self.assertEqual(stripSub("five thousand"),"five thousand")
    
    def testConjuate(self):
        verb=conjugate("be","I")
        self.assertEqual(verb, "am")
        verb=conjugate("be","he")
        self.assertEqual(verb, "is")
        verb=conjugate("be","you")
        self.assertEqual(verb, "are")
        verb=conjugate("do","he")
        self.assertEqual(verb, "does")
    
    def testPluralize(self):
        plural=pluralize("cat")
        self.assertEqual(plural, "cats")
        plural=pluralize("fish")
        self.assertEqual(plural, "fish")
    
    def testUnpluralize(self):
        singular=unpluralize("cows")
        self.assertEqual(singular, "cow")
        singular=unpluralize("aircraft")
        self.assertEqual(singular, "aircraft")
    
    def testDetectKind(self):
        result=detectKind("five hundred fifty-two")
        self.assertEqual(result,number)
        result=detectKind("8:52")
        self.assertEqual(result,time)
        result=detectKind("where")
        self.assertEqual(result,question)
        result=detectKind("bla")
        self.assertEqual(result,entity)
    
    def testKindAll(self):
        ff=fakeFile(self)
        current=conversation(ff)  #initialize the context
        ents=[male(str(i), current) for i in range(10)]
        alls=male.all(current)
        self.assertEqual(type(alls), plural)
        self.assertEqual(len(alls),10)
        for i,ent in enumerate(alls._entities):
            self.assertEqual(ent, ents[i])
    
    def testInterjection(self):
        inter=interjection(True)
        self.assertEqual(inter.name, "yes")
        self.assertEqual(str(inter),"yes")
        inter=interjection(False)
        self.assertEqual(inter.name, "no")
        self.assertEqual(str(inter),"no")
    
    def testPrepositionalPhraseAt(self):
        ff=fakeFile(self)
        current=conversation(ff)  #initialize the context
        pPhrase=prepositionalPhrase("at", "5:30", current)
        subj=entity("ent",current)
        pPhrase.modify(subj)
        self.assertEqual(str(subj.time), "05:30 AM")
        
        pPhrase=prepositionalPhrase("at", "9", current)
        subj=entity("ent",current)
        pPhrase.modify(subj)
        self.assertEqual(str(subj.time), "09:00 AM")
        
        tm=current.numDet("7", "PM")
        pPhrase=prepositionalPhrase("at",tm,current)
        subj=entity("ent2",current)
        pPhrase.modify(subj)
        self.assertEqual(str(subj.time), "07:00 PM")
        
        pPhrase=prepositionalPhrase("at","mall",current)
        subj=entity("ent3",current)
        pPhrase.modify(subj)
        self.assertEqual(str(subj.location), "mall")
        
    
    def testPrepositionalPhraseOf(self):
        ff=fakeFile(self)
        current=conversation(ff)  #initialize the context
        current.new("a", "dog")
        pPhrase=prepositionalPhrase("of", "a dog", current)
        current.add(pPhrase, True,"of a dog")
        name=current.adjective("of a dog", "name")
        self.assertEqual(str(current[name]), "a dog")
    
    def testPrepositionalPhraseOn(self):
        ff=fakeFile(self)
        current=conversation(ff)  #initialize the context
        nd=current.monthDay("December", "first")
        pPhrase=prepositionalPhrase("on", nd, current)
        subj=entity("ent1",current)
        pPhrase.modify(subj)
        self.assertEqual(str(subj.time), "December 01")
    
    def testPrepositionalPhraseAtOn(self):
        ff=fakeFile(self)
        current=conversation(ff)  #initialize the context
        nd=current.monthDay("October", 21)
        pPhrase=prepositionalPhrase("on", nd, current)
        subj=entity("ent1",current)
        pPhrase.modify(subj)
        pPhrase=prepositionalPhrase("at","seven",current)
        pPhrase.modify(subj)
        self.assertEqual(str(subj.time), "07:00 AM, on October 21")
        
        pPhrase=prepositionalPhrase("at","10:47",current)
        subj=entity("ent2",current)
        pPhrase.modify(subj)
        nd=current.monthDay("February","nine")
        pPhrase=prepositionalPhrase("on",nd,current)
        pPhrase.modify(subj)
        self.assertEqual(str(subj.time), "10:47 AM, on February 09")
        
    def testEntityGetAttr(self):
        ff=fakeFile(self)
        current=conversation(ff)  #initialize the context
        animal=current.new("an","animal")
        animal=current[animal]
        dog=current.new("a","dog")
        dog=current[dog]
        dog.be(animal)
        
        me=current["I.p"]
        me.have(dog)
        self.assertEqual(me.animal, me.dog)
        
        try:
            getattr(me, "person")
            self.fail("Exception not raised")
        except AttributeError as e:
            self.assertEqual(e.args[0], "You do not have a person.")
        
        ent=entity("ent", current)
        ent.have(dog)
        del ent.possessions
        try:
            getattr(ent,"animal")
            self.fail("Exception not raised")
        except AttributeError as e:
            self.assertEqual(e.args[0],"animal")
    
    def testDeclinate(self):
        ff=fakeFile(self)
        current=conversation(ff)  #initialize the context
        ent=entity("ent", current)
        ent.declinate(2)
        self.assertEqual(ent.decl, 2)
    
    def testPosessors(self):
        ff=fakeFile(self)
        current=conversation(ff)  #initialize the context
        ent1=entity("ent1", current)
        ent2=entity("ent2", current)
        ent1.have(ent2)
        self.assertEqual(ent2.possessors, ent1)
    
    def testHaveNothing(self):
        ff=fakeFile(self)
        current=conversation(ff)  #initialize the context
        ent=entity("ent", current)
        wanda=person("Wanda", current)
        ent.have(wanda)
        self.assertIn(wanda, ent.possessions)
        ent.have(nothing("no people", current, person))
        self.assertNotIn(wanda, ent.possessions)
    
    def testHavePrepositionModified(self):
        ff=fakeFile(self)
        current=conversation(ff)  #initialize the context
        ent=entity("ent", current)
        apt=entity("apt", current)
        pPhrase=prepositionalPhrase("at","5", current)
        ent.have(apt,(pPhrase,))
        self.assertEqual(str(ent.entity.time), "05:00 AM")
    
    def testHaveAgain(self):
        ff=fakeFile(self)
        current=conversation(ff)  #initialize the context
        ent1=entity("ent1", current)
        ent2=entity("ent2", current)
        ent1.have(ent2)
        ent1.have(ent2)
        self.assertEqual(ff.getLast(), "Of course!")
    
    def testNotHaveGeneric(self):
        ff=fakeFile(self)
        current=conversation(ff)  #initialize the context
        ent=entity("ent", current)
        wanda=person("Wanda", current)
        ent.have(wanda)
        self.assertIn(wanda, ent.possessions)
        ent.have(person("a person", current),(adverb("not",current),))
        self.assertNotIn(wanda, ent.possessions)
    
    def testNotHaveGenericRedundant(self):
        ff=fakeFile(self)
        current=conversation(ff)  #initialize the context
        ent=entity("ent", current)
        ent.have(person("a person", current),(adverb("not",current),))
        self.assertEqual(ff.getLast(), "Of course!")
    
    def testNotHaveSpecific(self):
        ff=fakeFile(self)
        current=conversation(ff)  #initialize the context
        ent=entity("ent", current)
        wanda=person("Wanda", current)
        ent.have(wanda)
        ent.have(wanda,(adverb("not",current),))
        self.assertNotIn(wanda, ent.possessions)
    
    def testNotHaveSpecificRedundant(self):
        ff=fakeFile(self)
        current=conversation(ff)  #initialize the context
        ent=entity("ent", current)
        ent.have(person("Wanda", current),(adverb("not",current),))
        self.assertEqual(ff.getLast(), "Of course!")
    
    def testHaveAskGeneric(self):
        ff=fakeFile(self)
        current=conversation(ff)  #initialize the context
        ent=entity("ent", current)
        bla=thing("bla",current)
        ent.have(bla)
        result=ent.have.ask(thing("a thing",current))
        self.assertEqual(str(result), "yes")
    
    def testHaveAskQuestion(self):
        ff=fakeFile(self)
        current=conversation(ff)  #initialize the context
        ent=entity("ent", current)
        bla=thing("bla",current)
        ent.have(bla)
        result=ent.have.ask(question("what", current, 0, thing))
        self.assertEqual(result, bla)
    
    def testHaveAskSpecific(self):
        ff=fakeFile(self)
        current=conversation(ff)  #initialize the context
        ent=entity("ent", current)
        bla=thing("bla",current)
        ent.have(bla)
        result=ent.have.ask(bla)
        self.assertEqual(str(result), "yes")
    
    def testDoHelp(self):
        ff=fakeFile(self)
        current=conversation(ff)  #initialize the context
        ent=entity("ent", current)
        candy=female("Candy",current)
        inf=infinitive(current, "have", candy)
        ent.do(inf)
        self.assertIn(candy, ent.possessions)
    
    def testDoAsk(self):
        ff=fakeFile(self)
        current=conversation(ff)  #initialize the context
        ent=entity("ent", current)
        candy=female("Candy",current)
        ent.have(candy)
        inf=infinitive(current, "have", candy)
        result=ent.do.ask(inf)
        self.assertEqual(str(result), "yes")
    
    def testDoAct(self):
        ff=fakeFile(self)
        current=conversation(ff)  #initialize the context
        you=current["you"]
        candy=female("Candy",current)
        inf=infinitive(current, "have", candy)
        you.do.act(inf)
        self.assertIn(candy, you.possessions)
    
    def testBePrepPhrases(self):
        ff=fakeFile(self)
        current=conversation(ff)  #initialize the context
        ent=entity("ent", current)
        tm=prepositionalPhrase("at", "6", current)
        dt=current.monthDay("December", "first")
        dt=current.dateYear(dt, "2013")
        dt=prepositionalPhrase("on", dt,current)
        ent.be(tm,(dt,))
        self.assertEqual(str(ent.time), "06:00 AM, on December 01, 2013")
    
    def testBeAdjective(self):
        ff=fakeFile(self)
        current=conversation(ff)  #initialize the context
        ent=entity("ent", current)
        happy=adjective("happy", current)
        ent.be(happy)
        self.assertIn(happy, ent.properties)
    
    def testBeOpposite(self):
        ff=fakeFile(self)
        current=conversation(ff)  #initialize the context
        ent=entity("ent", current)
        happy=adjective("happy", current)
        ent.be(happy)
        self.assertIn(happy, ent.properties)
        sad=adjective("sad", current)
        ent.be(sad)
        self.assertNotIn(happy, ent.properties)
    
    def testBeGenericRedundant(self):
        ff=fakeFile(self)
        current=conversation(ff)  #initialize the context
        genThing=thing("a thing", current)
        genEnt=entity("an entity", current)
        genThing.be(genEnt)
        self.assertEqual(str(ff.getLast()), "Of course it is!")
    
    def tesGenericBeGeneric(self):
        ff=fakeFile(self)
        current=conversation(ff)  #initialize the context
        animal=current.new("an", "animal")
        genThing=thing("a thing", current)
        animal=current[animal]
        animal.be(genThing)
        self.assertTrue(isinstance(current["animal"],thing))
        
    def testNumber(self):
        ff=fakeFile(self)
        current=conversation(ff)  #initialize the context
        self.assertRaises(numberError,number,"five",current,(),())
        
        s="four hundred twenty-five"
        num=self.compileNumber(s,current)
        self.assertEqual(num.getNumTuple(),(425,))
        self.assertEqual(int(num),425)
        self.assertEqual(str(num),"four hundred twenty five")
        
        s="nineteen ninety-two"
        num=self.compileNumber(s,current)
        self.assertEqual(num.getNumTuple(),(19,92))
        self.assertEqual(int(num),1992)
        self.assertEqual(str(num),"one thousand nine hundred ninety two")
        
        s="twenty fifteen"
        num=self.compileNumber(s,current)
        self.assertEqual(num.getNumTuple(),(20,15))
        self.assertEqual(int(num),2015)
        self.assertEqual(str(num),"two thousand fifteen")
        
        s="six thousand nine hundred seventy two"
        num=self.compileNumber(s,current)
        self.assertEqual(num.getNumTuple(),(6972,))
        self.assertEqual(int(num),6972)
        self.assertEqual(str(num),s)
        
        s="two hundred thousand five"
        num=self.compileNumber(s,current)
        self.assertEqual(num.getNumTuple(),(200005,))
        self.assertEqual(int(num),200005)
        self.assertEqual(str(num),"two hundred thousand five")
        
        s="thirty five hundred"
        num=self.compileNumber(s,current)
        self.assertEqual(num.getNumTuple(),(3500,))
        self.assertEqual(int(num),3500)
        self.assertEqual(str(num),"three thousand five hundred")
        
        s="eight six seven five three oh nine"
        num=self.compileNumber(s,current)
        self.assertEqual(num.getNumTuple(),(8,6,7,5,3,0,9))
        self.assertEqual(int(num),8675309)
        self.assertEqual(str(num),"eight million six hundred seventy five thousand three hundred nine")
        
        s="hundred"
        num=self.compileNumber(s,current)
        self.assertEqual(num.getNumTuple(),(100,))
        self.assertEqual(int(num),100)
        self.assertEqual(str(num),"one hundred")
        
        s="nineteen oh one"
        num=self.compileNumber(s,current)
        self.assertEqual(num.getNumTuple(),(19,0,1))
        self.assertEqual(int(num),1901)
        self.assertEqual(str(num),"one thousand nine hundred one")
        
        s="five million hundred"
        self.assertRaises(numberError, self.compileNumber, s, current)
    
    def compileNumber(self,string,current):
        if ' ' in string:
            return number(string,current,number(string.partition(' ')[0],current),self.compileNumber(string.partition(' ')[2],current))
        else:
            return number(string,current)
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()