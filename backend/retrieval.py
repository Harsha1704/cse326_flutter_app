"""
Retrieval layer for the chatbot.
Loads the site's own historical-place content (extracted from historicalplaces.html)
and finds the most relevant snippets for a user's question, so the chatbot
answers about your actual site data instead of guessing.
"""

import json
import os
import re

DATA_PATH = os.path.join(os.path.dirname(__file__), "state_data.json")

with open(DATA_PATH, "r", encoding="utf-8") as f:
    STATE_DATA = json.load(f)

STATE_NAMES = list(STATE_DATA.keys())
# Lowercase lookup for matching user text against state names
_STATE_NAMES_LOWER = {name.lower(): name for name in STATE_NAMES}


_STOPWORDS = {
    "the", "and", "for", "with", "that", "this", "was", "are", "its", "his", "her",
    "has", "have", "had", "who", "which", "from", "also", "one", "you", "your",
    "can", "how", "what", "where", "when", "why", "does", "book", "into", "over",
    "each", "some", "many", "most", "more", "less", "than", "such", "will", "about",
}


def _tokenize(text):
    words = re.findall(r"[a-zA-Z]+", text.lower())
    return [w for w in words if len(w) >= 4 and w not in _STOPWORDS]


def find_mentioned_states(query):
    """Return any state names the user's message directly mentions."""
    q_lower = query.lower()
    matches = []
    for name_lower, original in _STATE_NAMES_LOWER.items():
        if name_lower in q_lower:
            matches.append(original)
    return matches


def keyword_search(query, top_k=3):
    """
    Very lightweight keyword-overlap search across all site headings/content,
    used when the user doesn't name a specific state (e.g. "best waterfalls in India").
    Good enough for a site of this size without needing an embeddings model.
    """
    query_tokens = set(_tokenize(query))
    if not query_tokens:
        return []

    scored = []
    for state, data in STATE_DATA.items():
        for item in data.get("images", []):
            text = f"{item.get('heading', '')} {item.get('content', '')}"
            tokens = set(_tokenize(text))
            overlap = len(query_tokens & tokens)
            if overlap > 0:
                scored.append((overlap, state, item.get("heading", "").strip(":- "), item.get("content", "")))

    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[:top_k]


def build_context(query, max_chars=3000):
    """
    Build a grounding context block for the LLM prompt based on the user's query.
    Priority: explicitly mentioned states > keyword search across all states.
    """
    mentioned = find_mentioned_states(query)
    chunks = []

    if mentioned:
        for state in mentioned[:2]:  # cap to avoid overloading the prompt
            items = STATE_DATA[state].get("images", [])[:4]
            for item in items:
                heading = item.get("heading", "").strip(":- ")
                content = item.get("content", "")
                chunks.append(f"[{state} — {heading}]\n{content}")
    else:
        results = keyword_search(query, top_k=4)
        # Only trust results with a real signal - avoids grounding on noise
        # for navigation/booking questions that aren't about a specific place.
        results = [r for r in results if r[0] >= 2]
        for _, state, heading, content in results:
            chunks.append(f"[{state} — {heading}]\n{content}")

    context = "\n\n".join(chunks)
    if len(context) > max_chars:
        context = context[:max_chars] + "..."
    return context, mentioned


if __name__ == "__main__":
    # Quick manual test
    for q in ["Tell me about Kerala backwaters", "best waterfalls in India", "how do I book a flight"]:
        ctx, states = build_context(q)
        print(f"QUERY: {q}")
        print(f"Matched states: {states}")
        print(f"Context length: {len(ctx)} chars")
        print(ctx[:300])
        print("---")
