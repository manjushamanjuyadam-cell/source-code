from models.line import Line
from models.word import Word


class LineBuilder:

    Y_TOLERANCE = 3

    def build(self, words: list[Word]) -> list[Line]:

        if not words:
            return []

        # Sort by vertical position first, then horizontal
        words = sorted(words, key=lambda w: (w.top, w.x0))

        lines = []

        current_line = Line()
        current_y = words[0].top

        for word in words:

            if abs(word.top - current_y) <= self.Y_TOLERANCE:

                current_line.words.append(word)

            else:

                # Finish previous line
                current_line.words.sort(key=lambda w: w.x0)
                lines.append(current_line)

                # Start new line
                current_line = Line(words=[word])
                current_y = word.top

        # Add last line
        current_line.words.sort(key=lambda w: w.x0)
        lines.append(current_line)

        return lines