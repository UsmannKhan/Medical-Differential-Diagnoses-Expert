import os
from openai import OpenAI
from dotenv import load_dotenv

# Config
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

# System prompt for the llm (assigning its role)
SYSTEM_PROMPT = """You are a cautious clinical triage assistant.
You must NOT provide a medical diagnosis.
Given the symptoms, return the TOP 3 likely DIFFERENTIAL diagnoses as JSON.
Rules:
- Be concise, evidence-based, adult general population by default.
- Include a calibrated probability percentage for EACH diagnosis that sums to 100.
- Add a one-sentence rationale per item.
- Add a short red_flags note at the end advising urgent care if any are present.
- Never claim certainty. Never give treatment plans or drug dosing.
- Also suggest three **natural follow-up questions the patient might want to ask the assistant**, such as:
  * What does this mean for me?
  * Should I be worried about this symptom?
  * What should I ask my doctor next?
  Do NOT suggest questions a doctor would ask the patient.
- ALWAYS add a disclaimer at the end that is "This is not medical advice. Seek professional evaluation."
- If the user input is not symptoms, give a brief refusal and ask for symptoms.
Output JSON ONLY with this schema if user inputs symptoms:
{
  "differentials": [
    {"diagnosis": string, "probability_percent": number, "rationale": string},
    {"diagnosis": string, "probability_percent": number, "rationale": string},
    {"diagnosis": string, "probability_percent": number, "rationale": string}
  ],
  "clarifying_questions": [
    "string",
    "string",
    "string"
  ]
  "red_flags": string,
  "disclaimer": "This is not medical advice. Seek professional evaluation."
}
Otherwise, output this JSON ONLY:
{
  "differentials": [
    {"diagnosis": None, "probability_percent": 0, "rationale": "Please provide symptoms for analysis."},
  ],
  "clarifying_questions": [],
  "red_flags": None,
  "disclaimer": "This is not medical advice. Seek professional evaluation."
}
"""

# Function to generate the differential diagose analysis using OpenAI
def get_differential_diagnoses(symptoms, context=None):
    user_prompt = f"Symptoms: {symptoms}. Context: {context}"

    response = client.responses.create(
        model="gpt-5",
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ]
    )

    return response.output_text

# Function to handle further follow-up queries for a continuous conversation
def get_followup_response(user_input, history, chat_context):
    user_prompt = f"User input: {user_input}. User differential diagnoses for reference: {history}. Chat history: {chat_context}"
    response = client.responses.create(
        model="gpt-5",
        input= user_prompt
    )

    return response.output_text
    




