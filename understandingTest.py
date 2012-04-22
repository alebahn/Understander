'''
Created on Apr 4, 2011

@author: aaron
'''
import unittest
from understanderTest import fakeFile
from understanding import *
import os


class Test(unittest.TestCase):
    
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.ff=fakeFile(self)
        try:
            os.remove("test")
        except:
            pass
        self.current=conversation(self.ff, "test")  #initialize the context

    def testCreatePronoun(self):
        result=createPronoun("me",self.current)
        self.assertEqual(type(result),personal)
        self.assertEqual(object.__getattribute__(result,"name"), "I")
        self.assertEqual(result.decl, 1)
        
        result=createPronoun("who",self.current)
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
        ents=[male(str(i), self.current) for i in range(10)]
        alls=male.all(self.current)
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
        pPhrase=prepositionalPhrase("at", "5:30", self.current)
        subj=entity("ent",self.current)
        pPhrase.modify(subj)
        self.assertEqual(str(subj.time), "05:30 AM")
        
        pPhrase=prepositionalPhrase("at", "9", self.current)
        subj=entity("ent",self.current)
        pPhrase.modify(subj)
        self.assertEqual(str(subj.time), "09:00 AM")
        
        tm=self.current.numDet("7", "PM")
        pPhrase=prepositionalPhrase("at",tm,self.current)
        subj=entity("ent2",self.current)
        pPhrase.modify(subj)
        self.assertEqual(str(subj.time), "07:00 PM")
        
        pPhrase=prepositionalPhrase("at","mall",self.current)
        subj=entity("ent3",self.current)
        pPhrase.modify(subj)
        self.assertEqual(str(subj.location), "mall")
        
    
    def testPrepositionalPhraseOf(self):
        self.current.new("a", "dog")
        pPhrase=prepositionalPhrase("of", "a dog", self.current)
        self.current.add(pPhrase, True,"of a dog")
        name=self.current.adjective("of a dog", "name")
        self.assertEqual(str(self.current[name]), "a dog")
    
    def testPrepositionalPhraseOn(self):
        nd=self.current.monthDay("December", "first")
        pPhrase=prepositionalPhrase("on", nd, self.current)
        subj=entity("ent1",self.current)
        pPhrase.modify(subj)
        self.assertEqual(str(subj.time), "December 01")
    
    def testPrepositionalPhraseAtOn(self):
        nd=self.current.monthDay("October", 21)
        pPhrase=prepositionalPhrase("on", nd, self.current)
        subj=entity("ent1",self.current)
        pPhrase.modify(subj)
        pPhrase=prepositionalPhrase("at","seven",self.current)
        pPhrase.modify(subj)
        self.assertEqual(str(subj.time), "07:00 AM, on October 21")
        
        pPhrase=prepositionalPhrase("at","10:47",self.current)
        subj=entity("ent2",self.current)
        pPhrase.modify(subj)
        nd=self.current.monthDay("February","nine")
        pPhrase=prepositionalPhrase("on",nd,self.current)
        pPhrase.modify(subj)
        self.assertEqual(str(subj.time), "10:47 AM, on February 09")
        
    def testEntityGetAttr(self):
        animal=self.current.new("an","animal")
        animal=self.current[animal]
        dog=self.current.new("a","dog")
        dog=self.current[dog]
        dog.be(animal)
        
        me=self.current["I.p"]
        me.have(dog)
        self.assertEqual(me.animal, me.dog)
        
        try:
            getattr(me, "person")
            self.fail("Exception not raised")
        except AttributeError as e:
            self.assertEqual(e.args[0], "You do not have a person.")
        
        ent=entity("ent", self.current)
        ent.have(dog)
        del ent.possessions
        try:
            getattr(ent,"animal")
            self.fail("Exception not raised")
        except AttributeError as e:
            self.assertEqual(e.args[0],"animal")
    
    def testDeclinate(self):
        ent=entity("ent", self.current)
        ent.declinate(2)
        self.assertEqual(ent.decl, 2)
    
    def testPosessors(self):
        ent1=entity("ent1", self.current)
        ent2=entity("ent2", self.current)
        ent1.have(ent2)
        self.assertEqual(ent2.possessors, ent1)
    
    def testHaveNothing(self):
        ent=entity("ent", self.current)
        wanda=person("Wanda", self.current)
        ent.have(wanda)
        self.assertIn(wanda, ent.possessions)
        ent.have(nothing("no people", self.current, person))
        self.assertNotIn(wanda, ent.possessions)
    
    def testHavePrepositionModified(self):
        ent=entity("ent", self.current)
        apt=entity("apt", self.current)
        pPhrase=prepositionalPhrase("at","5", self.current)
        ent.have(apt,(pPhrase,))
        self.assertEqual(str(ent.entity.time), "05:00 AM")
    
    def testHaveAgain(self):
        ent1=entity("ent1", self.current)
        ent2=entity("ent2", self.current)
        ent1.have(ent2)
        ent1.have(ent2)
        self.assertEqual(self.ff.getLast(), "Of course!")
    
    def testNotHaveGeneric(self):
        ent=entity("ent", self.current)
        wanda=person("Wanda", self.current)
        ent.have(wanda)
        self.assertIn(wanda, ent.possessions)
        ent.have(person("a person", self.current),(adverb("not",self.current),))
        self.assertNotIn(wanda, ent.possessions)
    
    def testNotHaveGenericRedundant(self):
        ent=entity("ent", self.current)
        ent.have(person("a person", self.current),(adverb("not",self.current),))
        self.assertEqual(self.ff.getLast(), "Of course!")
    
    def testNotHaveSpecific(self):
        ent=entity("ent", self.current)
        wanda=person("Wanda", self.current)
        ent.have(wanda)
        ent.have(wanda,(adverb("not",self.current),))
        self.assertNotIn(wanda, ent.possessions)
    
    def testNotHaveSpecificRedundant(self):
        ent=entity("ent", self.current)
        ent.have(person("Wanda", self.current),(adverb("not",self.current),))
        self.assertEqual(self.ff.getLast(), "Of course!")
    
    def testHaveAskGeneric(self):
        ent=entity("ent", self.current)
        bla=thing("bla",self.current)
        ent.have(bla)
        result=ent.have.ask(thing("a thing",self.current))
        self.assertEqual(str(result), "yes")
    
    def testHaveAskQuestion(self):
        ent=entity("ent", self.current)
        bla=thing("bla",self.current)
        ent.have(bla)
        result=ent.have.ask(question("what", self.current, 0, thing))
        self.assertEqual(result, bla)
    
    def testHaveAskSpecific(self):
        ent=entity("ent", self.current)
        bla=thing("bla",self.current)
        ent.have(bla)
        result=ent.have.ask(bla)
        self.assertEqual(str(result), "yes")
    
    def testDoHelp(self):
        ent=entity("ent", self.current)
        candy=female("Candy",self.current)
        inf=infinitive(self.current, "have", candy)
        ent.do(inf)
        self.assertIn(candy, ent.possessions)
    
    def testDoAsk(self):
        ent=entity("ent", self.current)
        candy=female("Candy",self.current)
        ent.have(candy)
        inf=infinitive(self.current, "have", candy)
        result=ent.do.ask(inf)
        self.assertEqual(str(result), "yes")
    
    def testDoAct(self):
        you=self.current["you"]
        candy=female("Candy",self.current)
        inf=infinitive(self.current, "have", candy)
        you.do.act(inf)
        self.assertIn(candy, you.possessions)
    
    def testBePrepPhrases(self):
        ent=entity("ent", self.current)
        tm=prepositionalPhrase("at", "6", self.current)
        dt=self.current.monthDay("December", "first")
        dt=self.current.dateYear(dt, "2013")
        dt=prepositionalPhrase("on", dt,self.current)
        ent.be(tm,(dt,))
        self.assertEqual(str(ent.time), "06:00 AM, on December 01, 2013")
    
    def testBeAdjective(self):
        ent=entity("ent", self.current)
        happy=adjective("happy", self.current)
        ent.be(happy)
        self.assertIn(happy, ent.properties)
    
    def testBeOpposite(self):
        ent=entity("ent", self.current)
        happy=adjective("happy", self.current)
        ent.be(happy)
        self.assertIn(happy, ent.properties)
        sad=adjective("sad", self.current)
        ent.be(sad)
        self.assertNotIn(happy, ent.properties)
    
    def testBeGenericRedundant(self):
        genThing=thing("a thing", self.current)
        genEnt=entity("an entity", self.current)
        genThing.be(genEnt)
        self.assertEqual(str(self.ff.getLast()), "Of course it is!")
    
    def tesGenericBeGeneric(self):
        animal=self.current.new("an", "animal")
        genThing=thing("a thing", self.current)
        animal=self.current[animal]
        animal.be(genThing)
        self.assertTrue(isinstance(self.current["animal"],thing))
    
    def testSpecificBeGeneric(self):
        genEnt=entity("an entity", self.current)
        genThing=thing("a thing", self.current)
        me=self.current["me"]
        me.have(genEnt)
        me.entity.be(genThing)
        self.assertTrue(isinstance(me.entity,thing))
        me.thing    #assert no error thrown
    
    def testIllogicalRetyping(self):
        genFem=female("a female", self.current)
        genThing=thing("a thing", self.current)
        try:
            genFem.be(genThing)
            self.fail("Exception not raised")
        except Exception as e:
            self.assertEqual(e.args[0], "How can a female be a thing?")
    
    def testBe(self):
        I=self.current["me"]
        genFriend=self.current.new("a","friend")
        genFriend=self.current[genFriend]
        I.have(genFriend)
        genFriend=self.current._kinds["friend"]("a friend", self.current)
        genPerson=person("a person", self.current)
        genFriend.be(genPerson)
        Bob=person("Bob", self.current)
        self.current.add(Bob,False,"Bob")
        genThing=thing("a thing", self.current)
        Bob.have(genThing)
        happy=adjective("happy", self.current)
        Bob.be(happy)
        I.friend.be(Bob)
        self.assertIn(happy, Bob.properties)
        self.assertIn(genThing, Bob.possessions)
    
    def testNotBeAdj(self):
        Bob=person("Bob", self.current)
        happy=adjective("happy", self.current)
        Bob.be(happy)
        Bob.be(happy,(adverb("not", self.current),))
    
    def testNotBeEnt(self):
        genThing=thing("a thing", self.current)
        genEnt=entity("an entity", self.current)
        try:
            genThing.be(genEnt,(adverb("not", self.current),))
            self.fail("Exception not raised")
        except Exception as e:
            self.assertEqual(e.args[0],"What is it then?")
    
    def testBeAskAdj(self):
        Larry=person("Larry", self.current)
        happy=adjective("happy", self.current)
        Larry.be(happy)
        result=Larry.be.ask(happy)
        self.assertEqual(str(result), "yes")
    
    def testBeAskQuestionPlace(self):
        daThing=thing("the thing", self.current)
        daPlace=place("the mall", self.current)
        daThing.location=daPlace
        result=daThing.be.ask(question("what place", self.current, 0, place))
        self.assertEqual(result, daPlace)
    
    def testBeAskQuestionTime(self):
        daThing=thing("the thing", self.current)
        daTime=time("5:30", self.current, "PM")
        daThing.time=daTime
        result=daThing.be.ask(question("what time", self.current, 0, time))
        self.assertEqual(result,daTime)
    
    def testBeAskQuestionAdj(self):
        daThing=thing("the thing", self.current)
        genColor=self.current.new("a", "color")
        genColor=self.current[genColor]
        yellow=self.current["yellow.a"]
        yellow.be(genColor)
        yellow=self.current["yellow.a"]
        daThing.be(yellow)
        result=daThing.color
        self.assertEqual(result,yellow)
        result=daThing.be.ask(question("what color",self.current,0,self.current._kinds["color"]))
        self.assertEqual(result,yellow)
    
    def testBeAskGeneric(self):
        genEnt=entity("an entity", self.current)
        genThing=thing("a thing", self.current)
        result=genThing.be.ask(genEnt)
        self.assertEqual(str(result), "yes")
        result=genEnt.be.ask(genThing)
        self.assertEqual(str(result), "no")
    
    def testSpecificBeSpecific(self):
        I=self.current["me"]
        you=self.current["you"]
        result=I.be.ask(you)
        self.assertEqual(str(result), "no")
    
    def testCreateVibranium(self):
        you=self.current["you"]
        result=you.create.act(thing("Vibranium",self.current))
        self.assertEqual(result, "Congratulations sir, you have created a new element.")
    
    def testNameBe(self):
        daThing=thing("the thing", self.current)
        dave=self.current["Dave"]
        daThing.name.be(dave)
        self.assertEqual(str(daThing), "Dave")
    
    def testNameBeAdj(self):
        daThing=thing("the thing", self.current)
        beautiful=adjective("beautiful",self.current)
        daThing.name.be(beautiful)
        self.assertIn(beautiful, daThing.name.properties)
    
    def testNameNotBe(self):
        daThing=thing("the thing", self.current)
        dave=self.current["Dave"]
        daThing.name.be(dave,(adverb("not", self.current),))
        self.assertEqual(self.ff.getLast(), "What is it then?")
    
    def testNameBeAsk(self):
        daThing=thing("the thing", self.current)
        result=daThing.name.be.ask(daThing)
        self.assertEqual(str(result), "yes")
    
    def testNameBeAskAdj(self):
        daThing=thing("the thing", self.current)
        beautiful=adjective("beautiful",self.current)
        daThing.name.be(beautiful)
        result=daThing.name.be.ask(beautiful)
        self.assertEqual(str(result), "yes")
    
    def testAdjEquality(self):
        nice=adjective("nice", self.current)
        niceName=entity("nice", self.current).name
        self.assertEqual(nice, niceName)
        self.assertNotEqual(nice,5)
    
    def testAdvEquality(self):
        fast1=adverb("fast", self.current)
        fast2=adverb("fast", self.current)
        self.assertEqual(fast1, fast2)
        self.assertNotEqual(fast1,5)
    
    def testGenericNumber(self):
        genNum=number("a number", self.current)
        I=self.current["me"]
        I.have(genNum)
        result=I.have.ask(question("what",self.current,thing))
        self.assertEqual(str(result), "a number")
    
    def testNumberFromNumber(self):
        num1=number("five", self.current)
        num2=number(num1, self.current)
        self.assertEqual(str(num2),"five")
        
    def testNumber(self):
        self.assertRaises(numberError,number,"five",self.current,(),())
        
        s="four hundred twenty-five"
        num=self.compileNumber(s,self.current)
        self.assertEqual(num.getNumTuple(),(425,))
        self.assertEqual(int(num),425)
        self.assertEqual(str(num),"four hundred twenty five")
        
        s="nineteen ninety-two"
        num=self.compileNumber(s,self.current)
        self.assertEqual(num.getNumTuple(),(19,92))
        self.assertEqual(int(num),1992)
        self.assertEqual(str(num),"one thousand nine hundred ninety two")
        
        s="twenty fifteen"
        num=self.compileNumber(s,self.current)
        self.assertEqual(num.getNumTuple(),(20,15))
        self.assertEqual(int(num),2015)
        self.assertEqual(str(num),"two thousand fifteen")
        
        s="six thousand nine hundred seventy two"
        num=self.compileNumber(s,self.current)
        self.assertEqual(num.getNumTuple(),(6972,))
        self.assertEqual(int(num),6972)
        self.assertEqual(str(num),s)
        
        s="two hundred thousand five"
        num=self.compileNumber(s,self.current)
        self.assertEqual(num.getNumTuple(),(200005,))
        self.assertEqual(int(num),200005)
        self.assertEqual(str(num),"two hundred thousand five")
        
        s="thirty five hundred"
        num=self.compileNumber(s,self.current)
        self.assertEqual(num.getNumTuple(),(3500,))
        self.assertEqual(int(num),3500)
        self.assertEqual(str(num),"three thousand five hundred")
        
        s="eight six seven five three oh nine"
        num=self.compileNumber(s,self.current)
        self.assertEqual(num.getNumTuple(),(8,6,7,5,3,0,9))
        self.assertEqual(int(num),8675309)
        self.assertEqual(str(num),"eight million six hundred seventy five thousand three hundred nine")
        
        s="hundred"
        num=self.compileNumber(s,self.current)
        self.assertEqual(num.getNumTuple(),(100,))
        self.assertEqual(int(num),100)
        self.assertEqual(str(num),"one hundred")
        
        s="nineteen oh one"
        num=self.compileNumber(s,self.current)
        self.assertEqual(num.getNumTuple(),(19,0,1))
        self.assertEqual(int(num),1901)
        self.assertEqual(str(num),"one thousand nine hundred one")
        
        s="five million hundred"
        self.assertRaises(numberError, self.compileNumber, s, self.current)
    
    def compileNumber(self,string,current):
        if ' ' in string:
            return number(string,current,number(string.partition(' ')[0],current),self.compileNumber(string.partition(' ')[2],current))
        else:
            return number(string,current)
        
    def testTimeConv(self):
        
        s="five thirty"
        num=self.compileNumber(s, self.current)
        timeEnt=time(num,self.current)
        self.assertEqual(timeEnt.getTime(), datetime.time(5,30))
        self.assertEqual(str(timeEnt), "05:30 AM")
        
        s="thirteen hundred"
        num=self.compileNumber(s, self.current)
        timeEnt=time(num,self.current)
        self.assertEqual(timeEnt.getTime(), datetime.time(13,0))
        self.assertEqual(str(timeEnt), "01:00 PM")
        
        s="zero hundred"
        num=self.compileNumber(s, self.current)
        timeEnt=time(num,self.current)
        self.assertEqual(timeEnt.getTime(), datetime.time(0,0))
        self.assertEqual(str(timeEnt), "12:00 AM")
        
        s="1530"
        num=self.compileNumber(s, self.current)
        timeEnt=time(num,self.current)
        self.assertEqual(timeEnt.getTime(), datetime.time(15,30))
        self.assertEqual(str(timeEnt), "03:30 PM")
        
        s="5"
        num=self.compileNumber(s, self.current)
        timeEnt=time(num,self.current)
        self.assertEqual(timeEnt.getTime(), datetime.time(5,0))
        self.assertEqual(str(timeEnt), "05:00 AM")
        
        s="12:32"
        timeEnt=time(s,self.current)
        self.assertEqual(timeEnt.getTime(), datetime.time(12,32))
        self.assertEqual(str(timeEnt), "12:32 PM")
        
        s="seven oh nine"
        num=self.compileNumber(s, self.current)
        timeEnt=time(num,self.current)
        self.assertEqual(timeEnt.getTime(), datetime.time(7,9))
        self.assertEqual(str(timeEnt), "07:09 AM")
        
        s="oh two hundred"
        num=self.compileNumber(s, self.current)
        timeEnt=time(num,self.current)
        self.assertEqual(timeEnt.getTime(), datetime.time(2,0))
        self.assertEqual(str(timeEnt), "02:00 AM")
    
    def testBadTime(self):
        try:
            time(object(), self.current)
            self.fail("Exception not raised")
        except Exception as e:
            self.assertEqual(e.args[0], "Invalid time")
    
    def testGenericDate(self):
        genDate=date("a date", self.current)
        I=self.current["me"]
        I.have(genDate)
        result=I.have.ask(question("what",self.current,thing))
        self.assertEqual(str(result), "a date")
    
    def testBadDate(self):
        try:
            date(object(), self.current)
            self.fail("Exception not raised")
        except Exception as e:
            self.assertEqual(e.args[0], "Invalid date")
    
    def testSingularizeNumberedPlural(self):
        zero=plural("zero things", self.current, number("zero", self.current))
        self.assertEqual(type(zero), nothing)
        
        one=plural("one thing", self.current, number("one", self.current))
        self.assertEqual(type(one), thing)
        
        two=plural("two things", self.current, number("two", self.current))
        self.assertEqual(type(two), plural)
        self.assertEqual(len(two), 2)
    
    def testSingularizePlural(self):
        zero=plural("nothing", self.current, ())
        self.assertEqual(type(zero), nothing)
        
        genThing=thing("a thing", self.current)
        one=plural("a thing", self.current, (genThing,))
        self.assertEqual(one, genThing)
    
    def testPluralOfPlural(self):
        numPl=plural("two things", self.current, number("two", self.current))
        plOfPl=plural("not seen", self.current, (numPl,))
        self.assertEqual(str(plOfPl), "two things")
    
    def testPluralOfNonentity(self):
        try:
            plural("bad plural", self.current, (object(),object()))
            self.fail("Exception not raised")
        except Exception as e:
            self.assertEqual(e.args[0], "not an entity")
    
    def testPluralToString(self):
        pl=plural("ignored", self.current, (person("Bob", self.current), person("Sue", self.current)))
        self.assertEqual(str(pl), "Bob and Sue")
        
        pl=plural("ignored", self.current, (person("Bob", self.current), person("Phill", self.current), person("Andy", self.current)))
        self.assertEqual(str(pl), "Bob, Phill, and Andy")
    
    def testPluralDeclinate(self):
        pl=plural("ignored", self.current, number("five", self.current))
        pl.declinate(2)
        self.assertEqual(pl.decl, 2)
        
        pl=plural("ignored", self.current, (self.current["me"], entity("b", self.current)))
        pl.declinate(2)
        self.assertEqual(str(pl), "your and b")
    
    def testPluralFilter(self):
        happy=adjective("happy",self.current)
        hapTng1=thing("happy thing 1", self.current)
        hapTng1.be(happy)
        hapTng2=thing("happy thing 2", self.current)
        hapTng2.be(happy)
        sadTng1=thing("sad thing 1", self.current)
        sadTng2=thing("sad thing 2", self.current)
        pl=plural("ignored",self.current,(hapTng1,hapTng2,sadTng1,sadTng2))
        pl=pl.filter((happy,))
        self.assertEqual(len(pl._entities), 2)
    
    def testSaveLoad(self):
        globalsBak=globals().copy()
        I=self.current["me"]
        cat=self.current.new("a", "cat")
        cat=self.current[cat]
        I.have(cat)
        kinds=self.current._kinds
        entities=self.current._entities
        names=self.current._names
        adjectives=self.current._adjectives
        self.current.pickle()
        globals().clear()
        globals().update(globalsBak)
        self.current=conversation(self.ff, "test")
        self.assertEqual(kinds, self.current._kinds)
        self.assertEqual(entities.keys(), self.current._entities.keys())
        self.assertTrue(all(name in names.values() for name in self.current._names.values()))
        self.assertEqual(adjectives, self.current._adjectives)
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()