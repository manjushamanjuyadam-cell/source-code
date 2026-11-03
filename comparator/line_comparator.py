# comparator/line_comparator.py

from models.difference import Difference


class LineComparator:

    def compare(self, expected_lines, actual_lines, page_number):

        differences = []

        max_lines = max(
            len(expected_lines),
            len(actual_lines)
        )

        for i in range(max_lines):

            expected = (
                expected_lines[i].text
                if i < len(expected_lines)
                else ""
            )

            actual = (
                actual_lines[i].text
                if i < len(actual_lines)
                else ""
            )

            if expected != actual:

                differences.append(
                    Difference(
                        page=page_number,
                        line_number=i + 1,
                        expected=expected,
                        actual=actual
                    )
                )

        return differences