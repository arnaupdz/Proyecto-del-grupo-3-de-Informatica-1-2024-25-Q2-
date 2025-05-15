from node import Distance


class Segment:
    def __init__(self, name, origin, destination, cost):
        """
        Constructor de la clase Segment

        Args:
            name (str): Nombre del segmento
            origin (Node): Nodo de origen
            destination (Node): Nodo de destino
            cost (float): Costo del segmento (distancia)
        """
        self.name = name
        self.origin = origin
        self.destination = destination
        self.cost = cost

    def __str__(self):
        return f"{self.name}: {self.origin.name} -> {self.destination.name}, Cost: {self.cost:.2f}"
