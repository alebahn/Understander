import locale
import clinkgrammar as clg
import atexit

class lp(object):

	def __init__(self):
		locale.setlocale(locale.LC_ALL,"en_US.UTF8")

		lp.parse_options = ParseOptions()
		lp.dictionary = Dictionary("en")
	
	def __del__(self):
		#print "Deleting",self.__class__
		del lp.parse_options
		del lp.dictionary
	
	@property
	def version(self):
		return clg.linkgrammar_get_version()

class ParseOptions(object):
	def __init__(self):
		self._po = clg.parse_options_create()
	
	def __del__(self):
		#print "Deleting",self.__class__
		if self._po is not None:
			clg.parse_options_delete(self._po)
			self._po = None
	
	def set_verbosity(self,verbosity):
		clg.parse_options_set_verbosity(self._po,verbosity)
	def get_verbosity(self):
		return clg.parse_options_get_verbosity(self._po)
	verbosity = property(get_verbosity,set_verbosity)
	
	def set_linkage_limit(self,linkage_limit):
		clg.parse_options_set_linkage_limit(self._po,linkage_limit)
	def get_linkage_limit(self):
		return clg.parse_options_get_linkage_limit(self._po)
	linkage_limit = property(get_linkage_limit,set_linkage_limit)
	
	def set_disjunct_cost(self,disjunct_cost):
		clg.parse_options_set_disjunct_cost(self._po,disjunct_cost)
	def get_disjunct_cost(self):
		return clg.parse_options_get_disjunct_cost(self._po)
	disjunct_cost = property(get_disjunct_cost,set_disjunct_cost)
	
	def set_min_null_count(self,min_null_count):
		clg.parse_options_set_min_null_count(self._po,min_null_count)
	def get_min_null_count(self):
		return clg.parse_options_get_min_null_count(self._po)
	min_null_count = property(get_min_null_count,set_min_null_count)
	
	def set_max_null_count(self,max_null_count):
		clg.parse_options_set_max_null_count(self._po,max_null_count)
	def get_max_null_count(self):
		return clg.parse_options_get_max_null_count(self._po)
	max_null_count = property(get_max_null_count,set_max_null_count)
	
	def set_null_block(self,null_block):
		clg.parse_options_set_null_block(self._po,null_block)
	def get_null_block(self):
		return clg.parse_options_get_null_block(self._po)
	null_block = property(get_null_block,set_null_block)
	
	def set_short_length(self,short_length):
		clg.parse_options_set_short_length(self._po,short_length)
	def get_short_length(self):
		return clg.parse_options_get_short_length(self._po)
	short_length = property(get_short_length,set_short_length)
	
	def set_islands_ok(self,islands_ok):
		clg.parse_options_set_islands_ok(self._po,islands_ok)
	def get_islands_ok(self):
		return clg.parse_options_get_islands_ok(self._po)
	islands_ok = property(get_islands_ok,set_islands_ok)
	
	def set_max_parse_time(self,secs):
		clg.parse_options_set_max_parse_time(self._po,secs)
	def get_max_parse_time(self):
		return clg.parse_options_get_max_parse_time(self._po)
	max_parse_time = property(get_max_parse_time,set_max_parse_time)
	
	def set_max_memory(self,mem):
		clg.parse_options_set_max_memory(self._po,mem)
	def get_max_memory(self):
		return clg.parse_options_get_max_memory(self._po)
	max_memory = property(get_max_memory,set_max_memory)
	
	def timer_expired(self):
		return clg.parse_options_timer_expired(self._po)
	
	def memory_exhausted(self):
		return clg.parse_options_memory_exhausted(self._po)
	
	def resources_exhausted(self):
		return clg.parse_options_resources_exhausted(self._po)
	
	def reset_resources(self):
		clg.parse_options_reset_resources(self._po)
	
	def set_cost_model_type(self,cm):
		clg.parse_options_set_cost_model_type(self._po,cm)
	def get_cost_model_type(self):
		return clg.parse_options_get_cost_model_type(self._po)
	cost_model_type = property(get_cost_model_type,set_cost_model_type)
	
	def set_screen_width(self,val):
		clg.parse_options_set_screen_width(self._po,val)
	def get_screen_width(self):
		return clg.parse_options_get_screen_width(self._po)
	screen_width = property(get_screen_width,set_screen_width)
	
	def set_allow_null(self,val):
		clg.parse_options_set_allow_null(self._po,val)
	def get_allow_null(self):
		return clg.parse_options_get_allow_null(self._po)
	allow_null = property(get_allow_null,set_allow_null)
	
	def set_display_walls(self,val):
		clg.parse_options_set_display_walls(self._po,val)
	def get_display_walls(self):
		return clg.parse_options_get_display_walls(self._po)
	display_walls = property(get_display_walls,set_display_walls)
	
	def set_all_short_connectors(self,val):
		clg.parse_options_set_all_short_connectors(self._po,val)
	def get_all_short_connectors(self):
		return clg.parse_options_get_all_short_connectors(self._po)
	all_short_connectors = property(get_all_short_connectors,set_all_short_connectors)

class Dictionary(object):
	def __init__(self,lang):
		self._dict = clg.dictionary_create_lang(lang)
	
	def __del__(self):
		#print("Deleting",self.__class__)
		if self._dict is not None:
			clg.dictionary_delete(self._dict)
			self._dict = None
	
	def get_max_cost(self):
		return clg.dictionary_get_max_cost(self._dict)
			
class Sentence(object):
	
	def __init__(self,s):
		self.s = s
		self._sent = clg.sentence_create(s,lp.dictionary._dict)
	
	def __del__(self):
		#print("Deleting",self.__class__)
		if self._sent is not None:
			#clg.sentence_delete(self._sent)
			#print "Calling sentence_delete will cause a segfault"
			self._sent = None
	
	def split(self):
		return clg.sentence_split(self._sent,lp.parse_options._po)
	
	def parse(self):
		self.num_links = clg.sentence_parse(self._sent,lp.parse_options._po)
		return self.num_links
	
	@property
	def length(self):
		return clg.sentence_length(self._sent)
	
	def __len__(self):
		return clg.sentence_length(self._sent)
	
	def get_word(self, w):
		return clg.sentence_get_word(self._sent,w)
	
	def __getitem__(self,key):
		if key<0 or key>=len(self):
			raise IndexError
		return clg.sentence_get_word(self._sent,key)
	
	@property
	def null_count(self):
		return clg.sentence_null_count(self._sent)
	
	#unnecessary
	#@property
	#def num_linkages_found(self):
	#	return clg.sentence_num_linkages_found(self._sent)
	
	@property
	def num_valid_links(self):
		return clg.sentence_num_valid_linkages(self._sent)
	
	@property
	def num_links_post_processed(self):
		return clg.sentence_num_linkages_post_processed(self._sent)
	
	def num_violations(self,i):
		return clg.sentence_num_violations(self._sent,i)
	
	def disjunct_cost(self,i):
		return clg.sentence_disjunct_cost(self._sent,i)
	
	def link_cost(self,i):
		return clg.sentence_link_cost(self._sent,i)
	
	def and_cost(self,i):
		return clg.sentence_and_cost(self._sent,i)
	
	def nth_word_has_disjunction(self,i):
		return clg.sentence_nth_word_has_disjunction(self._sent,i)

class Linkage(object):
	def __init__(self,idx,sentence):
		self.idx = idx
		self.sent = sentence
		self._link = clg.linkage_create(idx,sentence._sent,lp.parse_options._po)
	
	@property
	def num_sublinks(self):
		return clg.linkage_get_num_sublinkages(self._link)
	
	def set_current_sublinkage(self,index):
		return clg.linkage_set_current_sublinkage(self._link,index)
	
	def compute_union(self):
		return clg.linkage_compute_union(self._link)
	
	@property
	def num_words(self):
		return clg.linkage_get_num_words(self._link)
	
	@property
	def num_links(self):
		return clg.linkage_get_num_links(self._link)
	
	def __len__(self):
		return clg.linkage_get_num_links(self._link)
	
	def __getitem__(self,index):
		if index<0 or index>=len(self):
			raise IndexError
		return Link(self,index)
	
	def get_link_length(self,index):
		return clg.linkage_get_link_length(self._link,index)
	
	def get_link_lword(self,index):
		return clg.linkage_get_link_lword(self._link,index)
	
	def get_link_rword(self,index):
		return clg.linkage_get_link_rword(self._link,index)
	
	def print_diagram(self):
		print(clg.linkage_print_diagram(self._link))
	
	@property
	def diagram(self):
		return clg.linkage_print_diagram(self._link)
	
	def print_postscript(self,mode):
		print(clg.linkage_print_postscript(self._link,mode))
	
	def get_postscript(self,mode):
		return clg.linkage_print_postscript(self._link,mode)
	
	def print_links_and_domains(self):
		print(clg.linkage_print_links_and_domains(self._link))
	
	@property
	def links_and_domains(self):
		return clg.linkage_print_links_and_domains(self._link)
	
	def get_link_label(self,index):
		return clg.linkage_get_link_label(self._link,index)
	
	def get_link_llabel(self,index):
		return clg.linkage_get_link_llabel(self._link,index)
	
	def get_link_rlabel(self,index):
		return clg.linkage_get_link_rlabel(self._link,index)
	
	def get_link_num_domains(self,index):
		return clg.linkage_get_link_num_domains(self._link,index)
	
	#needs special extra code to work
	def get_link_domain_names(self,index):
		return list(clg.stringray_getitem(clg.linkage_get_link_domain_names(self._link,index),i) for i in range(self.get_link_num_domains(index)))
	
	@property
	def violation_name(self):
		return clg.linkage_get_violation_name(self._link)
	
	def get_words(self):
		return list(self.get_word(i) for i in range(self.num_words))
	
	def get_word(self,w):
		return clg.linkage_get_word(self._link,w)
	
	#not imported
	#def get_disjunct(self,w):
	#	return clg.linkage_get_disjunct(self._link,w)
	
	def unused_word_cost(self):
		return clg.linkage_unused_word_cost(self._link)
	
	def disjunct_cost(self):
		return clg.linkage_disjunct_cost(self._link)
	
	def and_cost(self):
		return clg.linkage_and_cost(self._link)
	
	def link_cost(self):
		return clg.linkage_link_cost(self._link)
	
	def is_canonical(self):
		return clg.linkage_is_canonical(self._link)
	
	def is_improper(self):
		return clg.linkage_is_improper(self._link)
	
	def has_inconsistent_domains(self):
		return clg.linkage_has_inconsistent_domains(self._link)
	
	def __del__(self):
		#print "Deleting",self.__class__
		if self._link is not None:
			clg.linkage_delete(self._link)
			self._link = None

class Link(object):
	def __init__(self,linkage,index):
		self._linkage=linkage
		self._index=index
	
	@property
	def length(self):
		return self._linkage.get_link_length(self._index)
	
	@property
	def lword(self):
		return Word(self._linkage.get_link_lword(self._index),self._linkage)
	
	@property
	def rword(self):
		return Word(self._linkage.get_link_rword(self._index),self._linkage)
	
	@property
	def label(self):
		return self._linkage.get_link_label(self._index)
	
	@property
	def llabel(self):
		return self._linkage.get_link_llabel(self._index)
	
	@property
	def rlabel(self):
		return self._linkage.get_link_rlabel(self._index)
	
	@property
	def num_domains(self):
		return self._linkage.get_link_num_domains(self._index)
	
	@property
	def domain_names(self):
		return self._linkage.get_link_domain_names(self._index)
	
	def __index__(self):
		return self._index
	
	def __del__(self):
		self._linkage = None

class Word(object):
	def __init__(self,index,linkage):
		self._linkage=linkage
		self._index=index
		self._sentence=linkage.sent
	
	def __eq__(self,other):
		return isinstance(other,Word) and self._index==other._index and str(self)==str(other)
	
	def __ne__(self,other):
		return not self==other
	
	def __gt__(self,other):
		return self._index>other._index
	
	def __lt__(self,other):
		return self._index<other._index
	
	def __ge__(self,other):
		return not self<other
	
	def __le__(self,other):
		return not self>other
	
	def __hash__(self):
		return self._index ^ hash(str(self))
	
	def __str__(self):
		return self._linkage.get_word(self._index).replace('[~]','').replace('[?]','').replace('[!]','')
	
	def __repr__(self):
		return str(self._index)+':'+str(self)
	
	def __index__(self):
		return self._index
	
	def __del__(self):
		self._linkage = None
		self._sentence = None
		

def cleanup():
	pass
	#print("Cleaning up linkgrammar...")

atexit.register(cleanup)


	

