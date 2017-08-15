code = {
    "A": ".-",
    "B": "-...",
    "C": "-.-.",
    "D": "-..",
    "E": ".",
    "F": "..-.",
    "G": "--.",
    "H": "....",
    "I": "..",
    "J": ".---",
    "K": "-.-",
    "L": ".-..",
    "M": "--",
    "N": "-.",
    "O": "---",
    "P": ".--.",
    "Q": "--.-",
    "R": ".-.",
    "S": "...",
    "T": "-",
    "U": "..-",
    "V": "...-",
    "W": ".--",
    "X": "-..-",
    "Y": "-.--",
    "Z": "--..",
    "1": ".----",
    "2": "..---",
    "3": "...--",
    "4": "....-",
    "5": ".....",
    "6": "-....",
    "7": "--...",
    "8": "---..",
    "9": "----.",
    "0": "-----",
    "Ä": ".-.-",
    "Ö": "---.",
    "Ü": "..--",
    "ß": "...--..",
    " ":  "/"
}

# All durations below in seconds
# Duration for the "." character (dit)
duration_dit = 0.25
# Duration for the "-" character (dah), by convention 3 * dit
duration_dah = duration_dit * 3
# Duration of a short pause " ", by convention one dit
duration_pause = duration_dit
# Duration of a long pause between words "/", by convention 7 dits (5 dits + 2 * the normal symbol pause)
duration_pause_word = duration_dit * 5

# Durations in seconds
durations = {
    ".": duration_dit,
    "-": duration_dah,
    " ": duration_pause,
    "/": duration_pause_word
}


def text_to_morse(text: str):
    text_as_morse = list()
    for letter in text.upper():
        text_as_morse.append(code[letter])

    # Convention says that there must be 3 pauses between characters
    return " ".join(text_as_morse)
