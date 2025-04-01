from flask import Flask, render_template, request, jsonify
import openai
import random
import unicodedata

openai.api_key = "put your key here"
app = Flask(__name__)
language = random.choice(["Spanish", "French", "German", "Portuguese", "Italian", "Dutch", "English", "Latin" "Old English", "Old Norse", "Polish", "Czech", "Hawaiian", "Greek", "Gaelic", "Romanian", "Finnish", "Norse", "Icelandic", "Danish", "Vietnamese", "Polish", "Hungarian", "Swedish", "Afrikaans", "Esperanto", "Romansh", "Hatian Creole", "Tagalog", "Irish", "Swahili", "Turkish", "Pig Latin", "Catalan", "Galician", "Occitan", "Norwegian", "Slovak", "Slovenian", "Croatian", "Bosnian", "Montenegrin", "Welsh", "Cornish", "Breton", "Estonian", "Azerbaijani", "Uzbek", "Indonesian", "Malay", "Malagasy", "Yoruba", "Igbo", "Zulu", "Hausa", "Xhosa"])
# Game data
greek_to_latin_map = {
        'α': 'a', 'β': 'b', 'γ': 'g', 'δ': 'd', 'ε': 'e', 'ζ': 'z', 'η': 'i', 'θ': 'th',
        'ι': 'i', 'κ': 'k', 'λ': 'l', 'μ': 'm', 'ν': 'n', 'ξ': 'x', 'ο': 'o', 'π': 'p',
        'ρ': 'r', 'σ': 's', 'τ': 't', 'υ': 'y', 'φ': 'f', 'χ': 'ch', 'ψ': 'ps', 'ω': 'o',
        'ά': 'a', 'έ': 'e', 'ή': 'i', 'ί': 'i', 'ό': 'o', 'ύ': 'y', 'ώ': 'o', 'ς': 's',
        'ϊ': 'i', 'ΰ': 'y', 'ϋ': 'y', 'ό': 'o', 'ϊ': 'i', 'ΐ': 'i'
    }
def greek_to_latin(input_str):
    global greek_to_latin_map
    return ''.join([greek_to_latin_map.get(c, c) for c in input_str])
def remove_accents(input_str):
    # Normalize the string to remove diacritics (accents)
    for i in input_str:
        if i == '-' or i == "." or i == "!" or i == "@" or i == "#" or i == "$" or i == "%" or i == "^" or i == "&" or i == "*" or i == "(" or i == ")" or i == "_":
            i = ''
        if i in greek_to_latin_map.keys():
            input_str = greek_to_latin(input_str)
            break
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])
word = remove_accents(openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": f"Generate me a random hard {language} word for hangman, and remove accents. Make sure its unfair. Do not respond wih anything but the word. No special characters."}],
            max_tokens=500,  # Adjust max tokens to limit response length
            temperature=1
        ).choices[0].message["content"].strip().lower())
# word = "word"


guesses = []
incorrect_guesses = []
max_attempts = 9
attempts_left = max_attempts

def get_insult():
    return  openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user",
                   "content": f"You are a mean AI in a hangman game. Insult the player for guessing a wrong letter."}],
        max_tokens=500,  # Adjust max tokens to limit response length
        temperature=1
    ).choices[0].message["content"].strip()



@app.route("/")
def index():
    return render_template("hangman.html")

@app.route("/guess", methods=["POST"])
def guess():
    global attempts_left, word, guesses

    data = request.json
    letter = data.get("letter", "").lower()

    if not letter or not letter.isalpha() or len(letter) != 1:
        return jsonify({"error": "Invalid input"})

    # If the letter has already been guessed, return a message
    if letter in guesses or letter in incorrect_guesses:
        return jsonify({"message": "Already guessed this letter"})

    insult = ""  # Default insult is empty

    # If the guess is correct
    if letter in word:
        guesses.append(letter)
    else:
        # Add incorrect guess
        incorrect_guesses.append(letter)
        attempts_left -= 1
        insult = get_insult()  # Insult the player for wrong guess

        # Remove all progress (reset guesses)
        guesses = []

    # Display the word with underscores for unguessed letters
    display_word = " ".join([letter if letter in guesses else "_" for letter in word])

    game_status = "playing"
    if "_" not in display_word:
        game_status = "won"
    elif attempts_left == 0:
        game_status = "lost"

    return jsonify({
        "display_word": display_word,
        "incorrect_guesses": incorrect_guesses,
        "attempts_left": attempts_left,
        "status": game_status,
        "word": word if game_status == "lost" else None,
        "insult": insult  # Include insult only on wrong guess
    })




app.run(debug=True, port=8888)
