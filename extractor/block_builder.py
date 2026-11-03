from models.block import Block
from models.line import Line


class BlockBuilder:

    GAP_THRESHOLD = 20

    def build(self, lines: list[Line]) -> list[Block]:

        if not lines:
            return []

        blocks = []

        current_block = Block()
        current_block.lines.append(lines[0])

        previous_bottom = self._line_bottom(lines[0])

        for line in lines[1:]:

            current_top = self._line_top(line)

            gap = current_top - previous_bottom

            if gap <= self.GAP_THRESHOLD:

                current_block.lines.append(line)

            else:

                blocks.append(current_block)

                current_block = Block()
                current_block.lines.append(line)

            previous_bottom = self._line_bottom(line)

        blocks.append(current_block)

        return blocks

    def _line_top(self, line: Line) -> float:

        return min(
            word.top
            for word in line.words
        )

    def _line_bottom(self, line: Line) -> float:

        return max(
            word.bottom
            for word in line.words
        )