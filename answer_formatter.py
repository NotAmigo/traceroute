Answer = tuple[str | None, list[int | None]]


class AnswerFormatter:
    def __init__(self, answer: Answer):
        self.answer = answer

    def __str__(self):
        return " ".join(f"{(str(i) + ' ms').ljust(6)}" if i is not None else '*'.ljust(6) for i in self.answer[1]) + \
               f" {self.answer[0].ljust(6) if self.answer[0] is not None else ''}"
