# ============================================================================
# shared-utilities/data_science/text_processing_implementations.py - STEMMING & LEMMATIZATION
# ============================================================================
"""
Multiple text processing implementations with stemming and lemmatization
Support for NLTK, spaCy, and custom Hebrew processing
"""

import logging
import re
import string
from typing import List, Dict, Any, Optional, Set
from .text_processing_base import TextProcessorBase, ProcessorFactory

logger = logging.getLogger(__name__)


# ============================================================================
# NLTK Implementation
# ============================================================================

class NLTKTextProcessor(TextProcessorBase):
    """
    NLTK-based text processor with full stemming/lemmatization support
    """

    def __init__(self, language: str = "english"):
        self.language = language
        self.available = False
        self.stemmer = None
        self.lemmatizer = None
        self.stopwords_set = set()
        self._setup_nltk()

    def _setup_nltk(self):
        """Setup NLTK with all required components."""
        try:
            import nltk
            from nltk.stem import PorterStemmer, SnowballStemmer, WordNetLemmatizer
            from nltk.corpus import stopwords, wordnet
            from nltk.tokenize import word_tokenize
            from nltk import pos_tag

            # Download required NLTK data
            required_data = [
                'punkt', 'stopwords', 'wordnet', 'averaged_perceptron_tagger', 'omw-1.4'
            ]

            for data in required_data:
                try:
                    nltk.data.find(f'tokenizers/{data}')
                except LookupError:
                    try:
                        nltk.download(data, quiet=True)
                    except Exception as e:
                        logger.debug(f"Could not download {data}: {e}")

            # Setup components
            self.word_tokenize = word_tokenize
            self.pos_tag = pos_tag

            # Setup stemmers
            if self.language == "english":
                self.stemmer = PorterStemmer()
                self.snowball_stemmer = SnowballStemmer("english")
            else:
                try:
                    self.snowball_stemmer = SnowballStemmer(self.language)
                    self.stemmer = self.snowball_stemmer
                except ValueError:
                    self.stemmer = PorterStemmer()  # Fallback

            # Setup lemmatizer
            self.lemmatizer = WordNetLemmatizer()
            self.wordnet = wordnet

            # Setup stopwords
            try:
                self.stopwords_set = set(stopwords.words(self.language))
            except OSError:
                self.stopwords_set = set(stopwords.words('english'))

            self.available = True
            logger.info(f"NLTK text processor initialized for {self.language}")

        except ImportError:
            logger.warning("NLTK not available")
            self.available = False
        except Exception as e:
            logger.warning(f"NLTK setup failed: {e}")
            self.available = False

    def clean_text(self, text: str, **options) -> str:
        """Clean text with various options."""
        if not text or not isinstance(text, str):
            return ""

        cleaned = text

        # Remove URLs
        if options.get('remove_urls', True):
            cleaned = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '',
                             cleaned)

        # Remove emails
        if options.get('remove_emails', True):
            cleaned = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', cleaned)

        # Remove mentions and hashtags
        if options.get('remove_mentions', True):
            cleaned = re.sub(r'@\w+', '', cleaned)
        if options.get('remove_hashtags', True):
            cleaned = re.sub(r'#\w+', '', cleaned)

        # Remove punctuation
        if options.get('remove_punctuation', True):
            cleaned = cleaned.translate(str.maketrans('', '', string.punctuation))

        # Convert to lowercase
        if options.get('to_lowercase', True):
            cleaned = cleaned.lower()

        # Remove extra whitespace
        if options.get('remove_extra_whitespace', True):
            cleaned = re.sub(r'\s+', ' ', cleaned).strip()

        return cleaned

    def tokenize(self, text: str) -> List[str]:
        """Tokenize text into words."""
        if not self.available:
            return self._basic_tokenize(text)

        try:
            return self.word_tokenize(text)
        except Exception as e:
            logger.error(f"NLTK tokenization failed: {e}")
            return self._basic_tokenize(text)

    def extract_stems(self, text: str) -> List[str]:
        """Extract word stems using Porter/Snowball stemmer."""
        if not self.available or not self.stemmer:
            return self._basic_stems(text)

        try:
            tokens = self.tokenize(text)
            stems = []
            for token in tokens:
                if token.isalpha():  # Only process alphabetic tokens
                    stem = self.stemmer.stem(token.lower())
                    stems.append(stem)
            return stems
        except Exception as e:
            logger.error(f"NLTK stemming failed: {e}")
            return self._basic_stems(text)

    def extract_lemmas(self, text: str) -> List[str]:
        """Extract word lemmas using WordNet lemmatizer."""
        if not self.available or not self.lemmatizer:
            return self._basic_lemmas(text)

        try:
            tokens = self.tokenize(text)
            # Get POS tags for better lemmatization
            pos_tags = self.pos_tag(tokens)

            lemmas = []
            for token, pos in pos_tags:
                if token.isalpha():
                    # Convert POS tag to WordNet format
                    wordnet_pos = self._get_wordnet_pos(pos)
                    lemma = self.lemmatizer.lemmatize(token.lower(), pos=wordnet_pos)
                    lemmas.append(lemma)

            return lemmas
        except Exception as e:
            logger.error(f"NLTK lemmatization failed: {e}")
            return self._basic_lemmas(text)

    def extract_roots(self, text: str) -> List[str]:
        """Extract word roots (combination of stemming and lemmatization)."""
        if not self.available:
            return self._basic_roots(text)

        try:
            # Use both stemming and lemmatization for more comprehensive root extraction
            stems = set(self.extract_stems(text))
            lemmas = set(self.extract_lemmas(text))

            # Combine and deduplicate
            roots = list(stems.union(lemmas))
            return roots
        except Exception as e:
            logger.error(f"NLTK root extraction failed: {e}")
            return self._basic_roots(text)

    def remove_stopwords(self, tokens: List[str], language: str = None) -> List[str]:
        """Remove stopwords from token list."""
        if not tokens:
            return []

        if not self.available:
            return self._basic_stopword_removal(tokens, language)

        try:
            # Use specified language or default
            lang = language or self.language
            if lang != self.language:
                # Try to get stopwords for different language
                try:
                    import nltk
                    stopwords_set = set(nltk.corpus.stopwords.words(lang))
                except:
                    stopwords_set = self.stopwords_set
            else:
                stopwords_set = self.stopwords_set

            return [token for token in tokens if token.lower() not in stopwords_set]
        except Exception as e:
            logger.error(f"NLTK stopword removal failed: {e}")
            return self._basic_stopword_removal(tokens, language)

    def get_supported_languages(self) -> List[str]:
        """Return supported languages for NLTK."""
        if not self.available:
            return ['english']

        try:
            import nltk
            from nltk.corpus import stopwords
            return stopwords.fileids()
        except:
            return ['english', 'spanish', 'french', 'german', 'italian', 'portuguese', 'russian']

    def _get_wordnet_pos(self, treebank_tag: str) -> str:
        """Convert TreeBank POS tag to WordNet POS tag."""
        if not self.available:
            return 'n'  # Default to noun

        if treebank_tag.startswith('J'):
            return self.wordnet.ADJ
        elif treebank_tag.startswith('V'):
            return self.wordnet.VERB
        elif treebank_tag.startswith('N'):
            return self.wordnet.NOUN
        elif treebank_tag.startswith('R'):
            return self.wordnet.ADV
        else:
            return self.wordnet.NOUN  # Default to noun

    def _basic_tokenize(self, text: str) -> List[str]:
        """Basic tokenization fallback."""
        if not text:
            return []
        # Simple word tokenization
        return re.findall(r'\b\w+\b', text.lower())

    def _basic_stems(self, text: str) -> List[str]:
        """Basic stemming fallback."""
        tokens = self._basic_tokenize(text)
        # Simple suffix removal
        stems = []
        for token in tokens:
            if len(token) > 3:
                if token.endswith('ing'):
                    stems.append(token[:-3])
                elif token.endswith('ed'):
                    stems.append(token[:-2])
                elif token.endswith('ly'):
                    stems.append(token[:-2])
                else:
                    stems.append(token)
            else:
                stems.append(token)
        return stems

    def _basic_lemmas(self, text: str) -> List[str]:
        """Basic lemmatization fallback."""
        # For basic implementation, just return cleaned tokens
        return self._basic_tokenize(text)

    def _basic_roots(self, text: str) -> List[str]:
        """Basic root extraction fallback."""
        return list(set(self._basic_stems(text)))

    def _basic_stopword_removal(self, tokens: List[str], language: str = None) -> List[str]:
        """Basic stopword removal fallback."""
        # Basic English stopwords
        basic_stopwords = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'will', 'with', 'i', 'you', 'we', 'they', 'this',
            'but', 'not', 'or', 'have', 'had', 'what', 'when', 'where', 'who'
        }

        if language == 'hebrew':
            basic_stopwords.update({'של', 'את', 'על', 'אל', 'זה', 'זו', 'אני', 'אתה', 'היא', 'הוא'})

        return [token for token in tokens if token.lower() not in basic_stopwords]


# ============================================================================
# spaCy Implementation
# ============================================================================

class SpaCyTextProcessor(TextProcessorBase):
    """
    spaCy-based text processor with advanced NLP capabilities
    """

    def __init__(self, model_name: str = "en_core_web_sm"):
        self.model_name = model_name
        self.nlp = None
        self.available = False
        self._setup_spacy()

    def _setup_spacy(self):
        """Setup spaCy with model."""
        try:
            import spacy
            self.nlp = spacy.load(self.model_name)
            self.available = True
            logger.info(f"spaCy text processor initialized with {self.model_name}")
        except (ImportError, OSError) as e:
            logger.warning(f"spaCy not available: {e}")
            self.available = False

    def clean_text(self, text: str, **options) -> str:
        """Clean text using spaCy preprocessing."""
        if not text or not isinstance(text, str):
            return ""

        if not self.available:
            return self._basic_clean(text, **options)

        try:
            doc = self.nlp(text)

            cleaned_tokens = []
            for token in doc:
                # Skip based on options
                if options.get('remove_punctuation', True) and token.is_punct:
                    continue
                if options.get('remove_space', True) and token.is_space:
                    continue
                if options.get('remove_stopwords', False) and token.is_stop:
                    continue

                # Get token text
                token_text = token.text

                # Apply transformations
                if options.get('to_lowercase', True):
                    token_text = token_text.lower()

                cleaned_tokens.append(token_text)

            return ' '.join(cleaned_tokens)

        except Exception as e:
            logger.error(f"spaCy cleaning failed: {e}")
            return self._basic_clean(text, **options)

    def tokenize(self, text: str) -> List[str]:
        """Tokenize text using spaCy."""
        if not self.available:
            return self._basic_tokenize(text)

        try:
            doc = self.nlp(text)
            return [token.text for token in doc if not token.is_space]
        except Exception as e:
            logger.error(f"spaCy tokenization failed: {e}")
            return self._basic_tokenize(text)

    def extract_stems(self, text: str) -> List[str]:
        """Extract stems (spaCy doesn't have built-in stemming, use lemmas)."""
        if not self.available:
            return self._basic_stems(text)

        # spaCy doesn't have stemming, so we'll use lemmatization as approximation
        return self.extract_lemmas(text)

    def extract_lemmas(self, text: str) -> List[str]:
        """Extract lemmas using spaCy."""
        if not self.available:
            return self._basic_lemmas(text)

        try:
            doc = self.nlp(text)
            lemmas = []
            for token in doc:
                if token.is_alpha and not token.is_stop:  # Only alphabetic, non-stopword tokens
                    lemmas.append(token.lemma_.lower())
            return lemmas
        except Exception as e:
            logger.error(f"spaCy lemmatization failed: {e}")
            return self._basic_lemmas(text)

    def extract_roots(self, text: str) -> List[str]:
        """Extract word roots using spaCy lemmatization."""
        if not self.available:
            return self._basic_roots(text)

        try:
            doc = self.nlp(text)
            roots = []
            for token in doc:
                if token.is_alpha and not token.is_stop:
                    # Use lemma as root
                    root = token.lemma_.lower()
                    # Additional root extraction for compound words
                    if '-' in token.text:
                        # Handle hyphenated words
                        parts = token.text.split('-')
                        for part in parts:
                            if len(part) > 2:
                                part_doc = self.nlp(part)
                                for part_token in part_doc:
                                    if part_token.is_alpha:
                                        roots.append(part_token.lemma_.lower())
                    else:
                        roots.append(root)

            return list(set(roots))  # Remove duplicates
        except Exception as e:
            logger.error(f"spaCy root extraction failed: {e}")
            return self._basic_roots(text)

    def remove_stopwords(self, tokens: List[str], language: str = None) -> List[str]:
        """Remove stopwords using spaCy."""
        if not self.available:
            return self._basic_stopword_removal(tokens, language)

        try:
            # Process tokens through spaCy to identify stopwords
            text = ' '.join(tokens)
            doc = self.nlp(text)
            return [token.text for token in doc if not token.is_stop and token.is_alpha]
        except Exception as e:
            logger.error(f"spaCy stopword removal failed: {e}")
            return self._basic_stopword_removal(tokens, language)

    def get_supported_languages(self) -> List[str]:
        """Return supported languages for spaCy."""
        model_languages = {
            'en_core_web_sm': ['en', 'english'],
            'en_core_web_md': ['en', 'english'],
            'en_core_web_lg': ['en', 'english'],
            'de_core_news_sm': ['de', 'german'],
            'fr_core_news_sm': ['fr', 'french'],
            'es_core_news_sm': ['es', 'spanish'],
            'it_core_news_sm': ['it', 'italian'],
            'pt_core_news_sm': ['pt', 'portuguese'],
            'ru_core_news_sm': ['ru', 'russian'],
            'zh_core_web_sm': ['zh', 'chinese']
        }
        return model_languages.get(self.model_name, ['en'])

    def _basic_clean(self, text: str, **options) -> str:
        """Basic cleaning fallback."""
        cleaned = text
        if options.get('remove_punctuation', True):
            cleaned = cleaned.translate(str.maketrans('', '', string.punctuation))
        if options.get('to_lowercase', True):
            cleaned = cleaned.lower()
        if options.get('remove_extra_whitespace', True):
            cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return cleaned

    def _basic_tokenize(self, text: str) -> List[str]:
        """Basic tokenization fallback."""
        return re.findall(r'\b\w+\b', text.lower())

    def _basic_stems(self, text: str) -> List[str]:
        """Basic stemming fallback."""
        tokens = self._basic_tokenize(text)
        stems = []
        for token in tokens:
            if len(token) > 3:
                if token.endswith('ing'):
                    stems.append(token[:-3])
                elif token.endswith('ed'):
                    stems.append(token[:-2])
                else:
                    stems.append(token)
            else:
                stems.append(token)
        return stems

    def _basic_lemmas(self, text: str) -> List[str]:
        """Basic lemmatization fallback."""
        return self._basic_tokenize(text)

    def _basic_roots(self, text: str) -> List[str]:
        """Basic root extraction fallback."""
        return list(set(self._basic_stems(text)))

    def _basic_stopword_removal(self, tokens: List[str], language: str = None) -> List[str]:
        """Basic stopword removal fallback."""
        basic_stopwords = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'will', 'with'
        }
        return [token for token in tokens if token.lower() not in basic_stopwords]


# ============================================================================
# Hebrew Text Processor
# ============================================================================

class HebrewTextProcessor(TextProcessorBase):
    """
    Hebrew text processor with custom stemming and root extraction
    """

    def __init__(self):
        self.available = True

        # Hebrew prefixes (common prefixes in Hebrew)
        self.prefixes = {'ו', 'ב', 'ל', 'מ', 'ה', 'כ', 'ש'}

        # Hebrew suffixes
        self.suffixes = {'ים', 'ות', 'יה', 'ון', 'ית', 'י', 'ה', 'ת', 'ך', 'נו', 'כם', 'הן'}

        # Hebrew stopwords
        self.hebrew_stopwords = {
            'של', 'את', 'על', 'אל', 'זה', 'זו', 'זאת', 'אני', 'אתה', 'אתם', 'אתן',
            'היא', 'הוא', 'הם', 'הן', 'אנחנו', 'אנו', 'יש', 'אין', 'היה', 'היתה',
            'היו', 'הייתי', 'הייתה', 'היינו', 'הייתם', 'גם', 'כל', 'כמו', 'או',
            'אבל', 'רק', 'עוד', 'פה', 'שם', 'כאן', 'שלא', 'לא', 'עם', 'לפני',
            'אחרי', 'בתוך', 'מתוך', 'אצל', 'ליד', 'מול', 'תחת', 'מעל', 'בין'
        }

        logger.info("Hebrew text processor initialized")

    def clean_text(self, text: str, **options) -> str:
        """Clean Hebrew text."""
        if not text or not isinstance(text, str):
            return ""

        cleaned = text

        # Remove URLs
        if options.get('remove_urls', True):
            cleaned = re.sub(r'http[s]?://[^\s]+', '', cleaned)

        # Remove emails
        if options.get('remove_emails', True):
            cleaned = re.sub(r'\S+@\S+', '', cleaned)

        # Remove English characters if specified
        if options.get('hebrew_only', False):
            cleaned = re.sub(r'[a-zA-Z]', '', cleaned)

        # Remove punctuation
        if options.get('remove_punctuation', True):
            # Remove both Hebrew and English punctuation
            hebrew_punctuation = '׳״,;:.!?()[]{}"\'-–—'
            punctuation = string.punctuation + hebrew_punctuation
            cleaned = cleaned.translate(str.maketrans('', '', punctuation))

        # Remove numbers
        if options.get('remove_numbers', True):
            cleaned = re.sub(r'\d+', '', cleaned)

        # Remove extra whitespace
        if options.get('remove_extra_whitespace', True):
            cleaned = re.sub(r'\s+', ' ', cleaned).strip()

        return cleaned

    def tokenize(self, text: str) -> List[str]:
        """Tokenize Hebrew text."""
        if not text:
            return []

        # Split by whitespace and filter Hebrew words
        tokens = text.split()
        hebrew_tokens = []

        for token in tokens:
            # Check if token contains Hebrew characters
            if re.search(r'[\u0590-\u05FF]', token):
                # Clean the token
                clean_token = re.sub(r'[^\u0590-\u05FF]', '', token)
                if clean_token:
                    hebrew_tokens.append(clean_token)

        return hebrew_tokens

    def extract_stems(self, text: str) -> List[str]:
        """Extract Hebrew stems by removing common prefixes and suffixes."""
        tokens = self.tokenize(text)
        stems = []

        for token in tokens:
            stem = self._hebrew_stem(token)
            if stem and len(stem) >= 2:  # Keep stems with at least 2 characters
                stems.append(stem)

        return stems

    def extract_lemmas(self, text: str) -> List[str]:
        """Extract Hebrew lemmas (for Hebrew, similar to stemming)."""
        # For Hebrew, lemmatization is complex and usually requires specialized tools
        # We'll use stemming as approximation
        return self.extract_stems(text)

    def extract_roots(self, text: str) -> List[str]:
        """Extract Hebrew roots (shoresh)."""
        tokens = self.tokenize(text)
        roots = []

        for token in tokens:
            root = self._extract_hebrew_root(token)
            if root and len(root) >= 2:
                roots.append(root)

        return list(set(roots))  # Remove duplicates

    def remove_stopwords(self, tokens: List[str], language: str = None) -> List[str]:
        """Remove Hebrew stopwords."""
        return [token for token in tokens if token not in self.hebrew_stopwords]

    def get_supported_languages(self) -> List[str]:
        """Hebrew processor supports Hebrew."""
        return ['he', 'hebrew', 'iw']

    def _hebrew_stem(self, word: str) -> str:
        """Simple Hebrew stemming by removing prefixes and suffixes."""
        if len(word) < 3:
            return word

        stem = word

        # Remove prefixes
        for prefix in self.prefixes:
            if stem.startswith(prefix) and len(stem) > len(prefix) + 1:
                stem = stem[len(prefix):]
                break

        # Remove suffixes
        for suffix in sorted(self.suffixes, key=len, reverse=True):
            if stem.endswith(suffix) and len(stem) > len(suffix) + 1:
                stem = stem[:-len(suffix)]
                break

        return stem

    def _extract_hebrew_root(self, word: str) -> str:
        """Extract Hebrew root (simplified approach)."""
        if len(word) < 3:
            return word

        # First, apply stemming
        stem = self._hebrew_stem(word)

        # For Hebrew root extraction, we need the 3-letter root (shoresh)
        # This is a simplified approach - real Hebrew root extraction is much more complex
        if len(stem) >= 3:
            # Take first 3 consonants as potential root
            consonants = []
            for char in stem:
                # Skip vowel marks and focus on consonants
                if char not in 'אאיו':  # Skip some vowel letters (simplified)
                    consonants.append(char)
                if len(consonants) >= 3:
                    break

            if len(consonants) >= 3:
                return ''.join(consonants[:3])
            else:
                return stem[:3] if len(stem) >= 3 else stem

        return stem


# ============================================================================
# Basic/Fallback Text Processor
# ============================================================================

class BasicTextProcessor(TextProcessorBase):
    """
    Basic text processor that always works
    Simple implementations without external dependencies
    """

    def __init__(self):
        self.available = True

        # Basic stopwords for multiple languages
        self.stopwords = {
            'english': {
                'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
                'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
                'to', 'was', 'will', 'with', 'i', 'you', 'we', 'they', 'this',
                'but', 'not', 'or', 'have', 'had', 'what', 'when', 'where', 'who'
            },
            'hebrew': {
                'של', 'את', 'על', 'אל', 'זה', 'זו', 'אני', 'אתה', 'היא', 'הוא',
                'הם', 'הן', 'גם', 'כל', 'או', 'אבל', 'רק', 'לא', 'עם', 'יש'
            }
        }

    def clean_text(self, text: str, **options) -> str:
        """Basic text cleaning."""
        if not text or not isinstance(text, str):
            return ""

        cleaned = text

        # Remove URLs
        if options.get('remove_urls', True):
            cleaned = re.sub(r'http[s]?://[^\s]+', '', cleaned)

        # Remove emails
        if options.get('remove_emails', True):
            cleaned = re.sub(r'\S+@\S+', '', cleaned)

        # Remove punctuation
        if options.get('remove_punctuation', True):
            cleaned = cleaned.translate(str.maketrans('', '', string.punctuation))

        # Convert to lowercase
        if options.get('to_lowercase', True):
            cleaned = cleaned.lower()

        # Remove extra whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()

        return cleaned

    def tokenize(self, text: str) -> List[str]:
        """Basic tokenization."""
        if not text:
            return []
        return re.findall(r'\b\w+\b', text.lower())

    def extract_stems(self, text: str) -> List[str]:
        """Basic stemming by suffix removal."""
        tokens = self.tokenize(text)
        stems = []

        for token in tokens:
            stem = token
            if len(token) > 4:
                # Remove common English suffixes
                if token.endswith('ing'):
                    stem = token[:-3]
                elif token.endswith('ed'):
                    stem = token[:-2]
                elif token.endswith('ly'):
                    stem = token[:-2]
                elif token.endswith('er'):
                    stem = token[:-2]
                elif token.endswith('est'):
                    stem = token[:-3]
                elif token.endswith('tion'):
                    stem = token[:-4]
                elif token.endswith('sion'):
                    stem = token[:-4]

            stems.append(stem)

        return stems

    def extract_lemmas(self, text: str) -> List[str]:
        """Basic lemmatization (just return cleaned tokens)."""
        return self.tokenize(text)

    def extract_roots(self, text: str) -> List[str]:
        """Basic root extraction (use stems)."""
        return list(set(self.extract_stems(text)))

    def remove_stopwords(self, tokens: List[str], language: str = 'english') -> List[str]:
        """Basic stopword removal."""
        lang = language.lower()
        if lang not in self.stopwords:
            lang = 'english'

        stopwords_set = self.stopwords[lang]
        return [token for token in tokens if token.lower() not in stopwords_set]

    def get_supported_languages(self) -> List[str]:
        """Basic processor supports English and Hebrew."""
        return ['english', 'hebrew', 'en', 'he']


# ============================================================================
# Register All Implementations
# ============================================================================

def register_text_processors():
    """Register all text processor implementations."""
    ProcessorFactory.register_text_processor("nltk", NLTKTextProcessor)
    ProcessorFactory.register_text_processor("spacy", SpaCyTextProcessor)
    ProcessorFactory.register_text_processor("hebrew", HebrewTextProcessor)
    ProcessorFactory.register_text_processor("basic", BasicTextProcessor)
    logger.info("All text processors registered")


# Auto-register when module is imported
register_text_processors()


# ============================================================================
# Smart Text Processor
# ============================================================================

class SmartTextProcessor(TextProcessorBase):
    """
    Smart text processor that automatically chooses the best available implementation
    """

    def __init__(self, preferred_order: List[str] = None):
        """
        Initialize smart processor.

        Args:
            preferred_order: List of processor names in order of preference
        """
        self.preferred_order = preferred_order or ["spacy", "nltk", "hebrew", "basic"]
        self.available_processors = {}
        self.language_specific = {
            'he': 'hebrew',
            'hebrew': 'hebrew',
            'iw': 'hebrew'
        }
        self._setup_processors()

    def _setup_processors(self):
        """Setup available processors."""
        for processor_name in self.preferred_order:
            try:
                processor = ProcessorFactory.create_text_processor(processor_name)
                # Test processor
                test_result = processor.tokenize("test")
                if test_result:
                    self.available_processors[processor_name] = processor
                    logger.info(f"Smart processor: {processor_name} is available")
            except Exception as e:
                logger.debug(f"Smart processor: {processor_name} not available: {e}")

        if not self.available_processors:
            # Ensure basic is always available
            self.available_processors['basic'] = BasicTextProcessor()

    def _choose_processor(self, language: str = None) -> TextProcessorBase:
        """Choose best processor for given language."""
        # Check language-specific processors first
        if language and language in self.language_specific:
            specific_processor = self.language_specific[language]
            if specific_processor in self.available_processors:
                return self.available_processors[specific_processor]

        # Use preferred order
        for processor_name in self.preferred_order:
            if processor_name in self.available_processors:
                processor = self.available_processors[processor_name]
                if not language or language in processor.get_supported_languages():
                    return processor

        # Fallback to any available processor
        if self.available_processors:
            return list(self.available_processors.values())[0]

        # Ultimate fallback
        return BasicTextProcessor()

    def clean_text(self, text: str, **options) -> str:
        """Clean text using best available processor."""
        language = options.get('language')
        processor = self._choose_processor(language)
        return processor.clean_text(text, **options)

    def tokenize(self, text: str) -> List[str]:
        """Tokenize using best available processor."""
        processor = self._choose_processor()
        return processor.tokenize(text)

    def extract_stems(self, text: str) -> List[str]:
        """Extract stems using best available processor."""
        processor = self._choose_processor()
        return processor.extract_stems(text)

    def extract_lemmas(self, text: str) -> List[str]:
        """Extract lemmas using best available processor."""
        processor = self._choose_processor()
        return processor.extract_lemmas(text)

    def extract_roots(self, text: str) -> List[str]:
        """Extract roots using best available processor."""
        processor = self._choose_processor()
        return processor.extract_roots(text)

    def remove_stopwords(self, tokens: List[str], language: str = 'english') -> List[str]:
        """Remove stopwords using best available processor."""
        processor = self._choose_processor(language)
        return processor.remove_stopwords(tokens, language)

    def get_supported_languages(self) -> List[str]:
        """Get all supported languages from available processors."""
        languages = set()
        for processor in self.available_processors.values():
            languages.update(processor.get_supported_languages())
        return list(languages)


# Register smart processor
ProcessorFactory.register_text_processor("smart", SmartTextProcessor)
ProcessorFactory.register_text_processor("auto", SmartTextProcessor)


# ============================================================================
# Convenience Functions
# ============================================================================

def get_best_available_text_processor() -> TextProcessorBase:
    """Get the best available text processor."""
    return SmartTextProcessor()


def extract_text_features(text: str,
                          include_stems: bool = True,
                          include_lemmas: bool = True,
                          include_roots: bool = True,
                          remove_stopwords: bool = True,
                          language: str = 'english') -> Dict[str, List[str]]:
    """
    Extract all text features using the best available processor.

    Args:
        text: Input text
        include_stems: Whether to include stems
        include_lemmas: Whether to include lemmas
        include_roots: Whether to include roots
        remove_stopwords: Whether to remove stopwords
        language: Text language

    Returns:
        Dictionary with all extracted features
    """
    processor = SmartTextProcessor()

    features = {}

    # Basic tokenization
    tokens = processor.tokenize(text)
    features['tokens'] = tokens

    # Remove stopwords if requested
    if remove_stopwords:
        tokens = processor.remove_stopwords(tokens, language)
        features['tokens_no_stopwords'] = tokens

    # Extract features
    if include_stems:
        features['stems'] = processor.extract_stems(text)

    if include_lemmas:
        features['lemmas'] = processor.extract_lemmas(text)

    if include_roots:
        features['roots'] = processor.extract_roots(text)

    return features


def get_available_text_processors() -> List[str]:
    """Get list of available text processor names."""
    available = ProcessorFactory.list_available()
    return available.get('text_processors', [])