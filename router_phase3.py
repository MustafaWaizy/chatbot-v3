from nlp_handler_phase3 import get_intent
from rule_responses_phase3 import get_response, faq_dict
from sentence_transformers import SentenceTransformer
from logger_phase3 import log_unknown_input
from fuzzywuzzy import fuzz
import torch

# Globals
model = None
faq_keys = list(faq_dict.keys())
faq_embeddings = None

# Called during FastAPI @startup
def initialize_model():
    global model, faq_embeddings
    model = SentenceTransformer('all-MiniLM-L6-v2')
    faq_embeddings = model.encode(faq_keys, convert_to_tensor=True)

# Semantic match (Step 2)
def get_semantic_match(text, threshold=0.6):
    if model is None or faq_embeddings is None:
        print("[ERROR] Semantic model not initialized")
        return None, 0.0

    input_embedding = model.encode(text, convert_to_tensor=True)
    cosine_scores = torch.nn.functional.cosine_similarity(input_embedding, faq_embeddings)
    top_score, top_idx = torch.max(cosine_scores, dim=0)

    best_match = faq_keys[top_idx]
    similarity = top_score.item()

    print(f"[SEMANTIC DEBUG] Best match: '{best_match}' with score: {similarity:.4f}")
    if similarity >= threshold:
        return best_match, similarity
    return None, similarity

# Fuzzy match (Step 3)
def get_fuzzy_match(input_text: str, threshold=65):
    best_key = None
    best_score = 0
    for key in faq_keys:
        score = fuzz.token_sort_ratio(input_text.lower(), key.lower())
        if score > best_score:
            best_score = score
            best_key = key
    if best_score >= threshold:
        return best_key, best_score / 100.0
    return None, 0.0

# Fallback suggestions (Step 4)
def get_top_suggestions(input_text: str, top_n=3, threshold=0.1):
    input_embedding = model.encode(input_text, convert_to_tensor=True)
    cosine_scores = torch.nn.functional.cosine_similarity(input_embedding, faq_embeddings)
    top_indices = torch.argsort(cosine_scores, descending=True)

    suggestions = []
    for idx in top_indices:
        score = cosine_scores[idx].item()
        if score >= threshold:
            suggestions.append(faq_keys[idx])
        if len(suggestions) == top_n:
            break
    return suggestions

# Main logic controller
def route_message(text: str):
    # Step 1: Rule-based intent classifier
    intent, confidence = get_intent(text)
    print(f"[DEBUG] spaCy Intent: {intent}, Confidence: {confidence:.2f}")
    if confidence >= 0.65:
        reply = get_response(intent)
        if reply:
            return {
                "response": reply,
                "suggestions": []
            }

    # Step 2: Semantic similarity
    semantic_key, semantic_conf = get_semantic_match(text, threshold=0.6)
    print(f"[DEBUG] Semantic Match: {semantic_key}, Confidence: {semantic_conf:.2f}")
    if semantic_key:
        reply = get_response(semantic_key)
        if reply:
            return {
                "response": reply,
                "suggestions": []
            }

    # Step 3: Fuzzy matching fallback
    fuzzy_key, fuzzy_conf = get_fuzzy_match(text, threshold=65)
    print(f"[DEBUG] Fuzzy Match: {fuzzy_key}, Score: {fuzzy_conf:.2f}")
    if fuzzy_key and fuzzy_conf >= 0.65:
        reply = get_response(fuzzy_key)
        if reply:
            return {
                "response": reply,
                "suggestions": []
            }

    # Step 4: Fallback structured suggestions
    suggestions = get_top_suggestions(text, top_n=3, threshold=0.1)
    print(f"[DEBUG] Fallback Suggestions: {suggestions}")
    structured_suggestions = [
        {"text": s, "intent": s} for s in suggestions
    ]

    log_unknown_input(text, "\n".join([f"- {s}" for s in suggestions]))

    return {
        "response": (
            "I'm still learning and working to improve my answers.\n"
            "Did you mean one of the following?"
        ),
        "suggestions": structured_suggestions
    }
