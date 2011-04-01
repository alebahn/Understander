from linkgrammar import Word
import platform
import getpass
import datetime
import math
#import subprocess

#                          Present                                        Past
#     Inf.      Inf/Imp.   I          Sing.       Plural     Part.        I             Sing.         Plural        Part.
conj={"have"  :("have.v"  ,"have.v"  ,"has.v"    ,"have.v"  ,"having.v"  ,"had.v-d"    ,"had.v-d"    ,"had.v-d"    ,"had.v-d"  ),
      "be"    :("be.v"    ,"am.v"    ,"is.v"     ,"are.v"   ,"being.v"   ,"was.v-d"    ,"was.v-d"    ,"were.v-d"   ,"been.v"   ),
      "do"    :("do.v"    ,"do.v"    ,"does.v"   ,"do.v"    ,"doing.v"   ,"did.v-d"    ,"did.v-d"    ,"did.v-d"    ,"done.v"   ),
      "create":("create.v","create.v","creates.v","create.v","creating.v","created.v-d","created.v-d","created.v-d","created.v")}
reverseConj=dict((value,key) for key in conj.keys() for value in set(conj[key]))
for contraction in ("'m","'re","'s"):
    reverseConj[contraction]="be"

#         Sub.       Sub.       Obj.       Det.        Poss.
pronouns={"I"      :("I.p"     ,"me"      ,"my"       ,"mine.p"   ),#Personal
	      "you"    :("you"     ,"you"     ,"your"     ,"yours"    ),
          "he"     :("he"      ,"him"     ,"his"      ,"his"      ),
          "she"    :("she"     ,"her"     ,"her.d"     ,"hers"     ),
          "it"     :("it"      ,"it"      ,"its"      ,None       ),
          "we"     :("we"      ,"us"      ,"our"      ,"ours"     ),
          "they"   :("they"    ,"them"    ,"their"    ,"theirs"   ),
          "that"   :("that.j-p","that.j-p","that.j-d" ,None       ),#Demonstrative
          "this"   :("this.p"  ,"this.p"  ,"this.d"   ,None       ),
          "those"  :("those"   ,"those"   ,"those"    ,None       ),
          "these"  :("these"   ,"these"   ,"these"    ,None       ),
          "who"    :("who"     ,"whom"    ,"whose"    ,"whose"    ),#Interrogative
          "what"   :("what"    ,"what"    ,"which"    ,None       ),
          "where"  :("where"   ,"where"   ,None       ,None       ),
          "when"   :("when"    ,"when"    ,None       ,None       )}
#add Indefinite pronouns (may not be correct. check later
for pronoun in ("another", "each", "either", "enough", "everything", "less", "little", "much", "neither", "nothing", "other", "plenty", "something", "both", "few", "fewer", "many", "others", "several", "all", "any", "more", "none", "some", "such"):
    pronouns[pronoun]=(pronoun,)*3+(None,)
for pronoun in("anybody", "anyone", "anything", "everybody", "everyone", "no one", "nobody", "one", "somebody", "someone"):
    pronouns[pronoun]=(pronoun,)*2+(pronoun+"'s",)*2
reversePronouns=dict((value,key) for key in pronouns.keys() for value in set(pronouns[key]) if value is not None)
questionPronouns=("who","what","where","when")

def createPronoun(name,context):
    assert(name in reversePronouns.keys())
    baseName=reversePronouns[name]
    index=pronouns[baseName].index(name)
    if baseName in ("I","you","he","she","it","we","they"):
        return personal(baseName,context,index)
    elif baseName in ("that","this","those","these"):
        pass
    elif baseName in questionPronouns:
        return question(baseName,context,index)

def stripSub(name): #convert a name to a string and remove the subscript if present
    return str(name).partition('.')[0]

def conjugate(verb,subject): #change the name of a verb for it's subject
    tup=conj[verb]
    if isinstance(subject,plural) or str(subject)=="you":
        return stripSub(tup[3])
    elif str(subject)=="I":
        return stripSub(tup[1])
    else:
        return stripSub(tup[2])

def detectKind(name):   #if possible, determine the type of an object by it's name
    name=str(name)
    if all((word in number.number_words) for word in name.replace('-',' ').split(' ')) or name.isdecimal():
        return number
    elif ":" in name:
        return time
    elif name in questionPronouns:
        return question
    else:
        return entity

class kind(type):   #the type of all entities; keeps track of all of a single kind
    def __init__(cls,name,bases,dict):
        type.__init__(cls,name,bases,dict)
        cls._entities=[]
    def all(self,context):
        return plural("all "+self.__name__,context,self._entities,kind=self)

class verb(object):
    def __init__(self,setter=None,helper=None,asker=None,acter=None):
        self._setter=setter
        self._helper=helper
        self._asker=asker
        self._acter=acter
    class _verber(object):
        def __init__(self,instance,parent):
            self._setter=parent._setter
            self._helper=parent._helper
            self._asker=parent._asker
            self._acter=parent._acter
            self._instance=instance
        def __call__(self,*args,**kargs):
            if any(isinstance(arg,infinitive) for arg in args) or any(isinstance(arg,infinitive) for arg in kargs.values()):
                return self._helper(self._instance,*args,**kargs)
            else:
                return self._setter(self._instance,*args,**kargs)
        def ask(self,*args,**kargs):
            return self._asker(self._instance,*args,**kargs)
        def act(self,*args,**kargs):
            return self._acter(self._instance,*args,**kargs)
    def __get__(self,instance,owner):
        return verb._verber(instance,self)

class interjection(object):
    def __init__(self,name):
        if isinstance(name,bool):
            if name:
                name="yes"
            else:
                name="no"
        self.name=name
    def __str__(self):
        return self.name

class prepositionalPhrase(object):
    def __init__(self,prep,obj,context):
        self.preposition=prep
        if self.preposition=="at":
            if obj in context:
                obj=context[obj]
                objKind=type(obj)
            else:
                objKind=detectKind(obj)
            if objKind==number or objKind==time:
                if objKind==number:
                    self.noun=time(number(obj, context), context)
                else:
                    self.noun=time(obj,context)
                context.add(self.noun,True,obj)
            else:
                self.noun=location(str(obj),context)
        elif self.preposition=="of":
            self.noun=context[obj]
        elif self.preposition=="on":
            if obj in context:
                obj=context[obj]
                objKind=type(obj)
            else:
                objKind=detectKind(obj)
            if objKind==date:
                self.noun=date(obj,context)
                context.add(self.noun,True,obj)
        self.name=name(str(prep)+' '+str(obj),context,self)
        self._current=context
    def modify(self,subj):
        if(self.preposition=="of"):
            subj=stripSub(subj)
            fullName=subj+" "+str(self.name)
            #self._current.add(getattr(self.noun,subj),True,fullName)
            return getattr(self.noun,subj)
        else:
            if(self.preposition=="at"):
                if isinstance(self.noun,time):
                    if "time" in subj.__dict__ and  isinstance(subj.time,date):
                        subj.possessions.remove(subj.time)
                        subj.time=dateTime(subj.time, self.noun,self._current)
                        subj.possessions.add(self.noun)
                    else:
                        subj.possessions.add(self.noun)
                        subj.time=self.noun
                else:
                    subj.possessions.add(self.noun)
                    subj.location=self.noun
            elif(self.preposition=="on"):
                if "time" in subj.__dict__ and  isinstance(subj.time,time):
                    subj.possessions.remove(subj.time)
                    subj.time=dateTime(self.noun,subj.time,self._current)
                    subj.possessions.add(self.noun)
                else:
                    subj.possessions.add(self.noun)
                    subj.time=self.noun
            return subj

class entity(metaclass=kind):
    def __new__(cls,*args,**kargs):
        ent=object.__new__(cls)
        while(cls is not object):
            cls._entities.append(ent)
            cls=cls.__base__
        return ent
    def __init__(self,called,context,decl=0):
        self.name=name(called,context,self)
        self._context=context
        self.possessions=set()
        self.possessor=nothing("no one",context,person)
        self.pronoun=None
        self.decl=decl
        self.properties=set()
    def __setattr__(self,name,value):
        if isinstance(value,pronoun) and  not isinstance(value,question):
            object.__setattr__(self,name,value.antecedent)
        else:
            object.__setattr__(self,name,value)
    def __str__(self):
        return str(self.name)
    def __getattr__(self,name):
        if "possessions" not in self.__dict__:
            raise AttributeError(name)
        for item in self.possessions:
            if isinstance(item,self._context._kinds[name]):
                setattr(self,name,getattr(self,type(item).__name__))
                return getattr(self,name)
        raise AttributeError(str(self).capitalize()+" "+conjugate("do",self)+" not have a "+name+".") #may have incorrect grammar
    def declinate(self,declination):
        self.decl=declination
    @property
    def possessors(self):
        return self.possessor
    def _have_set(self,DO=None,advs=()):
        if "not" not in advs:
            for adv in advs:
                adv.modify(DO)
            self.possessions.add(DO)
            setattr(self,type(DO).__name__,DO)
            if DO!=None:
                if DO.possessor:
                    DO.possessor.possessions.remove(DO)
                    delattr(DO.possessor,type(DO).__name__)
                DO.possessor=self
#                if DO.name.partition(' ')[0] in ('a','an'):
#                    for handle in self._context.names(DO):
#                        del(self._context[handle])
#                    DO.name=name(DO.name.partition(' ')[2],self._context,self)
        else:
            if DO.name.partition(' ')[0] in ('a','an'):
                if any(isinstance(item,type(DO)) for item in self.possessions):
                    for item in [item for item in self.possessions if isinstance(item,type(DO))]:
                        item.possessor=nothing("no one",self._context,person)
                        self.possessions.remove(item)
                    delattr(self,type(DO).__name__)
                else:
                    print("Of course!",file=self._context.outFile)
            else:
                if DO in self.possessions:
                    self.possessions.remove(DO)
                    if getattr(self,type(DO).__name__)==DO:
                        delattr(self,type(DO).__name__)
                else:
                    print("Of course!",file=self._context.outFile)
                if DO!=None:
                    if DO.possessor==self:
                        DO.possessor=nothing("no one",self._context,person)
    def _have_ask(self,DO):
        if DO.name.partition(' ')[0] in ('a','an'):
            return interjection(any(isinstance(item,type(DO)) for item in self.possessions))
        elif isinstance(DO, question):
            return plural("possessions",self._context,list(self.possessions)) #TODO: change name
        else:
            return interjection(DO in self.possessions)
    have=verb(_have_set,asker=_have_ask,acter=_have_set)  #should acter be different?
    def _do_help(self,DO=None,advs=()):
        return getattr(self,DO.verb)(DO.DO,advs=advs)
    def _do_ask(self,DO=None):
        return getattr(self,DO.verb).ask(DO.DO)
    def _do_act(self,DO=None):
        return getattr(self,DO.verb).act(DO.DO)
    do=verb(helper=_do_help,asker=_do_ask,acter=_do_act)
    def _be_set(self,DO=None,advs=()):
        if "not" not in advs:
            for adv in advs:
                adv.modify(self)
            if isinstance(DO,adjective):
                if type(DO).__name__ in self.__dict__:
                    self.properties.remove(getattr(self, type(DO).__name__))
                self.properties.add(DO)
                setattr(self, type(DO).__name__, DO)
            elif isinstance(DO,prepositionalPhrase):
                DO.modify(self)
            elif DO.name.partition(' ')[0] in ('a','an') and not DO.possessor:   #TODO: modify owner's list?
                if issubclass(type(self),type(DO)):
                    print("Of course it is!",file=self._context.outFile)
                elif self.name.partition(' ')[0] in ('a','an') and issubclass(type(DO),type(self).__base__):
                    type(self).__bases__=(type(DO),)
                elif issubclass(type(DO),type(self)):
                    cls=type(DO)
                    while(cls is not type(self)):
                        cls._entities.append(self)
                        cls=cls.__base__
                    self.__class__=type(DO)
                    setattr(self.possessor,type(DO).__name__,self)
                else:
                    raise Exception("How can a "+type(self).__name__+" be "+str(DO.name)+"?")
            else:
                if not DO.possessor:
                    DO.possessor=self.possessor
                for key in DO.__dict__:
                    if key not in ("possessions","properties"):
                        setattr(self,key,getattr(DO,key))
                for item in DO.possessions:
                    self.possessions.add(item)      #TODO: what if both have the same generic object?
                for item in DO.properties:
                    self.properties.add(item)    #TODO: more complexity needed when opposites added
                #if str(DO.name) in self._context._entities:
                for name in self._context.names(DO):
                    self._context._entities[name]=self
                if DO.possessor:
                    setattr(DO.possessor,type(DO).__name__,self)    #do all supertypes
                #check class compatibility and remove from class instance lists
                #raise Exception("WTF Batman!")    #TODO: add more redeffinition stuff
        else:
            if isinstance(DO,adjective):
                if DO in self.properties:
                    self.properties.remove(DO)
            else:
                raise Exception("What is it then?") #TODO: add more undefinition stuff
    def _be_ask(self,DO=None):
        if isinstance(DO,adjective):
            return interjection(DO in self.properties)
        elif isinstance(DO,question):
            if DO.kind==place:
                return self.location
            if DO.kind==time:
                return self.time
        elif DO.name.partition(' ')[0] in ('a','an'):
            return interjection(isinstance(self,type(DO)))
        else:
            return interjection(self == DO)
    be=verb(_be_set,asker=_be_ask,acter=_be_set)
    def _create_act(self,DO):
        if DO.name=="Vibranium":
            return "Congratulations sir, you have created a new element."
    create=verb(acter=_create_act)

class name(entity):
    def __init__(self,name,context,owner):
        self.string=name
        self.name=self
        self._context=context
        self.possessions=[]
        self.possessor=owner
        self.pronoun=None
        self.decl=0
        self.properties=[]
    def __str__(self):
        return self.string
    def __eq__(self,other):
        if isinstance(other,entity):
            return self.string==str(other.name)
        return self.string==str(other)
    def partition(self,sep):
        return self.string.partition(sep)
    def _be_set(self,DO=None,advs=()):
        if advs==():
            if isinstance(DO,adjective):
                self.properties.append(DO)
            else:
                self.string=str(DO.name)
                self.possessor.be(DO)
        if "not" in advs:
            print("What is it then?",file=self._context.outFile)
    def _be_ask(self,DO=None):
        if isinstance(DO,adjective):
            return interjection(DO in self.properties)
        else:
            return interjection(self == DO.name)
    be=verb(_be_set,asker=_be_ask,acter=_be_set)
    def __hash__(self):
        return hash(self.string)

class adjective(entity):
    def __eq__(self,other):
        if isinstance(other,adjective):
            return self.name==other.name
        elif isinstance(other,str) or isinstance(other,name):
            return self.name==other
        else:
            return False
    def _be_set(self,DO,advs=()):
        if advs==():
            if not issubclass(type(DO), adjective):
                type(DO).__bases__=(adjective,)
            self=type(DO)(str(self.name),self._context)
            self._context._adjectives[str(self.name)+".a"]=self
    be=verb(_be_set)
    def __hash__(self):
        return hash(str(self.name))

class adverb(entity):
    def __eq__(self,other):
        if isinstance(other,adverb):
            return self.name==other.name
        elif isinstance(other,str) or isinstance(other,name):
            return self.name==other
        else:
            return False

class person(entity):
    pass

class thing(entity):
    pass

class place(entity):
    pass

class location(place):
    pass

class number(thing):
    ones_place=dict((value,key) for (key,value) in enumerate(["zero","one","two","three","four","five","six","seven","eight","nine","ten","eleven","twelve","thirteen","fourteen","fifteen","sixteen","seventeen","eighteen","nineteen"]))
    ones_place.update(dict((value,key) for (key,value) in enumerate(["oh","first","second","third","fourth","fifth","sixth","seventh","eighth","ninth","tenth","eleventh","twelfth","thirteenth","fourteenth","fifteenth","sixteenth","seventeenth","eighteenth","nineteenth"])))
    tens_place=dict((value,key*10+20) for (key,value) in enumerate(["twenty","thirty","forty","fifty","sixty","seventy","eighty","ninety"]))
    place_marker={"hundred":2,"thousand":3,"million":6,"billion":9,"trillion":12}
    number_words=list(ones_place.keys())+list(tens_place.keys())+list(place_marker.keys())
    rev_ones=["zero","one","two","three","four","five","six","seven","eight","nine","ten","eleven","twelve","thirteen","fourteen","fifteen","sixteen","seventeen","eighteen","nineteen"]
    rev_tens=dict((key+2,value) for (key,value) in enumerate(["twenty","thirty","forty","fifty","sixty","seventy","eighty","ninety"]))
    rev_place={2:"hundred",3:"thousand",6:"million",9:"billion",12:"trillion"}
    def __init__(self,called,context,num1=None,num2=None):
        if called=="a number":
            thing.__init__(self,called,context)
        else:
            if isinstance(called,number):
                self.value=called.value
                self.words=called.words
            elif str(called).isdecimal():
                self.value=(int(str(called)),)
                self.words=self._genWords()
            else:
                if num1==None or num2==None:
                    self.words=tuple(str(called).split('-'))
                elif isinstance(num1, number) and isinstance(num2, number):
                    self.words=num1.words+num2.words
                else:
                    raise numberError()
                self.value=tuple(self.getItems())
            thing.__init__(self,self._toString(),context)
    def getItems(self):
        last=None
        for num in self.words:
            if num in self.ones_place:
                if last==None:
                    last=self.ones_place[num]
                elif self.ones_place[num]==0:
                    yield last
                    last=self.ones_place[num]
                elif self.ones_place[num]>=10 and last%100!=0:
                    yield last
                    last=self.ones_place[num]
                elif last%10!=0 or last==0:
                    yield last
                    last=self.ones_place[num]
                else:
                    last+=self.ones_place[num]
            elif num in self.tens_place:
                if last==None:
                    last=self.tens_place[num]
                elif last%100!=0 or last ==0:
                    yield last
                    last=self.tens_place[num]
                else:
                    last+=self.tens_place[num]
            elif num in self.place_marker:
                if last==None:
                    last=10**self.place_marker[num]
                elif last%(10**self.place_marker[num])==0:
                    if(num=="hundred" and last==0):
                        yield last
                        last=0
                    else:
                        raise numberError()
                else:
                    less=last%(10**self.place_marker[num])
                    greater=last-less
                    last=greater+less*10**self.place_marker[num]
        yield last
    def getNumTuple(self):
        return self.value
    def __int__(self):
        sum=0
        for value in self.value:
            if value==0:
                sum*=10
            else:
                sum=sum*10**(math.floor(math.log10(value))+1)+value
        return sum
    def _genWordsReversed(self):
        num=int(self)
        if(num==0):
            yield "zero"
        place=0
        while(num>0):
            if num%100<20:
                if num%100>0:
                    yield self.rev_ones[num%100]
                num//=100
            else:
                if num%10>0:
                    yield self.rev_ones[num%10]
                num//=10
                if num%10>0:
                    yield self.rev_tens[num%10]
                num//=10
            if num%10>0:
                yield self.rev_place[2]
                yield self.rev_ones[num%10]
            num//=10
            place+=3
            if num%1000>0:
                yield self.rev_place[place]
    def _genWords(self):
        return reversed(tuple(self._genWordsReversed()))
    def _toString(self):
        return " ".join(self._genWords())

class numberError(Exception):
    pass
                

class time(thing):
    time_words={"AM","PM","o'clock"}
    def __init__(self,called,context,sfx=None):
        if isinstance(called,Word):
            called=str(called)
        if isinstance(called,number):
            tup=called.getNumTuple()
            if len(tup)>2 and tup[1]==0:
                tup=tup[:1]+tup[2:]
            if len(tup)==1 and tup[0]>100:
                tup=(tup[0]//100,tup[0]%100)
            self.time=datetime.time(*tup)
        elif isinstance(called,time):
            self.time=called.time
        elif isinstance(called,str):
            self.time=datetime.datetime.strptime(called,"%H:%M").time()
        else:
            raise Exception("Invalid time")
        if sfx=="PM":
            self.time=self.time.replace(self.time.hour+12)
        thing.__init__(self,self._toString(),context)
    def getTime(self):
        return self.time
    def _toString(self):
        return self.time.strftime("%I:%M %p")

class date(thing):
    months=("January","February","March","April","May","June",
            "July","August","September","October","November","December")
    def __init__(self,called,context,part1=None,num=None):
        if called=="a date":
            thing.__init__(self,called,context)
        else:
            if isinstance(called,date):
                self.date=called.date
                self.hasYear=called.hasYear
            elif isinstance(part1,date):
                self.date=part1.date
                self.date=self.date.replace(int(num))
                self.hasYear=True
            elif part1 in self.months:
                self.date=datetime.datetime.strptime(part1+' '+str(int(num)),"%B %d")
                self.hasYear=False
            else:
                raise Exception("Invalid Date")
            thing.__init__(self,self._toString(),context)
    def _toString(self):
        if self.hasYear:
            return self.date.strftime("%B %d, %Y")
        else:
            return self.date.strftime("%B %d")

class dateTime(thing):
    def __init__(self,date,time,context):
        self.datetime=datetime.datetime.combine(date.date,time.time)
        self.hasYear=date.hasYear
        thing.__init__(self,self._toString(),context)
    def _toString(self):
        if self.hasYear:
            return self.datetime.strftime("%I:%M %p, on %B %d, %Y")
        else:
            return self.datetime.strftime("%I:%M %p, on %B %d")

class plural(entity):
    def __new__(cls,name,context,entities,kind=thing):
        if len(entities)==0:
            return nothing(name,context,kind)
        elif len(entities)==1:
            return list(entities)[0]
        else:
            return entity.__new__(cls,name,context,entities,kind)
    def __init__(self,name,context,entities,kind=thing):
        entity.__init__(self,name,context)
        if any(not isinstance(ent,entity) for ent in entities):
            raise Exception("not an entity")
        self._entities=list(entities)
        self.kind=kind
    def __str__(self):  #TODO: declinate
        if len(self._entities)==2:
            return ' and '.join(str(ent) for ent in self._entities)
        else:
            return ', '.join(str(ent) for ent in self._entities[:-1])+", and "+str(self._entities[-1])
    def declinate(self,declination):
        self.decl=declination
        for ent in self._entities:
            ent.declinate(declination)
    def __len__(self):
        return len(self._entities)
    def filter(self,adjs):
        temp=self._entities
        for adj in adjs:
            for index,item in enumerate(temp):
                if adj not in item.properties:
                    del temp[index]
        return plural(str(self.name), self._context, temp, self.kind)
    @property
    def possessors(self):
        return plural(str(self.name)+"'s possessors",self._context,[ent.possessor for ent in self._entities if ent.possessor],kind=person)

class nothing(entity):
    def __init__(self,called,context,kind=thing):
        self.name=name(called,context,self)
        self._context=context
        self.possessions=set()
        if kind is person:
            self.possessor=self
        else:
            self.possessor=nothing("no one",context,person)
        self.pronoun=None
        self.decl=0
        self.properties=set()
        self.kind=kind
    def __str__(self):  #TODO: declinate
        if issubclass(self.kind,person):
            return "no one"  #nobody?
        else:
            return "nothing"
    def __len__(self):
        return 0

class male(person):
    pass

class female(person):
    pass

class computer(person):
    def __init__(self,name,context,isI=False):
        person.__init__(self,name,context)
        self._isI=isI
    def __str__(self):
        if self._isI:
            return stripSub(pronouns["I"][self.decl])
        else:
            return str(self.name)

class user(person):
    def __init__(self,name,context,isYou=False):
        person.__init__(self,name,context)
        self._isYou=isYou
    def __str__(self):
        if self._isYou:
            return stripSub(pronouns["you"][self.decl])
        else:
            return str(self.name)

class infinitive(entity):
    def __init__(self,context,verb,DO=None,IO=None):
        entity.__init__(self,"To",context)
        verb=str(verb)
        if verb in reverseConj.keys():
            verb=reverseConj[verb]
        self.verb=verb
        self.DO=DO
        self.IO=IO

class pronoun(entity):
    def __init__(self,name,context,decl,match,singular):
        entity.__init__(self,name,context,decl)
        self.kind=match
        self.singular=singular
    def __str__(self):
        return str(self.antecedent)
    def __getattribute__(self,name):
        if name in ("decl","kind","singular","antecedent","context"):
            return object.__getattribute__(self,name)
        ##if name == "name" and object.__getattribute__(self,"name") in ("you","I.p"):
        ##    return object.__getattribute__(self,name)
        return getattr(self.antecedent,name)

class personal(pronoun):
    def __init__(self,name,context,decl):
        if name == "it":
            match=thing
        elif name == "they":
            match=plural
        else:
            match=person
        singular = name not in ("you","we","they")
        self.antecedent=context.getAntecedent(name)
        pronoun.__init__(self,name,context,decl,match,singular)

class question(pronoun):
    def __init__(self,name,context,decl,match=None):
        if match==None:
            if name=="who":
                match=person
            elif name=="what":
                match=thing
            elif name=="where":
                match=place
            elif name=="when":
                match=time
        pronoun.__init__(self,name,context,decl,match,True)
        self.antecedent=None
    def __getattribute__(self,name):
        return object.__getattribute__(self,name)
    def _have_ask(self,DO):         #TODO: implement more accurate answer
        if DO.name.partition(' ')[0] in ('a','an') and not DO.possessor:
            alls=type(DO).all(self._context)
            if isinstance(alls,plural):
                alls=alls.filter(DO.properties)
            elif isinstance(alls,nothing):
                return alls
            else:
                if any(adj not in alls.properties for adj in DO.properties):
                    return nothing(alls.name, self._context, self.kind)
            result=alls.possessors
            result.declinate(1)
            return result
        DO.possessor.declinate(1)
        return DO.possessors
    have=verb(asker=_have_ask)
    def _be_ask(self,DO):
        if issubclass(self.kind,adjective):
            return getattr(DO, self.kind.__name__)
        else:
            DO.declinate(1)
            return DO
    be=verb(asker=_be_ask)

class conversation:
    def __init__(self,outFile):
        computerName=platform.node().capitalize()
        userName=getpass.getuser().capitalize()
        self.outFile=outFile
        self._kinds={"kind":kind,"entity":entity,"name":name,"thing":thing,"person":person,
                     "computer":computer,"user":user,"infinitive":infinitive,"pronoun":pronoun,
                     "male":male,"female":female,"place":place,"location":location,"number":number,
                     "time":time}
        self._entities={computerName:computer(computerName,self,True),userName:user(userName,self,True),"Vibranium":thing("Vibranium",self)}
        self._temp={}   #stores 'a/an' objects, possessives, prepositional phrases, and numbers
        self._antecedents={"I":self._entities[userName],"you":self._entities[computerName]}
        self._names={}
        self._adjectives={}
        for key,value in self._entities.items():
            if value in self._names:
                self._names[value].add(key)
            else:
                self._names[value]={key}
    def getAntecedent(self,pronoun):
        return self._antecedents[pronoun]
    def __getitem__(self,index):
        return self.entity(index)
    def __delitem__(self,index):
        if index in self._entities:
            self._names[self._entities[index]].remove(index)
            del(self._entities[index])
        elif stripSub(index) in self._entities:
            self._names[self._entities[index]].remove(stripSub(index))
            del(self._entities[stripSub(index)])
        if index in self._temp:
            self._names[self._temp[index]].remove(index)
            del(self._temp[index])
        elif stripSub(index) in self._temp:
            self._names[self._temp[index]].remove(stripSub(index))
            del(self._temp[stripSub(index)])
        else:
            raise KeyError(index)
    def clearTemp(self):
        keys=set(self._temp.keys())
        for index in keys:
            self._names[self._temp[index]].remove(index)
            del(self._temp[index])
    def __contains__(self,index):
        return index in self._entities.keys() or index in self._kinds.keys() or index in reversePronouns.keys() or index in self._temp.keys()
    def entity(self,name):
        name=str(name)
        if name in self._entities:
            result=self._entities[name]
        elif name in self._temp:
            result=self._temp[name]
            del self[name]
        elif name in reversePronouns.keys():
            return createPronoun(name,self)
        elif stripSub(name) in self._entities:
            result=self._entities[stripSub(name)]
        elif name in self._adjectives:
            result=self._adjectives[name]
        elif len(name.partition('.'))==3 and name.partition('.')[2]=='a':
            result=adjective(stripSub(name),self)
            self._adjectives[name]=result
        elif name.capitalize()==name:
            self.add(person(stripSub(name),self), False, name)
            result=self._entities[name]
        else:
            raise KeyError(name)
        if isinstance(result,female):
            self._antecedents["she"]=result
        elif isinstance(result,person):
            self._antecedents["he"]=result
        elif isinstance(result,plural):
            self._antecedents["they"]=result
        else:
            self._antecedents["it"]=result
        return result
    def names(self,entity):
        return self._names[entity]
    def verb(self,subject,name):
        if isinstance(subject,Word):
            subject=str(subject)
        if isinstance(subject,str):
            subject=self.entity(subject)
        name=str(name)
        if name in reverseConj.keys():
            name=reverseConj[name]
        try:
            return getattr(subject,name)
        except AttributeError:
            raise AttributeError(str(subject).capitalize()+" can not "+stripSub(name)+".") #mayhaps this should raise a different error
    def new(self,detr,type,*args,**kargs):
        type=stripSub(type)
        name=str(detr)+' '+type
        if type in self._kinds:
            self.add(self._kinds[type](name,self,*args,**kargs),str(detr) in ("a","an"),name)
            return name
        else:
            self._kinds[type]=kind(type,(entity,),{})
            self.add(self._kinds[type](name,self,*args,**kargs),str(detr) in ("a","an"),name)
            return name
    def add(self,obj,temp,name):
        if temp:
            if name not in self._temp:
                self._temp[name]=obj
        else:
            if name not in self._entities:
                self._entities[name]=obj
        if obj in self._names:
            self._names[obj].add(name)
        else:
            self._names[obj]={name}
    def possession(self,owner,name):
        owner=str(owner)
        name=stripSub(name)
        fullName=stripSub(owner)+' '+name
        owner=self.entity(owner)
        if fullName not in self._temp:
            temp=getattr(owner,name)
            if not isinstance(temp, entity):
                if isinstance(temp, (set,list,tuple)):
                    temp=plural(fullName,self,temp)
                else:
                    raise Exception("You made an invalid attempt to access non wrapped object of type "+str(type(temp).__name__)+".")
            self.add(temp,True,fullName)
        return fullName
    def question(self,quest,match):
        quest=str(quest)
        match=stripSub(match)
        combination=quest+" "+match
        baseName=reversePronouns[quest]
        index=pronouns[baseName].index(quest)
        quest=question(baseName,self,index,self._kinds[match])
        self.add(quest,True,combination)
        return combination
    def adjective(self,adj,noun):
        noun=stripSub(noun)
        if "." in str(adj) and str(adj).partition(".")[2]=="a":
            adj=stripSub(adj)
            if noun.partition(' ')[0] in ('a','an','the'):
                name=noun.partition(' ')[0]+' '+adj+' '+noun.partition(' ')[2]
            else:
                name=adj+' '+noun
            if noun.partition(' ')[0] in ('a','an'):
                item=self[noun]
                item.be(self[adj+'.a'])
                self.add(item,True,name)
            else:
                item=self[noun]
                if name not in self._entities:
                    del self[noun]
                item.be(self[adj+'.a'])
                self.add(item,True,name)
        else:
            pPhrase=self[adj]
            name=stripSub(noun)+" "+adj
            self.add(pPhrase.modify(noun),True,name)
        return name
    def number(self,num1,num2):
        num1=stripSub(num1)
        num2=stripSub(num2)
        combination=num1+" "+num2
        if num1 in self:
            num1=self.entity(num1)
        else:
            num1=number(num1,self)
        if num2 in self:
            num2=self.entity(num2)
        else:
            num2=number(num2,self)
        self.add(number(combination,self,num1,num2),True,combination)
        return combination
    def monthDay(self,month,day):
        month=stripSub(month)
        day=stripSub(day)
        combination=month+" "+day
        if day in self:
            day=self.entity(day)
        else:
            day=number(day,self)
        self.add(date(combination,self,month,day),True,combination)
        return combination
    def dateYear(self,moDy,year):
        moDy=str(moDy)
        year=stripSub(year)
        combination=moDy+", "+year
        moDy=self.entity(moDy)
        if year in self:
            year=self.entity(year)
        else:
            year=number(year,self)
        self.add(date(combination,self,moDy,year),True,combination)
        return combination
    def numDet(self,num,obj):
        obj=stripSub(obj)
        combination=str(num)+" "+str(obj)
        if str(num) in self:
            num=self.entity(num)
        else:
            if ":" in str(num):
                num=time(num,self)
            else:
                num=number(num,self)
        if obj in time.time_words:
            self.add(time(num,self,obj),True,combination)
        return combination
    def prepPhrase(self,prep,obj):
        prep=stripSub(prep)
        obj=stripSub(obj)
        name=prep+' '+obj
        prepPhrase=prepositionalPhrase(prep,obj,self)
        if name not in self._temp:
            self.add(prepPhrase,True,name)
        else:
            raise Exception('second "' + name + '" not handled')
        return name
