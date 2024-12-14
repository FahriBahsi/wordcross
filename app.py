from flask import Flask, render_template, request
import numpy as np
import os
import threading

app = Flask(__name__)

def is_valid_word(word):
    return len(word) <= 12 and word.isalpha()

def find_intersection(word1, word2):
    for i, char1 in enumerate(word1):
        for j, char2 in enumerate(word2):
            if char1 == char2:
                return i, j
    return None

def create_crossword(words):
    grid_size = 30  # Daha küçük grid boyutu
    grid = np.full((grid_size, grid_size), ' ', dtype=str)
    center = grid_size // 2

    first_word = words[0].upper()
    row, col = center, center - len(first_word) // 2
    grid[row, col:col + len(first_word)] = list(first_word)
    positions = [(row, col, 'H', first_word)]

    for word in words[1:]:
        word = word.upper()
        placed = False

        for pos in positions:
            r, c, direction, base_word = pos
            if direction == 'H':
                for i, char in enumerate(base_word):
                    intersect = find_intersection(base_word, word)
                    if intersect:
                        base_idx, word_idx = intersect
                        start_row = r - word_idx
                        start_col = c + base_idx

                        if 0 <= start_row < grid_size and start_row + len(word) <= grid_size:
                            if all(grid[start_row + k, start_col] in (' ', word[k]) for k in range(len(word))):
                                for k, char in enumerate(word):
                                    grid[start_row + k, start_col] = char
                                positions.append((start_row, start_col, 'V', word))
                                placed = True
                                break
            elif direction == 'V':
                for i, char in enumerate(base_word):
                    intersect = find_intersection(base_word, word)
                    if intersect:
                        base_idx, word_idx = intersect
                        start_col = c - word_idx
                        start_row = r + base_idx

                        if 0 <= start_col < grid_size and start_col + len(word) <= grid_size:
                            if all(grid[start_row, start_col + k] in (' ', word[k]) for k in range(len(word))):
                                for k, char in enumerate(word):
                                    grid[start_row, start_col + k] = char
                                positions.append((start_row, start_col, 'H', word))
                                placed = True
                                break

        if not placed:
            return grid, False

    return grid, True

def display_grid(grid):
    grid_str = ""
    for row in grid:
        grid_str += "<tr>"
        for cell in row:
            if cell.strip():
                grid_str += f"<td>{cell}</td>"
            else:
                grid_str += "<td>&nbsp;</td>"
        grid_str += "</tr>"
    return grid_str

def process_crossword(words, result):
    try:
        grid, success = create_crossword(words)
        if not success:
            result['error'] = "Kelimeler birbiriyle kesişim oluşturamadı."
        else:
            result['grid_output'] = display_grid(grid)
    except Exception as e:
        result['error'] = f"Bir hata oluştu: {e}"

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        words = request.form.get('words')
        words = [word.strip() for word in words.split(',') if word.strip()]

        if len(words) > 6:
            return render_template('index.html', error="Maksimum 6 kelime girebilirsiniz.")

        if not all(is_valid_word(word) for word in words):
            return render_template('index.html', error="Kelime uzunluğu maksimum 12 karakter olmalı ve sadece harf içermeli.")

        result = {}
        thread = threading.Thread(target=process_crossword, args=(words, result))
        thread.start()
        thread.join()

        if 'error' in result:
            return render_template('index.html', error=result['error'])

        return render_template('index.html', grid_output=result['grid_output'])

    return render_template('index.html')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
