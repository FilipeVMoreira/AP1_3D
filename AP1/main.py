import pygame
import math


# ============================================================
# CONFIGURAÇÕES
# ============================================================

WIDTH = 1200
HEIGHT = 700
FPS = 60


# ============================================================
# CARREGADOR DE OBJ
# ============================================================

def load_obj(filename):
    vertices = []
    faces = []

    with open(filename, "r", encoding="utf-8") as file:

        for line in file:

            line = line.strip()

            if not line or line.startswith("#"):
                continue

            parts = line.split()

            # -------------------------
            # Vértice
            # -------------------------

            if parts[0] == "v":

                x = float(parts[1])
                y = float(parts[2])
                z = float(parts[3])

                vertices.append((x, y, z))

            # -------------------------
            # Face
            # -------------------------

            elif parts[0] == "f":

                face = []

                for part in parts[1:]:

                    # Pode ser:
                    # 1
                    # 1/2
                    # 1/2/3
                    # 1//3

                    vertex_index = part.split("/")[0]

                    index = int(vertex_index)

                    # OBJ começa em 1
                    # Python começa em 0
                    face.append(index - 1)

                faces.append(face)

    return vertices, faces


# ============================================================
# TRANSFORMAÇÃO
# ============================================================

def rotate_x(vertex, angle):

    x, y, z = vertex

    cos_a = math.cos(angle)
    sin_a = math.sin(angle)

    y2 = y * cos_a - z * sin_a
    z2 = y * sin_a + z * cos_a

    return x, y2, z2


def rotate_y(vertex, angle):

    x, y, z = vertex

    cos_a = math.cos(angle)
    sin_a = math.sin(angle)

    x2 = x * cos_a + z * sin_a
    z2 = -x * sin_a + z * cos_a

    return x2, y, z2


def rotate_z(vertex, angle):

    x, y, z = vertex

    cos_a = math.cos(angle)
    sin_a = math.sin(angle)

    x2 = x * cos_a - y * sin_a
    y2 = x * sin_a + y * cos_a

    return x2, y2, z


def transform_vertex(
    vertex,
    position=(0, 0, 0),
    scale=(1, 1, 1),
    rotation=(0, 0, 0)
):

    x, y, z = vertex

    # ESCALA
    x *= scale[0]
    y *= scale[1]
    z *= scale[2]

    # ROTAÇÃO
    x, y, z = rotate_x((x, y, z), rotation[0])
    x, y, z = rotate_y((x, y, z), rotation[1])
    x, y, z = rotate_z((x, y, z), rotation[2])

    # TRANSLAÇÃO
    x += position[0]
    y += position[1]
    z += position[2]

    return x, y, z


# ============================================================
# PROJEÇÃO 3D -> 2D
# ============================================================

def project(vertex):

    x, y, z = vertex

    # Distância da câmera
    camera_distance = 8

    z += camera_distance

    # Atrás da câmera
    if z <= 0.1:
        return None

    focal_length = 500

    screen_x = WIDTH / 2 + (x * focal_length / z)
    screen_y = HEIGHT / 2 - (y * focal_length / z)

    return int(screen_x), int(screen_y)


# ============================================================
# DESENHAR MODELO
# ============================================================

def draw_model(
    screen,
    vertices,
    faces,
    position=(0, 0, 0),
    scale=(1, 1, 1),
    rotation=(0, 0, 0),
    color=(150, 150, 150)
):

    transformed = []

    # Transformar todos os vértices
    for vertex in vertices:

        transformed_vertex = transform_vertex(
            vertex,
            position,
            scale,
            rotation
        )

        transformed.append(transformed_vertex)

    # Projetar vértices
    projected = []

    for vertex in transformed:

        projected.append(
            project(vertex)
        )

    # --------------------------------------------------------
    # Ordenar faces pela profundidade
    # --------------------------------------------------------

    faces_to_draw = []

    for face in faces:

        points = []

        depth = 0

        valid = True

        for index in face:

            point = projected[index]

            if point is None:
                valid = False
                break

            points.append(point)

            depth += transformed[index][2]

        if valid and len(points) >= 3:

            depth /= len(face)

            faces_to_draw.append(
                (depth, points)
            )

    # Faces mais distantes primeiro
    faces_to_draw.sort(
        key=lambda item: item[0],
        reverse=True
    )

    # --------------------------------------------------------
    # Desenhar
    # --------------------------------------------------------

    for depth, points in faces_to_draw:

        pygame.draw.polygon(
            screen,
            color,
            points
        )

        # Contorno para visualizar melhor o modelo
        pygame.draw.polygon(
            screen,
            (40, 40, 40),
            points,
            1
        )


# ============================================================
# PROGRAMA PRINCIPAL
# ============================================================

def main():

    pygame.init()

    screen = pygame.display.set_mode(
        (WIDTH, HEIGHT)
    )

    pygame.display.set_caption(
        "AP1 - Visualizador de Modelos 3D"
    )

    clock = pygame.time.Clock()

    # ========================================================
    # CARREGAR MODELOS
    # ========================================================

    stalagmite_vertices, stalagmite_faces = load_obj(
        "models/Stalagmite_Medium0.obj"
    )

    bat_vertices, bat_faces = load_obj(
        "models/bat.obj"
    )

    rock_vertices, rock_faces = load_obj(
        "models/rockmaterial.obj"
    )

    print(
        "Estalagmite:",
        len(stalagmite_vertices),
        "vertices /",
        len(stalagmite_faces),
        "faces"
    )

    print(
        "Morcego:",
        len(bat_vertices),
        "vertices /",
        len(bat_faces),
        "faces"
    )

    print(
        "Rocha:",
        len(rock_vertices),
        "vertices /",
        len(rock_faces),
        "faces"
    )

    # ========================================================
    # LOOP
    # ========================================================

    running = True

    while running:

        dt = clock.tick(FPS) / 1000

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

        # ====================================================
        # FUNDO
        # ====================================================

        screen.fill((15, 15, 20))

        # ====================================================
        # ESTALAGMITE
        # ====================================================

        draw_model(
            screen,
            stalagmite_vertices,
            stalagmite_faces,

            position=(-3, -2, 5),

            scale=(0.2, 0.2, 0.2),

            rotation=(0, 0, 0),

            color=(120, 120, 120)
        )

        # ====================================================
        # MORCEGO
        # ====================================================

        draw_model(
            screen,
            bat_vertices,
            bat_faces,

            position=(0, 0, 5),

            scale=(3, 3, 3),

            rotation=(0, 0, 0),

            color=(70, 60, 80)
        )

        # ====================================================
        # ROCHA
        # ====================================================

        draw_model(
            screen,
            rock_vertices,
            rock_faces,

            position=(3, -2, 5),

            scale=(5, 5, 5),

            rotation=(0, 0, 0),

            color=(100, 90, 80)
        )

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()