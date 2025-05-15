class NavPoint:
    def __init__(self, number, name, latitude, longitude):
        """
        Representa un punto de navegación en el espacio aéreo

        Args:
            number (int): Identificador único del punto
            name (str): Nombre del punto de navegación
            latitude (float): Latitud en grados decimales
            longitude (float): Longitud en grados decimales
        """
        self.number = number
        self.name = name
        self.latitude = latitude
        self.longitude = longitude


class NavSegment:
    def __init__(self, origin_number, destination_number, distance):
        """
        Representa un segmento que conecta dos puntos de navegación

        Args:
            origin_number (int): Número del punto de origen
            destination_number (int): Número del punto de destino
            distance (float): Distancia entre los puntos en kilómetros
        """
        self.origin_number = origin_number
        self.destination_number = destination_number
        self.distance = distance


class NavAirport:
    def __init__(self, name, sids, stars):  # Nota: minúsculas
        self.name = name
        self.sids = sids  # Lista de números de puntos SID
        self.stars = stars  # Lista de números de puntos STAR


class AirSpace:
    def __init__(self):
        """Representa todo el espacio aéreo con sus componentes"""
        self.nav_points = []  # Lista de NavPoint
        self.nav_segments = []  # Lista de NavSegment
        self.nav_airports = []  # Lista de NavAirport


def LoadAirspace(nav_file, seg_file, airport_file):
    """
    Carga los datos del espacio aéreo desde los archivos de texto

    Args:
        nav_file (str): Ruta al archivo de puntos de navegación
        seg_file (str): Ruta al archivo de segmentos
        airport_file (str): Ruta al archivo de aeropuertos

    Returns:
        AirSpace: Objeto con todos los datos del espacio aéreo cargados
    """
    airspace = AirSpace()

    # 1. Cargar puntos de navegación
    with open(nav_file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            parts = line.split()
            try:
                number = int(parts[0])
                name = parts[1]
                latitude = float(parts[2])
                longitude = float(parts[3])
                airspace.nav_points.append(NavPoint(number, name, latitude, longitude))
            except (IndexError, ValueError) as e:
                print(f"Error al procesar línea en {nav_file}: {line}")
                continue

    # 2. Cargar segmentos
    with open(seg_file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            parts = line.split()
            try:
                origin = int(parts[0])
                destination = int(parts[1])
                distance = float(parts[2])
                airspace.nav_segments.append(NavSegment(origin, destination, distance))
            except (IndexError, ValueError) as e:
                print(f"Error al procesar línea en {seg_file}: {line}")
                continue

    # 3. Cargar aeropuertos
    with open(airport_file, 'r') as f:
        current_airport = None
        current_sids = []
        current_stars = []

        for line in f:
            line = line.strip()
            if not line:
                continue

            # Si es un aeropuerto nuevo
            if not line.startswith(('SID', 'STAR')):
                # Guardar el aeropuerto anterior si existe
                if current_airport:
                    airspace.nav_airports.append(NavAirport(current_airport, current_sids, current_stars))
                    current_sids = []
                    current_stars = []

                current_airport = line
            elif line.startswith('SID'):
                try:
                    current_sids = [int(x) for x in line.split()[1:]]
                except ValueError:
                    print(f"Error al procesar SIDs en {airport_file}: {line}")
            elif line.startswith('STAR'):
                try:
                    current_stars = [int(x) for x in line.split()[1:]]
                except ValueError:
                    print(f"Error al procesar STARs en {airport_file}: {line}")

        # Añadir el último aeropuerto
        if current_airport:
            airspace.nav_airports.append(NavAirport(current_airport, current_sids, current_stars))

    return airspace


def GetReachableNavPoints(airspace, start_id):
    """
    Obtiene todos los puntos de navegación alcanzables desde un punto inicial

    Args:
        airspace (AirSpace): El espacio aéreo completo
        start_id (int): Número del punto de inicio

    Returns:
        list: Lista de NavPoint alcanzables desde el punto inicial
    """
    from collections import deque

    # Encontrar el punto de inicio
    start_point = next((p for p in airspace.nav_points if p.number == start_id), None)
    if not start_point:
        return []

    visited = set()
    queue = deque([start_point])
    reachable = []

    while queue:
        current = queue.popleft()
        if current.number in visited:
            continue

        visited.add(current.number)
        reachable.append(current)

        # Encontrar todos los vecinos (destinos de segmentos que salen de current)
        for seg in airspace.nav_segments:
            if seg.origin_number == current.number:
                neighbor = next((p for p in airspace.nav_points
                                 if p.number == seg.destination_number), None)
                if neighbor and neighbor.number not in visited:
                    queue.append(neighbor)

    return reachable


def FindShortestNavPath(airspace, start_id, end_id):
    """
    Encuentra el camino más corto entre dos puntos de navegación usando A*

    Args:
        airspace (AirSpace): El espacio aéreo completo
        start_id (int): Número del punto de inicio
        end_id (int): Número del punto de destino

    Returns:
        Path: Objeto con los puntos del camino y el costo total, o None si no hay camino
    """
    import heapq

    class Path:
        def __init__(self, points, cost):
            self.points = points  # Lista de NavPoint en orden del camino
            self.cost = cost  # Costo total acumulado del camino

    # Verificar que los puntos existen
    start_point = next((p for p in airspace.nav_points if p.number == start_id), None)
    end_point = next((p for p in airspace.nav_points if p.number == end_id), None)

    if not start_point or not end_point:
        return None

    # Priority queue: (f_score, path_object)
    open_set = []
    heapq.heappush(open_set, (0, Path([start_point], 0)))

    # Diccionario para almacenar los mejores costos conocidos
    g_scores = {start_point.number: 0}

    while open_set:
        _, current_path = heapq.heappop(open_set)
        last_point = current_path.points[-1]

        # Si llegamos al destino
        if last_point.number == end_id:
            return current_path

        # Explorar vecinos
        for seg in airspace.nav_segments:
            if seg.origin_number == last_point.number:
                neighbor = next((p for p in airspace.nav_points
                                 if p.number == seg.destination_number), None)
                if not neighbor:
                    continue

                # Calcular nuevo costo acumulado
                tentative_g_score = g_scores[last_point.number] + seg.distance

                if neighbor.number not in g_scores or tentative_g_score < g_scores[neighbor.number]:
                    g_scores[neighbor.number] = tentative_g_score

                    # Heurística: distancia euclidiana al destino (en grados)
                    h_score = ((neighbor.latitude - end_point.latitude) ** 2 +
                               (neighbor.longitude - end_point.longitude) ** 2) ** 0.5
                    f_score = tentative_g_score + h_score

                    new_path = Path(current_path.points + [neighbor], tentative_g_score)
                    heapq.heappush(open_set, (f_score, new_path))

    return None


# Funciones auxiliares para facilitar el testing
def PrintAirspaceSummary(airspace):
    """Muestra un resumen del espacio aéreo cargado"""
    print(f"Puntos de navegación: {len(airspace.nav_points)}")
    print(f"Segmentos: {len(airspace.nav_segments)}")
    print(f"Aeropuertos: {len(airspace.nav_airports)}")
    print("\nPrimeros 5 puntos de navegación:")
    for p in airspace.nav_points[:5]:
        print(f"{p.number} {p.name} ({p.latitude}, {p.longitude})")

    print("\nPrimeros 5 segmentos:")
    for s in airspace.nav_segments[:5]:
        print(f"{s.origin_number} -> {s.destination_number} ({s.distance} km)")

    print("\nAeropuertos:")
    for a in airspace.nav_airports:
        print(f"{a.name} - SIDs: {len(a.sids)}, STARs: {len(a.stars)}")


if __name__ == "__main__":
    # Ejemplo de uso para testing
    print("Probando carga de espacio aéreo...")
    airspace = LoadAirspace("Cat_nav.txt", "Cat_seg.txt", "Cat_ger.txt")
    PrintAirspaceSummary(airspace)

    # Probar alcanzabilidad
    print("\nProbando alcanzabilidad desde el punto 5129 (GODOX)...")
    reachable = GetReachableNavPoints(airspace, 5129)
    print(f"Puntos alcanzables: {len(reachable)}")
    for p in reachable[:5]:
        print(f"- {p.name} ({p.number})")

    # Probar camino más corto
    print("\nProbando camino más corto entre 5129 (GODOX) y 6063 (IZA D)...")
    path = FindShortestNavPath(airspace, 5129, 6063)
    if path:
        print(f"Camino encontrado ({path.cost:.2f} km):")
        for p in path.points:
            print(f"- {p.name} ({p.number})")
    else:
        print("No se encontró camino")
