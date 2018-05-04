from konlpy.tag import Mecab as KoNLPyMecab
from ekonlpy.etag import ExTagger
from ekonlpy.data.tagset import mecab_tags as tagset
from ekonlpy.data.tagset import nouns_tags, stop_tags, sent_tags, topic_tags
from ekonlpy.dictionary import TermDictionary
from ekonlpy.utils import installpath
from ekonlpy.utils import load_dictionary, loadtxt


class Mecab:
    def __init__(self, use_default_dictionary=True, use_phrases=True):
        self._base = KoNLPyMecab()
        self._dictionary = TermDictionary()
        self._loaded_default_dictionary = use_default_dictionary
        if use_default_dictionary:
            self._load_default_dictionary(use_phrases)
        self.extagger = self._load_ext_tagger()
        self.tagset = tagset
        self.nouns_tags = nouns_tags
        self.topic_tags = topic_tags
        self.stop_tags = stop_tags
        self.sent_tags = sent_tags
        self.stopwords = self._load_stopwords()

    def _load_ext_tagger(self):
        return ExTagger(self._dictionary)

    def _load_stopwords(self):
        directory = '%s/data/dictionary/' % installpath
        return loadtxt('%s/STOPWORDS.txt' % directory)

    def _load_default_dictionary(self, use_phrases):
        directory = '%s/data/dictionary/' % installpath
        self._dictionary.add_dictionary(load_dictionary('%s/ECON_TERMS.txt' % directory), 'NNG')
        self._dictionary.add_dictionary(load_dictionary('%s/COUNTRY_LIST.txt' % directory), 'NNG')
        self._dictionary.add_dictionary(load_dictionary('%s/CUST_NAMES.txt' % directory), 'NNP')
        self._dictionary.add_dictionary(load_dictionary('%s/ENTITY_LIST.txt' % directory), 'NNP')
        self._dictionary.add_dictionary(load_dictionary('%s/FINIST_LIST.txt' % directory), 'NNP')
        self._dictionary.add_dictionary(load_dictionary('%s/CUST_ADJS.txt' % directory), 'VA')
        self._dictionary.add_dictionary(load_dictionary('%s/CUST_ADVS.txt' % directory), 'MAG')
        self._dictionary.add_dictionary(load_dictionary('%s/FOREIGN_TERMS.txt' % directory), 'SL')
        if use_phrases:
            self._dictionary.add_dictionary(load_dictionary('%s/PHRASES.txt' % directory), 'NNG')
            self._dictionary.add_dictionary(load_dictionary('%s/ACTION_PHRASES.txt' % directory), 'NNG')
            self._dictionary.add_dictionary(load_dictionary('%s/NAME_PHRASES.txt' % directory), 'NNP')

    def pos(self, phrase):
        tagged = self._base.pos(phrase)
        tagged = self.extagger.pos(tagged)
        return tagged

    def nouns(self, phrase):
        tagged = self.pos(phrase) if type(phrase) == str else phrase
        return [w.lower() for w, t in tagged if t in self.topic_tags and w.lower()]

    def sent_words(self, phrase):
        tagged = self.pos(phrase) if type(phrase) == str else phrase
        return ['{}/{}'.format(w.lower(), t.split('+')[0]) for w, t in tagged
                if t in self.sent_tags and w.lower()]

    def morphs(self, phrase):
        tagged = self.pos(phrase) if type(phrase) == str else phrase
        return [s for s, t in tagged]

    def phrases(self, phrase):
        return self._base.phrases(phrase)

    def add_dictionary(self, words, tag, force=False):
        if (not force) and (not (tag in self.tagset)):
            raise ValueError('%s is not available tag' % tag)
        self._dictionary.add_dictionary(words, tag)

    def load_dictionary(self, fname, tag):
        if not (tag in self.tagset):
            raise ValueError('%s is not available tag' % tag)
        self._dictionary.load_dictionary(fname, tag)
