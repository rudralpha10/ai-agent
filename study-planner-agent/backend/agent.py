import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq

from memory import memory, save
from tools import calculate_hours

env_path = Path(__file__).with_name(".env")
_llm = None


def _resolve_groq_api_key() -> str | None:
    load_dotenv(dotenv_path=env_path, override=True)
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key and env_path.exists():
        for raw_line in env_path.read_text(encoding="utf-8-sig").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            if key.strip().lstrip("\ufeff") == "GROQ_API_KEY":
                api_key = value.strip().strip('"').strip("'")
                break

    if api_key:
        os.environ["GROQ_API_KEY"] = api_key
    return api_key


def _get_llm() -> ChatGroq:
    global _llm
    api_key = _resolve_groq_api_key()
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY is missing. Add it to backend/.env and save the file, then restart uvicorn."
        )
    if _llm is None:
        _llm = ChatGroq(groq_api_key=api_key, model_name="llama-3.1-8b-instant")
    return _llm


def ask_agent(user_input: str) -> str:
    try:
        total_hours = calculate_hours(30, 1)
        previous = memory.get("study_plan", {})
        save("study_plan", {"input": user_input, "hours": total_hours})

        previous = memory.get("study_plan", {})

        prompt = f"""
You are an AI Study Planner Agent.

Previous Context:
{previous}

User Request:
{user_input}

Total Study Hours Available:
{total_hours}

Instructions:
- Give a clean and structured response
- Use headings and bullet points
- Keep explanations concise
- Make realistic study plans
- Divide learning into phases/weeks
- Include revision and practice

Output Format:

🎯 Goal:
[Write user's learning goal]

⏳ Available Hours:
[Total hours]

📅 Study Roadmap:

Week 1:
- Topic 1
- Topic 2
- Practice Task

Week 2:
- Topic 1
- Topic 2
- Practice Task

Week 3:
- Topic 1
- Topic 2
- Practice Task

Week 4:
- Topic 1
- Topic 2
- Practice Task

📝 Daily Routine:
- Theory:
- Practice:
- Revision:

🚀 Mini Projects / Practice:
- Project / exercises suggestions

🔥 Tips:
- Tip 1
- Tip 2

Return ONLY the structured roadmap.
"""
        response = _get_llm().invoke([HumanMessage(content=prompt)])
        return response.content
    except Exception as e:
        return str(e)
