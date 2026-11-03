from models.paragraph import Paragraph
from models.line import Line


class ParagraphBuilder:

    GAP_THRESHOLD = 18

    def build(self, lines: list[Line]) -> list[Paragraph]:

        if not lines:
            return []

        paragraphs = []

        current_paragraph = Paragraph()
        current_paragraph.lines.append(lines[0])

        previous_bottom = self._line_bottom(lines[0])

        for line in lines[1:]:

            current_top = self._line_top(line)

            gap = current_top - previous_bottom

            if gap <= self.GAP_THRESHOLD:

                current_paragraph.lines.append(line)

            else:

                paragraphs.append(current_paragraph)

                current_paragraph = Paragraph()
                current_paragraph.lines.append(line)

            previous_bottom = self._line_bottom(line)

        paragraphs.append(current_paragraph)

        return paragraphs

    def _line_top(self, line: Line):

        return min(word.top for word in line.words)

    def _line_bottom(self, line: Line):

        return max(word.bottom for word in line.words)