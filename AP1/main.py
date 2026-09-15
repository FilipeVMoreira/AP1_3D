import pygame
import math
import random
import os

# ============================================================
# CONFIGURAÇÕES GERAIS
# ============================================================
WIDTH = 1200
HEIGHT = 700
FPS = 60

COLOR_BG = (12, 14, 22)
COLOR_HUD_BG = (20, 25, 38, 200)
COLOR_TEXT_PRIMARY = (235, 240, 250)
COLOR_TEXT_SECONDARY = (160, 175, 200)
COLOR_ACCENT = (100, 210, 255)
COLOR_WARN = (255, 180, 80)
COLOR_GREEN = (100, 230, 150)


# ============================================================
# CARREGADOR DE OBJ COM FALLBACK PROCEDURAL
# ============================================================
def create_fallback_mesh(mesh_type):
    """Gera uma malha simples caso o OBJ não seja encontrado."""
    if mesh_type == "estalagmite":
        vertices = [
            (0.0, 1.0, 0.0),
            (-0.6, -1.0, -0.6),
            (0.6, -1.0, -0.6),
            (0.6, -1.0, 0.6),
            (-0.6, -1.0, 0.6)
        ]
        faces = [
            [0, 1, 2], [0, 2, 3], [0, 3, 4],
            [0, 4, 1], [1, 2, 3], [1, 3, 4]
        ]

    elif mesh_type == "morcego":
        # Fallback apenas para o corpo caso os OBJ não existam.
        vertices = [
            (0, 0, 0),
            (-0.9, 0.4, -0.3),
            (-0.9, -0.4, -0.3),
            (0.9, 0.4, -0.3),
            (0.9, -0.4, -0.3)
        ]
        faces = [[0, 1, 2], [0, 3, 4]]

    elif mesh_type == "asa":
        # Fallback simples para uma asa.
        vertices = [
            (0, 0, 0),
            (-2.0, 0.8, 0),
            (-2.5, 0.0, 0),
            (-1.8, -0.8, 0),
            (-0.8, -0.3, 0)
        ]
        faces = [[0, 1, 4], [1, 2, 4], [2, 3, 4]]

    elif mesh_type == "rocha":
        vertices = [
            (-0.8, -0.6, -0.6), (0.8, -0.6, -0.6),
            (0.8, 0.6, -0.6), (-0.8, 0.6, -0.6),
            (-0.7, -0.4, 0.6), (0.7, -0.4, 0.6),
            (0.7, 0.4, 0.6), (-0.7, 0.4, 0.6)
        ]
        faces = [
            [0, 1, 2, 3], [4, 5, 6, 7],
            [0, 1, 5, 4], [2, 3, 7, 6],
            [1, 2, 6, 5], [3, 0, 4, 7]
        ]

    else:
        # Cristal -> octaedro
        vertices = [
            (0, 1.0, 0), (0, -1.0, 0),
            (1.0, 0, 0), (0, 0, 1.0),
            (-1.0, 0, 0), (0, 0, -1.0)
        ]
        faces = [
            [0, 2, 3], [0, 3, 4], [0, 4, 5], [0, 5, 2],
            [1, 3, 2], [1, 4, 3], [1, 5, 4], [1, 2, 5]
        ]

    return vertices, faces


def load_obj(filename, mesh_fallback_type):
    """Carrega somente vértices e faces do arquivo OBJ."""
    if os.path.exists(filename):
        vertices = []
        faces = []

        try:
            with open(filename, "r", encoding="utf-8") as file:
                for line in file:
                    line = line.strip()

                    if not line or line.startswith("#"):
                        continue

                    parts = line.split()

                    if parts[0] == "v":
                        try:
                            x, y, z = (
                                float(parts[1]),
                                float(parts[2]),
                                float(parts[3])
                            )
                            vertices.append((x, y, z))
                        except Exception:
                            continue

                    elif parts[0] == "f":
                        face = []

                        for part in parts[1:]:
                            vertex_index = part.split("/")[0]

                            try:
                                face.append(int(vertex_index) - 1)
                            except Exception:
                                pass

                        if face:
                            faces.append(face)

            if vertices and faces:
                print(f"Modelo carregado: {filename}")
                print(f"  Vértices: {len(vertices)} | Faces: {len(faces)}")
                return vertices, faces

        except Exception as e:
            print(f"Aviso ao carregar {filename}: {e}")

    print(
        f"Modelo {filename} não encontrado. "
        f"Usando malha procedural: {mesh_fallback_type}"
    )
    return create_fallback_mesh(mesh_fallback_type)


# ============================================================
# TRANSFORMAÇÕES GEOMÉTRICAS
# ============================================================
def rotate_x(vertex, angle):
    x, y, z = vertex
    cos_a, sin_a = math.cos(angle), math.sin(angle)
    return x, y * cos_a - z * sin_a, y * sin_a + z * cos_a


def rotate_y(vertex, angle):
    x, y, z = vertex
    cos_a, sin_a = math.cos(angle), math.sin(angle)
    return x * cos_a + z * sin_a, y, -x * sin_a + z * cos_a


def rotate_z(vertex, angle):
    x, y, z = vertex
    cos_a, sin_a = math.cos(angle), math.sin(angle)
    return x * cos_a - y * sin_a, x * sin_a + y * cos_a, z


def apply_scale(vertex, scale):
    x, y, z = vertex

    if hasattr(scale, "__len__"):
        sx = scale[0]
        sy = scale[1]
        sz = scale[2] if len(scale) > 2 else sx
    else:
        sx = sy = sz = scale

    return x * sx, y * sy, z * sz


def transform_vertex(
    vertex,
    position=(0, 0, 0),
    scale=(1, 1, 1),
    rotation=(0, 0, 0)
):
    """Escala -> rotação -> translação."""
    v = apply_scale(vertex, scale)

    rx, ry, rz = rotation

    v = rotate_x(v, rx)
    v = rotate_y(v, ry)
    v = rotate_z(v, rz)

    return (
        v[0] + position[0],
        v[1] + position[1],
        v[2] + position[2]
    )


def transform_vertex_pivot(
    vertex,
    position=(0, 0, 0),
    scale=(1, 1, 1),
    rotation=(0, 0, 0),
    pivot=(0, 0, 0)
):
    """
    Transformação usada nas asas.

    A asa é deslocada para o pivô, escalada/rotacionada,
    e depois o pivô é recolocado. Assim a rotação acontece
    na região onde a asa se liga ao corpo.
    """

    # Escala aplicada também ao pivô, pois o modelo inteiro
    # é escalado antes da transformação.
    v = apply_scale(vertex, scale)
    p = apply_scale(pivot, scale)

    # Transladar o vértice para o pivô.
    v = (
        v[0] - p[0],
        v[1] - p[1],
        v[2] - p[2]
    )

    rx, ry, rz = rotation

    v = rotate_x(v, rx)
    v = rotate_y(v, ry)
    v = rotate_z(v, rz)

    # Recolocar o pivô e depois posicionar o morcego na cena.
    v = (
        v[0] + p[0] + position[0],
        v[1] + p[1] + position[1],
        v[2] + p[2] + position[2]
    )

    return v


# ============================================================
# PROJEÇÃO PERSPECTIVA
# ============================================================
def project(vertex, camera_pos=(0, 0, 0), focal_length=520):
    x, y, z = vertex
    cx, cy, cz = camera_pos

    x -= cx
    y -= cy
    z -= cz

    if z <= 0.1:
        return None

    screen_x = WIDTH / 2 + (x * focal_length / z)
    screen_y = HEIGHT / 2 - (y * focal_length / z)

    return int(screen_x), int(screen_y), z


# ============================================================
# RENDERIZAÇÃO
# ============================================================
def draw_model(
    screen,
    vertices,
    faces,
    position=(0, 0, 0),
    scale=(1, 1, 1),
    rotation=(0, 0, 0),
    color=(150, 150, 150),
    camera_pos=(0, 0, 0),
    wireframe=False,
    pivot=None
):
    """
    Desenha uma malha 3D usando projeção perspectiva e algoritmo
    do pintor.

    Se pivot for informado, a rotação será feita em torno dele.
    """

    if pivot is None:
        transformed = [
            transform_vertex(v, position, scale, rotation)
            for v in vertices
        ]
    else:
        transformed = [
            transform_vertex_pivot(
                v,
                position,
                scale,
                rotation,
                pivot
            )
            for v in vertices
        ]

    projected = [project(v, camera_pos) for v in transformed]

    faces_to_draw = []

    for face in faces:
        points = []
        depth = 0.0
        valid = True

        for idx in face:
            if idx < 0 or idx >= len(projected):
                valid = False
                break

            proj = projected[idx]

            if proj is None:
                valid = False
                break

            points.append((proj[0], proj[1]))
            depth += proj[2]

        if valid and len(points) >= 3:
            depth /= len(face)
            faces_to_draw.append((depth, points))

    # Algoritmo do Pintor
    faces_to_draw.sort(key=lambda item: item[0], reverse=True)

    for depth, points in faces_to_draw:
        if not wireframe:
            pygame.draw.polygon(screen, color, points)

            stroke_color = tuple(
                max(0, c - 40) for c in color
            )

            pygame.draw.polygon(
                screen,
                stroke_color,
                points,
                1
            )
        else:
            pygame.draw.polygon(
                screen,
                COLOR_ACCENT,
                points,
                1
            )


# ============================================================
# INTERFACE / HUD
# ============================================================
def draw_hud(
    screen,
    font,
    font_small,
    anim_running,
    time_elapsed,
    camera_mode,
    wireframe_mode
):
    hud_surface = pygame.Surface(
        (WIDTH, 110),
        pygame.SRCALPHA
    )
    hud_surface.fill(COLOR_HUD_BG)
    screen.blit(hud_surface, (0, 0))

    title = font.render(
        "Mundo Virtual Animado — Caverna Sombria (AP1)",
        True,
        COLOR_TEXT_PRIMARY
    )
    screen.blit(title, (20, 12))

    state_str = "RODANDO" if anim_running else "PAUSADO"
    state_color = COLOR_GREEN if anim_running else COLOR_WARN

    state_text = font_small.render(
        f"Estado: {state_str}",
        True,
        state_color
    )
    screen.blit(state_text, (20, 42))

    time_text = font_small.render(
        f"Tempo: {time_elapsed:.1f}s",
        True,
        COLOR_TEXT_SECONDARY
    )
    screen.blit(time_text, (180, 42))

    cam_str = (
        "Geral (Visão Ampla)"
        if camera_mode == 0
        else "Foco no Morcego"
    )

    cam_text = font_small.render(
        f"Câmera: {cam_str}",
        True,
        COLOR_TEXT_SECONDARY
    )
    screen.blit(cam_text, (320, 42))

    vis_str = (
        "Arame (Wireframe)"
        if wireframe_mode
        else "Sólido (Polígonos)"
    )

    vis_text = font_small.render(
        f"Visual: {vis_str}",
        True,
        COLOR_TEXT_SECONDARY
    )
    screen.blit(vis_text, (550, 42))

    cycle_progress = (time_elapsed % 10.0) / 10.0

    pygame.draw.rect(
        screen,
        (50, 60, 80),
        (20, 68, 700, 8),
        border_radius=4
    )

    pygame.draw.rect(
        screen,
        COLOR_ACCENT,
        (20, 68, int(700 * cycle_progress), 8),
        border_radius=4
    )

    cmd_text = font_small.render(
        "[ESPAÇO] Iniciar/Pausar  |  "
        "[R] Reiniciar  |  "
        "[C] Alternar Câmera  |  "
        "[M] Modo Arame/Sólido",
        True,
        COLOR_TEXT_PRIMARY
    )

    screen.blit(cmd_text, (20, 84))


# ============================================================
# CENÁRIO
# ============================================================
def draw_ground(screen, camera_pos):
    corners = [
        (-12.0, -2.5, 3.0),
        (12.0, -2.5, 3.0),
        (12.0, -2.5, 30.0),
        (-12.0, -2.5, 30.0)
    ]

    proj = [
        project(c, camera_pos)
        for c in corners
    ]

    if all(p is not None for p in proj):
        pts = [(p[0], p[1]) for p in proj]

        pygame.draw.polygon(
            screen,
            (28, 34, 45),
            pts
        )

    for x in range(-10, 11, 2):
        p1 = project(
            (x, -2.5, 3.0),
            camera_pos
        )
        p2 = project(
            (x, -2.5, 30.0),
            camera_pos
        )

        if p1 and p2:
            pygame.draw.line(
                screen,
                (30, 35, 50),
                (p1[0], p1[1]),
                (p2[0], p2[1]),
                1
            )

    for z in range(3, 31, 2):
        p1 = project(
            (-12.0, -2.5, z),
            camera_pos
        )
        p2 = project(
            (12.0, -2.5, z),
            camera_pos
        )

        if p1 and p2:
            pygame.draw.line(
                screen,
                (30, 35, 50),
                (p1[0], p1[1]),
                (p2[0], p2[1]),
                1
            )


def draw_cave(screen):
    w, h = screen.get_size()

    cave_color = (10, 12, 16)
    pygame.draw.rect(
        screen,
        cave_color,
        (0, 0, w, int(h * 0.55))
    )

    mouth_color = (18, 20, 28)

    mouth_rect = pygame.Rect(
        w * 0.05,
        -h * 0.2,
        w * 0.9,
        h * 0.9
    )

    pygame.draw.ellipse(
        screen,
        mouth_color,
        mouth_rect
    )


def clamp(v, a, b):
    return max(a, min(b, v))


def clamp_scene_positions(
    instances,
    x_min=-11.0,
    x_max=11.0,
    z_min=3.5,
    z_max=28.0,
    y_min=-2.4,
    y_max=3.5
):
    for inst in instances:
        pos = inst.get("pos")

        if isinstance(pos, (list, tuple)) and len(pos) >= 3:
            p = list(pos)

            p[0] = clamp(p[0], x_min, x_max)
            p[1] = clamp(p[1], y_min, y_max)
            p[2] = clamp(p[2], z_min, z_max)

            inst["pos"] = p


# ============================================================
# PROGRAMA PRINCIPAL
# ============================================================
def main():
    pygame.init()

    screen = pygame.display.set_mode(
        (WIDTH, HEIGHT)
    )

    pygame.display.set_caption(
        "AP1 - Caverna Sombria - Mundo Virtual Animado"
    )

    clock = pygame.time.Clock()

    font = pygame.font.SysFont(
        "Arial",
        22,
        bold=True
    )

    font_small = pygame.font.SysFont(
        "Arial",
        16
    )

    # ========================================================
    # CARREGAMENTO DOS MODELOS
    # ========================================================

    stalagmite_v, stalagmite_f = load_obj(
        "models/Stalagmite_Medium0.obj",
        "estalagmite"
    )

    rock_v, rock_f = load_obj(
        "models/rockmaterial.obj",
        "rocha"
    )

    # NOVO: o morcego agora é composto por 3 OBJ.
    bat_corpo_v, bat_corpo_f = load_obj(
        "models/bat_corpo.obj",
        "morcego"
    )

    bat_asa_esq_v, bat_asa_esq_f = load_obj(
        "models/bat_asa_esquerda.obj",
        "asa"
    )

    bat_asa_dir_v, bat_asa_dir_f = load_obj(
        "models/bat_asa_direita.obj",
        "asa"
    )

    random.seed(1)

    # ========================================================
    # INSTÂNCIAS DA CENA
    # ========================================================

    s1 = random.uniform(0.30, 0.45)
    s2 = random.uniform(0.30, 0.45)
    s3 = random.uniform(0.30, 0.45)

    # O morcego agora possui 3 partes.
    morcego_pos = [0.0, 1.0, 5.0]

    instancias = [
        {
            "modelo": "estalagmite",
            "v": stalagmite_v,
            "f": stalagmite_f,
            "pos": [-4.0, -2.5, 7.0],
            "scale": [
                0.25 * s1,
                0.35 * s1,
                0.25 * s1
            ],
            "rot": [0, 0.2, 0],
            "color": (110, 110, 120)
        },

        {
            "modelo": "estalagmite",
            "v": stalagmite_v,
            "f": stalagmite_f,
            "pos": [3.5, -2.5, 8.5],
            "scale": [
                0.35 * s2,
                0.50 * s2,
                0.35 * s2
            ],
            "rot": [0, -0.5, 0],
            "color": (95, 95, 105)
        },

        {
            "modelo": "estalagmite_pai",
            "v": stalagmite_v,
            "f": stalagmite_f,
            "pos": [-0.5, 2.8, 6.5],
            "scale": [
                0.3 * s3,
                0.4 * s3,
                0.3 * s3
            ],
            "rot": [0, 0.8, 0],
            "color": (120, 115, 130)
        },

        {
            "modelo": "rocha",
            "v": rock_v,
            "f": rock_f,
            "pos": [1.5, -2.2, 5.5],
            "scale": [1.2, 1.2, 1.2],
            "rot": [0, 0, 0],
            "color": (100, 85, 75)
        },

        # Corpo do morcego
        {
            "modelo": "morcego_corpo",
            "v": bat_corpo_v,
            "f": bat_corpo_f,
            "pos": morcego_pos,
            "scale": [0.8, 0.8, 0.8],
            "rot": [0, 0, 0],
            "color": (75, 60, 90)
        },

        # Asa esquerda
        {
            "modelo": "morcego_asa_esquerda",
            "v": bat_asa_esq_v,
            "f": bat_asa_esq_f,
            "pos": morcego_pos,
            "scale": [0.8, 0.8, 0.8],
            "rot": [0, 0, 0],
            "pivot": (-0.18, 0.0, 0.0),
            "color": (65, 50, 80)
        },

        # Asa direita
        {
            "modelo": "morcego_asa_direita",
            "v": bat_asa_dir_v,
            "f": bat_asa_dir_f,
            "pos": morcego_pos,
            "scale": [0.8, 0.8, 0.8],
            "rot": [0, 0, 0],
            "pivot": (0.18, 0.0, 0.0),
            "color": (65, 50, 80)
        }
    ]

    clamp_scene_positions(instancias)

    cameras = [
        [0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0]
    ]

    camera_mode = 0
    anim_running = False
    time_elapsed = 0.0
    wireframe_mode = False

    running = True

    # ========================================================
    # LOOP PRINCIPAL
    # ========================================================
    while running:

        dt = clock.tick(FPS) / 1000.0

        # ----------------------------------------------------
        # EVENTOS
        # ----------------------------------------------------
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    running = False

                elif event.key == pygame.K_SPACE:
                    anim_running = not anim_running

                elif event.key == pygame.K_r:
                    time_elapsed = 0.0

                elif event.key == pygame.K_c:
                    camera_mode = (
                        camera_mode + 1
                    ) % len(cameras)

                elif event.key == pygame.K_m:
                    wireframe_mode = not wireframe_mode

        # ----------------------------------------------------
        # TEMPO DA ANIMAÇÃO
        # ----------------------------------------------------
        if anim_running:
            time_elapsed += dt

        t = time_elapsed

        # ====================================================
        # ANIMAÇÃO DO MORCEGO
        # ====================================================

        morcego_corpo = instancias[4]
        asa_esquerda = instancias[5]
        asa_direita = instancias[6]

        # Movimento do morcego pela caverna.
        nova_pos = [
            math.sin(t * 1.5) * 2.5,
            0.8 + math.cos(t * 3.0) * 0.4,
            5.5 + math.sin(t * 2.0) * 1.0
        ]

        morcego_corpo["pos"] = nova_pos
        asa_esquerda["pos"] = nova_pos.copy()
        asa_direita["pos"] = nova_pos.copy()

        # Rotação geral do corpo.
        morcego_corpo["rot"] = (
            math.sin(t * 3.0) * 0.2,
            t * 1.5,
            math.cos(t * 2.0) * 0.15
        )

        # ====================================================
        # BATIMENTO DAS ASAS
        # ====================================================
        #
        # A função seno cria um movimento periódico.
        #
        # As asas fazem movimentos opostos:
        # esquerda:  +angulo
        # direita:   -angulo
        #
        # A rotação é aplicada no eixo Z, usando os pivôs
        # definidos na própria malha.
        # ====================================================

        flap_angle = math.sin(t * 6.0) * 0.65

        asa_esquerda["rot"] = (
            0.0,
            0.0,
            flap_angle
        )

        asa_direita["rot"] = (
            0.0,
            0.0,
            -flap_angle
        )

        # ====================================================
        # ANIMAÇÃO DA ROCHA
        # ====================================================

        rocha = instancias[3]

        base_x = 1.5

        rocha["pos"][0] = (
            base_x + math.sin(t * 1.0) * 3.5
        )

        rocha["pos"][1] = -2.2

        rocha["rot"] = (
            t * 4.0,
            0,
            0
        )

        clamp_scene_positions(instancias)

        # ====================================================
        # CÂMERA
        # ====================================================

        cameras[1] = [
            morcego_corpo["pos"][0] * 0.5,
            morcego_corpo["pos"][1] * 0.5,
            morcego_corpo["pos"][2] - 4.5
        ]

        # ====================================================
        # DESENHO
        # ====================================================

        screen.fill(COLOR_BG)

        cam_active = cameras[camera_mode]

        draw_cave(screen)
        draw_ground(screen, cam_active)

        for inst in instancias:

            draw_model(
                screen,
                inst["v"],
                inst["f"],
                position=inst.get(
                    "pos",
                    [0, 0, 6]
                ),
                scale=inst.get(
                    "scale",
                    [1, 1, 1]
                ),
                rotation=inst.get(
                    "rot",
                    [0, 0, 0]
                ),
                color=inst.get(
                    "color",
                    (200, 200, 200)
                ),
                camera_pos=cam_active,
                wireframe=wireframe_mode,
                pivot=inst.get("pivot")
            )

        draw_hud(
            screen,
            font,
            font_small,
            anim_running,
            time_elapsed,
            camera_mode,
            wireframe_mode
        )

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
