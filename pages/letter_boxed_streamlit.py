import streamlit as st
from typing import List, Set, Union
from collections import defaultdict
from functools import wraps
from datetime import datetime
import pandas as pd


def timed(func):
    @wraps(func)
    def timed_func(*args, **kwargs):
        start_time = datetime.now()
        ret = func(*args, **kwargs)
        print(f'{func.__name__} - {(datetime.now() - start_time).total_seconds():.4f}')
        return ret
    return timed_func

class WordTrieNode:
    def __init__(self, value: str, parent: Union['WordTrieNode', None]):
        self.value = value
        self.parent = parent
        self.children = {}
        self.valid = False

    def get_word(self) -> str:
        if self.parent is not None:
            return self.parent.get_word() + self.value
        else:
            return self.value

class LetterBoxed:
    @timed
    def __init__(self, input_string: str, dictionary: str, len_threshold=3):
        # parse the input string (abc-def-ghi-jkl) into set of 4 sides
        self.input_string = input_string.lower()
        self.sides = {side for side in input_string.split('-')}
        self.puzzle_letters = {letter for side in self.sides for letter in side}
        self.len_threshold = len_threshold

        # build trie from newline-delimited .txt word list
        self.root = WordTrieNode('', None)
        with open(dictionary) as f:
            for line in f.readlines():
                self.add_word(line.strip().lower())

        # find all valid words in puzzle
        self.puzzle_words = self.get_puzzle_words()

        # puzzle_graph[starting_letter][ending_letter] = {{letters}: [words]}
        # e.g. puzzle_graph['f']['s'] = {{'a','e','f','r','s'} : ['fares', 'fears', 'farers', 'fearers']}
        self.puzzle_graph = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        for word in self.puzzle_words:
            self.puzzle_graph[word[0]][word[-1]][frozenset(word)].append(word)

    def add_word(self, word) -> None:
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = WordTrieNode(char, node)
            node = node.children[char]
        node.valid = True

    def _puzzle_words_inner(self, node: WordTrieNode, last_side: str) -> List[WordTrieNode]:
        valid_nodes = [node] if node.valid else []
        if node.children:
            for next_side in self.sides - {last_side}:
                for next_letter in next_side:
                    if next_letter in node.children:
                        next_node = node.children[next_letter]
                        valid_nodes += self._puzzle_words_inner(next_node, next_side)
        return valid_nodes

    @timed
    def get_puzzle_words(self) -> List[str]:
        all_valid_nodes = []
        for starting_side in self.sides:
            for starting_letter in starting_side:
                if starting_letter in self.root.children:
                    all_valid_nodes += self._puzzle_words_inner(self.root.children[starting_letter], starting_side)
        return [node.get_word() for node in all_valid_nodes]

    def _find_solutions_inner(self, path_words: List[List[str]], letters: Set[str], next_letter: str) -> List[List[List[str]]]:
        if len(letters) == 12:
            return [path_words]
        elif len(path_words) == self.len_threshold:
            return []

        solutions = []
        for last_letter in self.puzzle_graph[next_letter]:
            for letter_edge, edge_words in self.puzzle_graph[next_letter][last_letter].items():
                if letter_edge - letters:
                    solutions += self._find_solutions_inner(path_words + [edge_words], letters | letter_edge, last_letter)
        return solutions

    @timed
    def find_all_solutions(self) -> List[List[str]]:
        all_solutions = []
        for first_letter in self.puzzle_letters:
            for last_letter in self.puzzle_letters:
                for letter_edge, edge_words in self.puzzle_graph[first_letter][last_letter].items():
                    all_solutions += self._find_solutions_inner([edge_words], letter_edge, last_letter)
        return all_solutions

    def generate_solutions(self):
        for first_letter in self.puzzle_letters:
            for last_letter in self.puzzle_letters:
                for letter_edge, edge_words in self.puzzle_graph[first_letter][last_letter].items():
                    yield from self._generate_solutions_inner([edge_words], letter_edge, last_letter)
    
    def _generate_solutions_inner(self, path_words, letters, next_letter):
        if len(letters) == 12:
            yield path_words
        elif len(path_words) == self.len_threshold:
            return
        else:
            for last_letter in self.puzzle_graph[next_letter]:
                for letter_edge, edge_words in self.puzzle_graph[next_letter][last_letter].items():
                    if letter_edge - letters:
                        yield from self._generate_solutions_inner(
                            path_words + [edge_words],
                            letters | letter_edge,
                            last_letter
                        )




st.title("Letter Box Solver")

# Initialize a list to store the letters
letters = [None] * 12

# Top row
top_cols = st.columns([1, 1, 1, 1, 1])
with top_cols[1]:
    letters[0] = st.text_input("Top-Left", max_chars=1, key="input-top-1")
with top_cols[2]:
    letters[1] = st.text_input("Top-Middle", max_chars=1, key="input-top-2")
with top_cols[3]:
    letters[2] = st.text_input("Top-Right", max_chars=1, key="input-top-3")

# Middle rows with left and right cells
middle_cols_1 = st.columns([1, 3, 1])
with middle_cols_1[0]:
    letters[11] = st.text_input("Left-Top", max_chars=1, key="input-left-1")
with middle_cols_1[2]:
    letters[3] = st.text_input("Right-Top", max_chars=1, key="input-right-1")


middle_cols_2 = st.columns([1, 3, 1])
with middle_cols_2[0]:
    letters[10] = st.text_input("Left-Middle", max_chars=1, key="input-left-2")
with middle_cols_2[2]:
    letters[4] = st.text_input("Right-Middle", max_chars=1, key="input-right-2")

middle_cols_3 = st.columns([1, 3, 1])
with middle_cols_3[0]:
    letters[9] = st.text_input("Left-Bottom", max_chars=1, key="input-left-3")
with middle_cols_3[2]:
    letters[5] = st.text_input("Right-Bottom", max_chars=1, key="input-right-3")

# Bottom row
bottom_cols = st.columns([1, 1, 1, 1, 1])
with bottom_cols[1]:
    letters[8] = st.text_input("Bottom-Left", max_chars=1, key="input-bottom-1")
with bottom_cols[2]:
    letters[7] = st.text_input("Bottom-Middle", max_chars=1, key="input-bottom-2")
with bottom_cols[3]:
    letters[6] = st.text_input("Bottom-Right", max_chars=1, key="input-bottom-3")

# Length of Threshold
len_threshold = st.number_input("Threshold Length", min_value=1, step=1)

# Solution Mode
solution_mode = st.radio(
    "Solution Mode",
    options=["Find first solution", "Find all solutions"],
    index=1  # default to "Find all solutions"
)

# Add your Letter Box solver logic here
if st.button("Solve"):
    # Check if all letters are filled
    if all(letter and letter.strip() for letter in letters):
        # Process the letters and solve the puzzle
        letters_split = "-".join(["".join(letters[i:i+3]) for i in range(0, 12, 3)]).lower()
        dictionary_path = 'pages/words_for_letter_boxed.txt'

        

        if solution_mode == "Find first solution":
            # Store parameters to reinitialize LetterBoxed later
            st.session_state['letters_split'] = letters_split
            st.session_state['len_threshold'] = len_threshold
            st.session_state['solution_gen'] = None  # will be initialized later
            st.session_state['displayed_solutions'] = []
            st.session_state['first_solution_ready'] = True

            # Lazily reinitialize puzzle and generator
            puzzle = LetterBoxed(
                st.session_state['letters_split'],
                'pages/words_for_letter_boxed.txt',
                len_threshold=st.session_state['len_threshold']
            )
            st.session_state['solution_gen'] = puzzle.generate_solutions()

            try:
                gen = st.session_state['solution_gen']
                next_solution = next(gen)
                st.session_state['displayed_solutions'].append(next_solution)
            except StopIteration:
                st.info("No more solutions found.")

        else:
            st.write("Solving the puzzle with the given letters: ", letters_split)

            puzzle = LetterBoxed(letters_split, dictionary_path, len_threshold=len_threshold)
            st.write(len(puzzle.puzzle_words), "valid words found")
            
            meta_solutions = puzzle.find_all_solutions()
            st.write(len(meta_solutions), "meta-solutions (meaningfully distinct paths)")
            full_count = 0
            for meta_solution in meta_solutions:
                count = 1
                for element in meta_solution:
                    count *= len(element)
                full_count += count
            st.write(full_count, "total solutions (unique combinations/orders of words)")
            # Display meta-solutions in table form
            rows = []
            for idx, meta_solution in enumerate(meta_solutions):
                path_str = " → ".join(["/".join(word_group) for word_group in meta_solution])
                
                # Optional: compute number of combinations for this path
                combinations = 1
                for group in meta_solution:
                    combinations *= len(group)

                rows.append({
                    "#": idx + 1,
                    "Meta-Solution Path": path_str,
                    "Combinations": combinations
                })

            # Convert to DataFrame and display
            df = pd.DataFrame(rows)
            st.dataframe(df, use_container_width=True)
    else:
        st.error("Please fill in all the cells before solving.")

if st.session_state.get('first_solution_ready'):
    if st.button("Display another solution"):
        try:
            gen = st.session_state['solution_gen']
            next_solution = next(gen)
            st.session_state['displayed_solutions'].append(next_solution)
        except StopIteration:
            st.info("No more solutions found.")

    # Prepare the table data as a list of dicts of string-formatted paths
    solution_rows = []
    for idx, sol in enumerate(st.session_state['displayed_solutions']):
        # Convert list of word-lists (e.g., [['start'], ['middle', 'mix'], ['end']])
        # into a string representation for that path (e.g. "start -> middle/mix -> end")
        combined = " → ".join(["/".join(words) for words in sol])
        solution_rows.append({"#": idx + 1, "Solution Path": combined})

    # Display the one-solution-at-a-time table
    if solution_rows:
        df = pd.DataFrame(solution_rows)
        st.dataframe(df, use_container_width=True)
