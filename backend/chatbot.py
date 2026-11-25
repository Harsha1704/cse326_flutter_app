"""
Chatbot brain: combines retrieval context (from retrieval.py) with a system
prompt describing 3D Bharat's structure, and calls the Gemini API.

Requires: pip install google-generativeai
Requires: an env var GEMINI_API_KEY (get a free key at https://aistudio.google.com/apikey)
"""

import os
import google.generativeai as genai
from retrieval import build_context

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
# gemini-2.5-flash is on Google's free tier as of 2026 - if this stops working,
# check https://ai.google.dev/gemini-api/docs/models for the current free-tier model name
MODEL_NAME = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

SYSTEM_PROMPT = """You are the assistant built into 3D Bharat, a website for exploring India's \
historical places and planning trips. Answer naturally and concisely (2-4 sentences unless the \
user asks for more detail).

Site structure you can help users navigate to:
- main_page.html - the home dashboard
- historicalplaces.html - interactive India map; click a state to see its historical sites
- quizzes.html - quiz games about historical places
- airports.html - flight/transport booking and simulation
- index.html - login / registration

When a user asks about a specific historical place, state, or monument, use the CONTEXT below \
if it's provided - it comes directly from this site's own content, so prefer it over your general \
knowledge for anything it covers. If the context doesn't cover what they asked, answer from your \
general knowledge instead, but stay focused on travel/history/tourism topics relevant to India.

When a user asks how to do something on the site (book a flight, take a quiz, log in, find a \
state), give clear step-by-step guidance referencing the actual page names above.

If a question is completely unrelated to travel, history, or this site, politely redirect the \
user back to what you can help with."""


def ask_chatbot(user_message, conversation_history=None):
    """
    user_message: str
    conversation_history: optional list of {"role": "user"|"model", "text": str}
    Returns: (reply_text, matched_states)
    """
    if not GEMINI_API_KEY:
        return (
            "The chatbot isn't configured yet - set the GEMINI_API_KEY environment "
            "variable on the server (get a free key at https://aistudio.google.com/apikey).",
            [],
        )

    context, matched_states = build_context(user_message)

    prompt_parts = [SYSTEM_PROMPT]
    if context:
        prompt_parts.append(f"\nCONTEXT (from this site's own data):\n{context}")

    history_text = ""
    if conversation_history:
        for turn in conversation_history[-6:]:  # keep last 6 turns to control token usage
            role = "User" if turn.get("role") == "user" else "Assistant"
            history_text += f"\n{role}: {turn.get('text', '')}"
    if history_text:
        prompt_parts.append(f"\nRecent conversation:{history_text}")

    prompt_parts.append(f"\nUser: {user_message}\nAssistant:")
    full_prompt = "\n".join(prompt_parts)

    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(full_prompt)
        reply = response.text.strip()
    except Exception as e:
        reply = f"Sorry, I couldn't reach the AI service right now. ({type(e).__name__})"

    return reply, matched_states
