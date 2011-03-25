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

def createPronoun(name,context):
    assert(name in reversePronouns.keys())
    baseName=reversePronouns[name]
    index=pronouns[baseName].index(name)
    if baseName in ("I","you","he","she","it","we","they"):
        return personal(baseName,context,index)
    elif baseName in ("that","this","those","these"):
        pass
    elif baseName in ("who","what","where","when"):
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
    if all((word in number.number_words) for word in name.replace('-',' ').split(' ')):
        return number
    elif any((word in number.number_words) for word in name.replace('-',' ').split(' ')):
        return time
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
        if(self.preposition=="at"):
            objKind=detectKind(obj)
            if objKind==number or objKind==time:
                self.noun=time(obj,context)
            else:
                self.noun=location(str(obj),context)
            context.add(self.noun,False)
        if(self.preposition=="of"):
            self.noun=context[obj]
        self.name=name(str(prep)+' '+str(obj),context,self)
        self._context=context
    def modify(self,subj):
        if(self.preposition=="at"):
            if isinstance(self.noun,time):
                subj.possessions.add(self.noun)
                subj.time=self.noun
            else:
                subj.possessions.add(self.noun)
                subj.location=self.noun
        if(self.preposition=="of"):
            subj=stripSub(subj)
            fullName=subj+" "+str(self.name)
            self._context.add(getattr(self.noun,subj),True,fullName)
    def __str__(self):
        return str(self.name)

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
    def _have_set(self,DO=None,adv=None):
        if adv==None:
            self.possessions.add(DO)
            setattr(self,type(DO).__name__,DO)
            if DO!=None:
                if DO.possessor:
                    DO.possessor.possessions.remove(DO)
                    delattr(DO.possessor,type(DO).__name__)
                DO.possessor=self
                if DO.name.partition(' ')[0] in ('a','an'):
                    del(self._context[DO.name])
                    DO.name=name(DO.name.partition(' ')[2],self._context,self)
        elif adv=="not":
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
    def _do_help(self,DO=None,adv=None):
        return getattr(self,DO.verb)(DO.DO,adv=adv)
    def _do_ask(self,DO=None):
        return getattr(self,DO.verb).ask(DO.DO)
    def _do_act(self,DO=None):
        return getattr(self,DO.verb).act(DO.DO)
    do=verb(helper=_do_help,asker=_do_ask,acter=_do_act)
    def _be_set(self,DO=None,adv=None):
        if adv==None:
            if isinstance(DO,adjective):
                self.properties.add(DO)
            elif isinstance(DO,prepositionalPhrase):
                DO.modify(self)
            elif DO.name.partition(' ')[0] in ('a','an'):   #TODO: modify owner's list?
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
                if str(DO.name) in self._context._entities:
                    self._context._entities[str(DO.name)]=self
                if DO.possessor:
                    setattr(DO.possessor,type(DO).__name__,self)    #do all supertypes
                #check class compatibility and remove from class instance lists
                #raise Exception("WTF Batman!")    #TODO: add more redeffinition stuff
        elif adv=="not":
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
    def _be_set(self,DO=None,adv=None):
        if adv==None:   #TODO: make owner same as new name possessor?
            if isinstance(DO,adjective):
                self.properties.append(DO)
            else:
                self.string=str(DO.name)
        elif adv=="not":
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
    ones_place["oh"]=0
    tens_place=dict((value,key*10+20) for (key,value) in enumerate(["twenty","thirty","forty","fifty","sixty","seventy","eighty","ninety"]))
    place_marker={"hundred":2,"thousand":3,"million":6,"billion":9,"trillion":12}
    number_words=list(ones_place.keys())+list(tens_place.keys())+list(place_marker.keys())
    def __init__(self,called,context,num1=None,num2=None):
        thing.__init__(self,called,context)
        if num1==None or num2==None:
            self.value=tuple(str(called).split('-'))
        elif isinstance(num1, number) and isinstance(num2, number):
            self.value=num1.value+num2.value
        else:
            raise numberError()
        self.getNumTuple() #TODO: check for number error
    def getItems(self):
        last=None
        for num in self.value:
            if num in self.ones_place:
                if last==None:
                    last=self.ones_place[num]
                elif self.ones_place[num]==0:
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
                    raise numberError()
                else:
                    less=last%(10**self.place_marker[num])
                    greater=last-less
                    last=greater+less*10**self.place_marker[num]
        yield last
    def getNumTuple(self):
        return tuple(self.getItems())
    def __int__(self):
        sum=0
        for value in self.getItems():
            if value==0:
                sum*=10
            else:
                sum=sum*10**(math.floor(math.log10(value))+1)+value
        return sum

class numberError(Exception):
    pass
                

class time(thing):
    def __init__(self,called,context):
        thing.__init__(self,str(called),context)
        if isinstance(called,number):
            self.time=datetime.time(*called.getNumTuple())
    def getTime(self):
        return self.time

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
    def __init__(self,name,context,decl):
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
        if DO.name.partition(' ')[0] in ('a','an'):
            alls=type(DO).all(self._context)
            result=alls.possessors
            result.declinate(1)
            return result
        DO.possessor.declinate(1)
        return DO.possessors
    have=verb(asker=_have_ask)
    def _be_ask(self,DO):
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
    def getAntecedent(self,pronoun):
        return self._antecedents[pronoun]
    def __getitem__(self,index):
        return self.entity(index)
    def __delitem__(self,index):
        if index in self._entities:
            del(self._entities[index])
        elif stripSub(index) in self._entities:
            del(self._entities[stripSub(index)])
        else:
            raise KeyError(index)
    def __contains__(self,index):
        return index in self._entities.keys() or index in self._kinds.keys() or index in reversePronouns.keys() or index in self._temp.keys()
    def entity(self,name):
        name=str(name)
        if name in self._entities:
            result=self._entities[name]
        elif name in self._temp:
            result=self._temp[name]
            del self._temp[name]
        elif name in reversePronouns.keys():
            return createPronoun(name,self)
        elif stripSub(name) in self._entities:
            result=self._entities[stripSub(name)]
        elif len(name.partition('.'))==3 and name.partition('.')[2]=='a':
            result=adjective(stripSub(name),self)
        elif name.capitalize()==name:
            self._entities[name]=person(stripSub(name),self)
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
            self.add(self._kinds[type](name,self,*args,**kargs),detr in ("a","an"))
            return name
        else:
            self._kinds[type]=kind(type,(entity,),{})
            self.add(self._kinds[type](name,self,*args,**kargs),detr in ("a","an"))
            return name
    def add(self,obj,temp=True,name=None):
        if name==None:
            name=str(obj)
        if temp:
            if name not in self._temp:
                self._temp[name]=obj
        else:
            if name not in self._entities:
                self._entities[name]=obj
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
            self._temp[fullName]=temp
        return fullName
    def adjective(self,adj,noun):
        adj=stripSub(adj)
        noun=stripSub(noun)
        if noun.partition(' ')[0] in ('a','an','the'):
            name=noun.partition(' ')[0]+' '+adj+' '+noun.partition(' ')[2]
        else:
            name=adj+' '+noun
        if noun.partition(' ')[0] in ('a','an'):
            if name not in self._temp:
                item=self[noun]
                item.be(self[adj+'.a'])
                self._temp[name]=item
        else:
            if name not in self._entities:
                item=self[noun]
                del self[noun]
                item.be(self[adj+'.a'])
                self._entities[name]=item
        return name
    def number(self,num1,num2):
        pass
    def prepPhrase(self,prep,obj):
        prep=stripSub(prep)
        obj=stripSub(obj)
        name=prep+' '+obj
        prepPhrase=prepositionalPhrase(prep,obj,self)
        if name not in self._temp:
            self._temp[name]=prepPhrase
        else:
            raise Exception('second "' + name + '" not handled')
        return name
