class TestIsSolved:
    def __init__(self, hook, **kwargs):
        self.hook = hook
        super().__init__(**kwargs)

    def is_solved():
        return self.hook(self.chosen, self.answer)
