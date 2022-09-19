class DummyPuzzle:

    def __init__(self, graph, start, end, blocks=None):
        self.graph = graph
        self.start = start
        self.end = end
        self.blocks = set(blocks) if blocks else set()

    def fail_fast(self) -> bool:
        return self.start in self.blocks

    def is_solved(self) -> bool:
        return self.start == self.end

    def extensions(self):
        R = []
        neis = self.graph[self.start]
        for n in neis:
            R.append(DummyPuzzle(self.graph, n, self.end, self.blocks))
        return R

    def __repr__(self):
        return f'({self.start} -> {self.end})'

    def __str__(self):
        return f'({self.start} -> {self.end})'

    def __eq__(self, other):
        if isinstance(other, str):
            return str(self) == other
        return self.start == other.start and self.end == other.end
