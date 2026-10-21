from google import genai
import genanki
from pydantic import BaseModel
import json
import os
from pypdf import PdfReader
from dotenv import load_dotenv

load_dotenv(override=True)

MODEL_ID = 1607392319
DECK_ID = 2059400110

class Card(BaseModel):
    front: str
    back: str
    
class Deck(BaseModel):
    cards:list[Card]
    
my_model = genanki.Model(
    MODEL_ID,
    'Custom deck',
    fields = [
        {'name': 'Front'},
        {'name': 'Back'}
    ],
    templates=[
        {
            'name':'Card 1',
            'qfmt':'{{Front}}',
            'afmt':'{{FrontSide}}<hr id="answer">{{Back}}'
        }
    ]
)

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
  
reference = input("Reference file path:").strip()
prompt = input("Prompt:")

def build_apkg(cards: list[dict], deck_name: str, output_path: str) -> str:
    deck = genanki.Deck(DECK_ID, deck_name)
    for card in cards:
        note = genanki.Note(
            model = my_model,
            fields = [card['front'], card['back']]
        )
        deck.add_note(note)
    package = genanki.Package(deck)
    package.write_to_file(output_path)
    return output_path

def generate_content(reference, prompt):
    try:
        file_to_txt = None
        file_type = reference.split(".")[1]
        if file_type == "txt" or file_type == "md":
            with open(reference, "r", encoding="utf-8") as file:
                file_to_txt = file.read()
        elif file_type == "pdf":
            file_to_txt = ""
            reader = PdfReader(reference)
            for i, page in enumerate(reader.pages()):
                file_to_txt += f"Page {i}\n{page.extract_text()}\n"
            
        contents = f"REFERENCE MATERIAL: {file_to_txt}. PROMPT: {prompt}"
        system = (
            "You are an anki deck generator. Given reference material and a prompt "
            "instruction, produce concise front/back flashcards based on prompted format."
            "Unless stated by prompt, make backs as simple as possible(no long text blocks) and well structured(eg bullet points)."
            "If data from the reference you choose is short(eg one sentence) try to keep it like the reference(dont alter)."
            "If targeted material needed is long and needs summarization, you may alter it when writing it."
            "No duplicate cards."
            "If the prompt contradicts any of these then listen to the prompt. Prompt is priority."
        )
    
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=contents,
            config={
                "system_instruction": system,
                "response_mime_type": "application/json",
                "response_schema": Deck,
            },
        )
        parsed = json.loads(response.text)
        cards = parsed["cards"]
        build_apkg(cards, "deck1", "output.apkg")
    
    except Exception as e:
        print("e",e)
        print("Invalid file path")
    return

generate_content(reference, prompt)