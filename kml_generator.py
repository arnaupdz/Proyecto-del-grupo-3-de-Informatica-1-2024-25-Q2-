import simplekml
from pathlib import Path

class KMLGenerator:
    def __init__(self):
        self.kml = simplekml.Kml()
        # Estilos predefinidos como objetos Style, no como IDs
        self.styles = {
            'normal_point': self._make_point_style('ff00aaff', 0.8, 'http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png'),
            'highlight_point': self._make_point_style('ff0000ff', 1.2, 'http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png'),
            'airport': self._make_point_style('ffaa00ff', 1.5, 'http://maps.google.com/mapfiles/kml/shapes/airports.png'),
            'normal_line': self._make_line_style('7f00ff00', 2),
            'highlight_line': self._make_line_style('7fff0000', 4)
        }

    def _make_point_style(self, color, scale, icon_href):
        style = simplekml.Style()
        style.iconstyle.color = color
        style.iconstyle.scale = scale
        style.iconstyle.icon.href = icon_href
        return style

    def _make_line_style(self, color, width):
        style = simplekml.Style()
        style.linestyle.color = color
        style.linestyle.width = width
        return style

    def add_point(self, name, lon, lat, description="", highlight=False, altitude=0):
        point = self.kml.newpoint(
            name=name,
            coords=[(lon, lat, altitude)],
            description=description
        )
        point.style = self.styles['highlight_point'] if highlight else self.styles['normal_point']
        return point

    def add_line(self, name, points, description="", highlight=False):
        linestring = self.kml.newlinestring(
            name=name,
            coords=points,
            description=description,
            altitudemode=simplekml.AltitudeMode.clamptoground
        )
        linestring.style = self.styles['highlight_line'] if highlight else self.styles['normal_line']
        return linestring

    def add_path(self, name, points, description=""):
        folder = self.kml.newfolder(name=name, description=description)
        # Añadir puntos
        for i, point in enumerate(points):
            pt = folder.newpoint(
                name=point['name'],
                coords=[(point['lon'], point['lat'])],
                description=f"Point {i + 1} of path"
            )
            pt.style = self.styles['normal_point']
        # Añadir línea conectando los puntos
        coords = [(p['lon'], p['lat']) for p in points]
        line = folder.newlinestring(
            name=f"{name}_path",
            coords=coords,
            description=f"Path connecting {len(points)} points"
        )
        line.style = self.styles['highlight_line']
        return folder

    def add_airport(self, name, lon, lat, sids=[], stars=[], description=""):
        folder = self.kml.newfolder(name=f"Airport {name}", description=description)
        # Punto principal del aeropuerto
        airport = folder.newpoint(
            name=f"Airport {name}",
            coords=[(lon, lat)],
            description=description
        )
        airport.style = self.styles['airport']
        # Añadir SIDs
        if sids:
            sid_folder = folder.newfolder(name=f"SIDs for {name}")
            for sid in sids:
                sid_folder.newpoint(
                    name=f"SID {sid['name']}",
                    coords=[(sid['lon'], sid['lat'])],
                    description=f"Departure route for {name}"
                ).style = self.styles['normal_point']
        # Añadir STARs
        if stars:
            star_folder = folder.newfolder(name=f"STARs for {name}")
            for star in stars:
                star_folder.newpoint(
                    name=f"STAR {star['name']}",
                    coords=[(star['lon'], star['lat'])],
                    description=f"Arrival route for {name}"
                ).style = self.styles['normal_point']
        return folder

    def save_to_file(self, filename):
        filename = Path(filename).with_suffix('.kml')
        self.kml.save(filename)
        return str(filename)

    def generate_graph_kml(self, graph, filename):
        for node in graph.nodes:
            self.add_point(
                name=node.name,
                lon=node.x,
                lat=node.y,
                description=f"Node {node.name} at ({node.x}, {node.y})"
            )
        for seg in graph.segments:
            self.add_line(
                name=f"{seg.origin.name}-{seg.destination.name}",
                points=[
                    (seg.origin.x, seg.origin.y),
                    (seg.destination.x, seg.destination.y)
                ],
                description=f"Segment with cost {seg.cost:.2f}"
            )
        return self.save_to_file(filename)

    def generate_airspace_kml(self, airspace, filename):
        for point in airspace.nav_points:
            self.add_point(
                name=f"{point.name} ({point.number})",
                lon=point.longitude,
                lat=point.latitude,
                description=f"NavPoint {point.name} at ({point.latitude:.6f}, {point.longitude:.6f})"
            )
        for seg in airspace.nav_segments:
            origin = next(p for p in airspace.nav_points if p.number == seg.origin_number)
            dest = next(p for p in airspace.nav_points if p.number == seg.destination_number)
            self.add_line(
                name=f"{origin.name}-{dest.name}",
                points=[
                    (origin.longitude, origin.latitude),
                    (dest.longitude, dest.latitude)
                ],
                description=f"Airway segment: {seg.distance:.2f} km"
            )
        for airport in airspace.nav_airports:
            if airport.sids:
                first_sid = next(p for p in airspace.nav_points if p.number == airport.sids[0])
                sids_data = [
                    {'name': p.name, 'lon': p.longitude, 'lat': p.latitude}
                    for p in airspace.nav_points if p.number in airport.sids
                ]
                stars_data = [
                    {'name': p.name, 'lon': p.longitude, 'lat': p.latitude}
                    for p in airspace.nav_points if p.number in airport.stars
                ]
                self.add_airport(
                    name=airport.name,
                    lon=first_sid.longitude,
                    lat=first_sid.latitude,
                    sids=sids_data,
                    stars=stars_data,
                    description=f"Airport {airport.name} with {len(airport.sids)} SIDs and {len(airport.stars)} STARs"
                )
        return self.save_to_file(filename)

# Ejemplo de uso
if __name__ == "__main__":
    kml_gen = KMLGenerator()
    kml_gen.add_point("Punto 1", -0.107331, 51.503297, "London")
    kml_gen.add_point("Punto 2", 2.352222, 48.856613, "Paris", highlight=True)
    kml_gen.add_line(
        "Ruta Londres-París",
        [(-0.107331, 51.503297), (2.352222, 48.856613)],
        "Ejemplo de ruta entre ciudades"
    )
    output_file = kml_gen.save_to_file("ejemplo.kml")
    print(f"Archivo KML generado: {output_file}")
