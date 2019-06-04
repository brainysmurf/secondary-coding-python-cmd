SOURCE = """
# Add any code to execute here
"""


class HookBase:
    loc = None

    def __init__(self, name, hooks, *args, **kwargs):
        if self.loc is None:
            import os
            import pathlib
            path = pathlib.Path(os.getcwd()).joinpath('main.py')
            source = path.read_text()
            self.loc = {}
            exec(SOURCE + source, {}, self.loc)

        self.hook = self.loc.get(name)
        if self.hook is None:
            raise Exception("No hook?")
        super().__init__(*args, **kwargs)


class SolveHook(HookBase):
    def __init__(self, hooks, *args, **kwargs):
        super().__init__('is_solved', hooks, *args, **kwargs)

    def is_solved(self):
        return self.hook(self.chosen, self.answer)
