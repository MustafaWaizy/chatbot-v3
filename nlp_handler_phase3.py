import spacy
from spacy.matcher import PhraseMatcher

# Load your trained spaCy intent classification model
nlp = spacy.load("nlp/chatbot_intent_model")

# Initialize PhraseMatcher with lowercase matching
matcher = PhraseMatcher(nlp.vocab, attr="LOWER")

# Custom phrases mapped to intents
custom_intents = {
    "greeting": ["hi", "hello", "hey", "good morning", "good evening"],
    "goodbye": ["bye", "goodbye", "see you", "talk later", "by"],
    "chitchat": ["how are you", "what’s up", "how's it going", "what’s new"]
}

# Add patterns for each intent to the matcher
for intent, phrases in custom_intents.items():
    patterns = [nlp.make_doc(text) for text in phrases]
    matcher.add(intent, patterns)

def get_intent(text: str):
    doc = nlp(text)
    matches = matcher(doc)
    if matches:
        match_id, start, end = matches[0]
        intent = nlp.vocab.strings[match_id]
        return intent.lower(), 1.0  # full confidence for phrase matches
    
    intent = max(doc.cats, key=doc.cats.get)
    confidence = doc.cats[intent]
    return intent.lower(), confidence
