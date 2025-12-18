from pathlib import Path

from src.models import BookData

with open(Path("testbook_out.json")) as fd:
    book = BookData.model_validate_json(fd.read())

for stats in [
    (
        f"{b.puzzle_title}, {len(b.puzzle_word_list)} words out of {len(b.input_word_list)}, "
        f"size {b.width}x{b.height} with a density of {b.density}"
    )
    for b in book.puzzles
]:
    print(stats)
