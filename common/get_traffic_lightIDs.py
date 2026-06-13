import carla
import time

def draw_traffic_light_ids():
    # Verbindung zu CARLA herstellen
    client = carla.Client('localhost', 2000)
    client.set_timeout(10.0)
    world = client.get_world()
    debug = world.debug

    # Alle Ampeln aus der Welt holen
    traffic_lights = world.get_actors().filter('*traffic_light*')
    print(f"{len(traffic_lights)} Ampeln gefunden. IDs werden in der Welt angezeigt...")

    # Textfarbe (RGB): Knalliges Rot/Pink, damit man es gut sieht
    color = carla.Color(255, 0, 100)

    # Die IDs für 30 Sekunden in der Welt einblenden
    anzahl_sekunden = 30.0

    for tl in traffic_lights:
        # Position der Ampel holen
        loc = tl.get_location()
        
        # Den Text etwas nach oben verschieben (Z-Achse + 3 Meter), 
        # damit er schön über der Ampel schwebt
        text_pos = carla.Location(x=loc.x, y=loc.y, z=loc.z + 3.0)
        
        # Text zusammenbauen (Actor ID und optionale OpenDRIVE ID)
        text = f"ID: {tl.id} (OpenDRIVE: {tl.get_opendrive_id()})"
        
        # Den Text in die 3D-Welt zeichnen
        debug.draw_string(
            text_pos, 
            text, 
            draw_shadow=True, 
            color=color, 
            life_time=anzahl_sekunden,
            persistent_lines=False
        )

if __name__ == '__main__':
    draw_traffic_light_ids()