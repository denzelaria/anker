from google import genai
import genanki

reference = input("Reference file path:")
prompt = input("Prompt:")

cards = [
    {
        'front':'yeah.',
        'back':'yeah.'
    }
]

MODEL_ID = 1607392319
DECK_ID = 2059400110

client = genai.Client(api_key="AQ.Ab8RN6LJK6SRBBuoC5Onz7XIdwpOel00ms0Dg9aQlwgIksgOmg")

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

build_apkg(cards, "deck1", "output.apkg")