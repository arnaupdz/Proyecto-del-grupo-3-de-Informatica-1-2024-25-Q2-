from node import Distance

class Segment:
    def __init__(self, name, origin, destination):
        self.name = name
        self.origin = origin
        self.destination = destination
        self.cost = Distance(origin, destination)

    def __str__(self):
        return f"{self.name}: {self.origin.name} -> {self.destination.name}, Cost: {self.cost:.2f}"
