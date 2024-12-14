from flask import Flask, render_template, request
import numpy as np

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
    grid_size = 50
    grid = np.full((grid_size, grid_size), ' ', dtype=str)
    center = grid_size // 2

    first_word = words[0].upper()
    row, col = center, center - len(first_word) // 2
    grid[row, col:col + len(first_word)] = list(first_word)
    positions = [(row, col, 'H')]

    for word in words[1:]:
        word = word.upper()
        placed = False
        for pos in positions:
            r, c, direction = pos
            base_word = grid[r, c:c + len(first_word)] if direction == 'H' else grid[r:r + len(first_word), c]

            intersect = find_intersection(base_word, word)
            if intersect:
                i, j = intersect
                if direction == 'H':
                    start_row = r - j
                    if start_row >= 0 and start_row + len(word) <= grid_size:
                        if all(grid[start_row + k, c + i] in (' ', word[k]) for k in range(len(word))):
                            for k, char in enumerate(word):
                                grid[start_row + k, c + i] = char
                            positions.append((start_row, c + i, 'V'))
                            placed = True
                            break
                elif direction == 'V':
                    start_col = c - j
                    if start_col >= 0 and start_col + len(word) <= grid_size:
                        if all(grid[r + i, start_col + k] in (' ', word[k]) for k in range(len(word))):
                            for k, char in enumerate(word):
                                grid[r + i, start_col + k] = char
                            positions.append((r + i, start_col, 'H'))
                            placed = True
                            break
        if not placed:
            print(f"'{word}' kelimesi yerleştirilemedi.")
    return grid

def display_grid(grid):
    grid_str = ""
    for row in grid:
        grid_str += ''.join(row) + "<br>"
    return grid_str

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        words = request.form.get('words')
        words = [word.strip() for word in words.split(',') if word.strip()]

        if len(words) < 2 or len(words) > 6:
            return render_template('index.html', error="Lütfen 2 ile 6 arasında kelime girin.")
        
        for word in words:
            if not is_valid_word(word):
                return render_template('index.html', error=f"'{word}' geçersiz! Kelimeler yalnızca harflerden oluşmalı ve 12 karakterden kısa olmalı.")
        
        grid = create_crossword(words)
        grid_output = display_grid(grid)
        return render_template('index.html', grid_output=grid_output)

    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
