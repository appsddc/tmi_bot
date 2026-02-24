import os
import logging
import anthropic

logger = logging.getLogger(__name__)

# Your personal signal profile — edit this to tune TMI to your interests
USER_PROFILE = """
INTERESTS (weighted by importance):
- Irish Planning Laws, Housing Supply & Infrastructure (10/10)
- EirGrid / Energy Constraints / Data Centre Power (9/10)  
- Unit Economics of AI & Tech (8/10)
- FDI & Multinational Tax Structures in Ireland (8/10)
- Progress Studies — why things do/don't get built (7/10)
- Geopolitics only where it intersects with the above (5/10)

PREFERRED STYLE: Systems-thinking, contrarian, data-driven. Historical context welcome.

AVOID: Celebrity gossip, vague "future of humanity" speculation, US partisan politics, 
personal backstories beyond what's relevant to the ideas.
"""

SYSTEM_PROMPT = f"""You are the TMI Signal Scout — a precision information filter.

Your job is to analyze a podcast or video transcript and extract only what's genuinely 
valuable to the user. You are ruthlessly honest about signal vs noise.

USER PROFILE:
{USER_PROFILE}

RULES:
- Be specific about timestamps when they're available in the transcript
- If timestamps aren't available, describe where in the episode the segment occurs
- Don't pad the output — if an episode scores below 40%, say so clearly
- The "Link" section should connect the content to the Irish/local context where possible
- Segments must be at least 5 minutes of substantive content to qualify as High Value

OUTPUT FORMAT (use this exactly):
[Score: X%]

🟢 *High Value* [MM:SS – MM:SS]: One sentence on the mechanical insight.
💡 *The Link*: Why this matters for the Irish economy/infrastructure/tech ecosystem.

🟢 *High Value* [MM:SS – MM:SS]: (include a second segment if warranted)
💡 *The Link*: ...

🟡 *Worth a Skim* [MM:SS – MM:SS]: Useful but not essential.

🔴 *Skip*: Describe what to skip and why (e.g. "First 15 mins — standard intro and bio").

If score is below 40%, just return:
[Score: X%]
🔴 Not worth your time. Brief reason why.
"""


def analyze_transcript(transcript: str, source_url: str = "") -> str:
    """
    Send a transcript to Claude for TMI analysis.
    Returns a formatted signal report.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set.")

    client = anthropic.Anthropic(api_key=api_key)

    # Truncate transcript to avoid token limits — ~60k chars is roughly 15k tokens
    truncated = transcript[:60000]
    if len(transcript) > 60000:
        truncated += "\n\n[Transcript truncated for length]"

    user_message = f"Analyze this transcript and return your TMI Signal Scout report.\n\nSource: {source_url}\n\nTRANSCRIPT:\n{truncated}"

    try:
        message = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}]
        )
        return message.content[0].text

    except anthropic.APIError as e:
        logger.error(f"Anthropic API error: {e}")
        return "❌ Analysis failed — API error. Please try again."
    except Exception as e:
        logger.error(f"Unexpected error in analyze_transcript: {e}")
        return "❌ Analysis failed — unexpected error."