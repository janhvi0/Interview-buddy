from agno.agent import Agent
from agno.models.google import Gemini
from agno.memory.v2.db.sqlite import SqliteMemoryDb
from agno.memory.v2.manager import MemoryManager
from agno.memory.v2.memory import Memory
from agno.storage.sqlite import SqliteStorage
from agno.tools.googlesearch import GoogleSearchTools
from textwrap import dedent
from dotenv import load_dotenv
import os

load_dotenv()

# Setup Agent Components
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# print("GEMINI_API_KEY:", GEMINI_API_KEY)

model = Gemini(id="gemini-2.0-flash", api_key=GEMINI_API_KEY, max_output_tokens=1024)

agent_storage = SqliteStorage(table_name="agent_sessions", db_file="tmp/persistent_memory.db")
memory_db = SqliteMemoryDb(table_name="memory", db_file="tmp/memory.db")

memory = Memory(
    db=memory_db,
    memory_manager=MemoryManager(
        memory_capture_instructions=dedent("""
                        Collect User's name,
                        Collect Information about the user's job title, industry, and experience level,
                        Collect Information about the user's interview preparation status,
        """),
        model=Gemini(id="gemini-2.0-flash"),
    ),
)

Aceint_agent = Agent(
    name="Aceint Agent",
    model=model,
    tools=[GoogleSearchTools()],
    add_history_to_messages=True,
    num_history_responses=5,
    add_datetime_to_instructions=True,
    markdown=True,
    memory=memory,
    enable_agentic_memory=True,
    instructions=dedent("""
        You are an AI Interview Coach on WhatsApp. Help users prepare for job interviews across all roles, industries, and experience levels.

        Your tasks:

        Start by asking for the user’s job title, industry, and experience level — only if not already provided.

        Ask mock interview questions tailored to that role and experience.

        Give honest, helpful feedback with suggestions for better answers.

        Simulate various interviewer styles (formal, friendly, rushed, technical, behavioral).

        Adapt your questions and tone based on user responses.

        Provide summaries of strengths and areas to improve when relevant.

        Keep responses natural, professional, and human-like.

        Do not repeat the same greeting or introduction. Respond only with relevant follow-ups and use emojis.
    """),

    debug_mode=True,
)

def get_agent():
    return Aceint_agent
