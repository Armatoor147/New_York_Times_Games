from typing import List, Tuple
from langchain_core.tools import tool

def is_valid(word: str, central_letter: str, peripheral_letters: List[str]) -> bool:
    central_letter = central_letter.upper()
    peripheral_letters = [normal_letter.upper() for normal_letter in peripheral_letters]
    if central_letter not in word:
        return False
    for letter in word:
        if letter not in peripheral_letters and letter != central_letter:
            return False
    return True
    

def spelling_bee(central_letter: str, peripheral_letters: List[str]) -> List[Tuple[int, List[str]]]:
    with open("pages/words_for_spelling_bee.txt") as f:
        words = [word.rstrip().upper() for word in f if word.rstrip().isalpha() and len(word.rstrip()) > 3]
    valid_words = [word for word in words if is_valid(word, central_letter, peripheral_letters)]
    valid_words_categorised_by_length = {}
    for word in valid_words:
        length = len(word)
        if length not in valid_words_categorised_by_length:
            valid_words_categorised_by_length[length] = []
        valid_words_categorised_by_length[length].append(word)
    valid_words_ordered_by_length = [(number, valid_words_categorised_by_length[number]) for number in sorted(list(valid_words_categorised_by_length.keys()), reverse=True)]
    return valid_words_ordered_by_length

@tool
def spelling_bee_tool(central_letter: str, peripheral_letters: List[str]) -> List[Tuple[int, List[str]]]:
    """
    This tool takes the central letter and the peripherial letters from a given "Spelling Bee" 
    puzzle and returns all the possible words that are valid (i.e. must contain the central letter, 
    cannot contain a letter other than the central letter and peripheral letters, and must be contain 
    more than 3 letters). The format of the output is a list of tuples. Each tuple contains a 
    interger and a list of strings, the integer represents the length of the words in the correponding 
    list of strings. The tuples inside the outer list are ordered from longest words to shortest words.

    Args:
        central_letter (str): The central letter.
        peripheral_letters (List[str]): The peripheral letters.
    Returns:
        List[Tuple[int, List[str]]]: The valid words.
    """
    return spelling_bee(central_letter, peripheral_letters)




if __name__ == "__main__":
    # central_letter = "E"
    # peripheral_letters = ["L", "A", "N", "Y", "O", "G"]
    # print(spelling_bee(central_letter, peripheral_letters))
    print(spelling_bee)