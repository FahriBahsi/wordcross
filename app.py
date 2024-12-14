from flask import Flask, render_template, request
import numpy as np
import os  # Heroku'nun PORT değişkeni için

app = Flask(__name__)

def is_valid_word(word):
    return len(word) <= 12 and word.isalpha()

def find_intersection(word1, word2):
    for i, char1 in enumerate(word1):
        for j, char2 in enumerate(word2):
            if char1 == char2:
                print(f"Kesişim bulundu: {char1} ({i}, {j})")  # Hata ayıklama için
                return i, j
    print(f"Kesişim yok: {word1} ile {word2}")  # Hata ayıklama için
    return None

def create_crossword(words):
    grid_size = 50
    grid = np.full((grid_size, grid_size), ' ', dtype=str)
    center = grid_size // 2

    first_word = words[0].upper()
    row, col = center, center - len(first_word) // 2
    grid[row, col:col + len(first_word)] = list(first_word)
    positions = [(row, col, 'H')]

    print(f"İlk kelime yerleşti: {first_word} ({row}, {col})")  # Hata ayıklama için

    placed_any_word = False  # Yerleştirilen bir kelime olup olmadığını takip et

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
                            placed_any_word = True
                            print(f"{word} yerleşti: Dikey ({start_row}, {c + i})")  # Hata ayıklama için
                            break
                elif direction == 'V':
                    start_col = c - j
                    if start_col >= 0 and start_col + len(word) <= grid_size:
                        if all(grid[r + i, start_col + k] in (' ', word[k]) for k in range(len(word))):
                            for k, char in enumerate(word):
                                grid[r + i, start_col + k] = char
                            positions.append((r + i, start_col, 'H'))
                            placed = True
                            placed_any_word = True
                            print(f"{word} yerleşti: Yatay ({r + i}, {start_col})")  # Hata ayıklama için
                            break
        if not placed:
            print(f"'{word}' kelimesi yerleştirilemedi.")  # Hata ayıklama için

    return grid, placed_any_word

def display_grid(grid):
    grid_str = ""
    for row in grid[:15]:  # İlk 15 satır
        grid_str += "<tr>"
        for cell in row[:15]:  # İlk 15 sütun
            grid_str += f"<td>{cell if cell != ' ' else '&nbsp;'}</td>"
        grid_str += "</tr>"
    return grid_str

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        words = request.form.get('words')
        words = [word.strip() for word in words.split(',') if word.strip()]
        print(f"Girilen kelimeler: {words}")  # Hata ayıklama için

        if len(words) < 2 or len(words) > 6:
            return render_template('index.html', error="Lütfen 2 ile 6 arasında kelime girin.")

        for word in words:
            if not is_valid_word(word):
                return render_template('index.html', error=f"'{word}' geçersiz! Kelimeler yalnızca harflerden oluşmalı ve 12 karakterden kısa olmalı.")

        grid, placed_any_word = create_crossword(words)

        # Eğer hiçbir kelime yerleştirilemediyse hata mesajı döndür
        if not placed_any_word:
            return render_template('index.html', error="Kelimeler arasında kesişim bulunamadı.")

        grid_output = display_grid(grid)
        print(f"Üretilen Grid: \n{grid}")  # Hata ayıklama için
        return render_template('index.html', grid_output=grid_output)

    return render_template('index.html')

if __name__ == "__main__":
    # Heroku'nun PORT değişkenini kullanın
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
