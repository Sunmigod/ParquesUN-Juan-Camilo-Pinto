import pygame
import random

# Configuración
display_size = 800
grid_size = 15
cell_size = display_size // grid_size

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 0, 0)
GREEN = (0, 200, 0)
BLUE = (0, 0, 200)
YELLOW = (200, 200, 0)
COLORS = [RED, GREEN, BLUE, YELLOW]
LIGHT_COLORS = [
    (255, 150, 150),  # Rojo claro
    (150, 255, 150),  # Verde claro
    (150, 150, 255),  # Azul claro
    (255, 255, 150)   # Amarillo claro
]

# Inicializar Pygame
pygame.init()
screen = pygame.display.set_mode((display_size, display_size))
pygame.display.set_caption("Parqués")
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)

dice_values = [1, 1]  # Dos dados con valores iniciales
dice_rolled = False
turn = 0
selected_piece = 0
game_over = False
winner = -1

# Definir casillas centrales del tablero (meta)
central_cell = (7, 7)

# Posiciones iniciales de las fichas (cárcel/casa)
initial_positions = {
    0: [(2, 2), (3, 2), (2, 3), (3, 3)],          # Rojo (esquina superior izquierda)
    1: [(11, 2), (12, 2), (11, 3), (12, 3)],      # Verde (esquina superior derecha)
    2: [(11, 11), (12, 11), (11, 12), (12, 12)],  # Azul (esquina inferior derecha)
    3: [(2, 11), (3, 11), (2, 12), (3, 12)]       # Amarillo (esquina inferior izquierda)
}
player_positions = {p: list(initial_positions[p]) for p in range(4)}

# Registro de vueltas dadas por cada ficha
piece_laps = {0: [0, 0, 0, 0], 1: [0, 0, 0, 0], 2: [0, 0, 0, 0], 3: [0, 0, 0, 0]}

# Casillas de salida para cada color 
starting_positions = [(6, 1), (13, 6), (8, 13), (1, 8)]

# Camino principal 
main_path = []

# Desde salida roja hacia la derecha
for i in range(6, 14):
    main_path.append((i, 1))

# Bajando por el lado derecho
for i in range(2, 14):
    main_path.append((13, i))

# Hacia la izquierda por abajo
for i in range(12, 0, -1):
    main_path.append((i, 13))

# Subiendo por el lado izquierdo
for i in range(12, 0, -1):
    main_path.append((1, i))

# Hacia la derecha arriba
for i in range(2, 6):
    main_path.append((i, 1))

# Caminos de llegada a meta 
home_paths = {
    0: [(i, 7) for i in range(1, 7)],           # Rojo: hacia la derecha en fila 7
    1: [(7, i) for i in range(13, 7, -1)],      # Verde: hacia arriba en columna 7
    2: [(i, 7) for i in range(13, 7, -1)],      # Azul: hacia la izquierda en fila 7
    3: [(7, i) for i in range(1, 7)]            # Amarillo: hacia abajo en columna 7
}

# Casillas seguras 
safe_spots = set([
    (6, 1),    # Salida roja
    (13, 6),   # Salida verde
    (8, 13),   # Salida azul
    (1, 8),    # Salida amarilla
    (10, 1),   # Seguro en camino común superior
    (13, 10),  # Seguro en camino común derecho
    (4, 13),   # Seguro en camino común inferior
    (1, 4)     # Seguro en camino común izquierdo
])

def draw_board():
    screen.fill(WHITE)
    
    # Dibujar las casas (cárceles) en las esquinas
    house_rects = [
        pygame.Rect(0, 0, 5*cell_size, 5*cell_size),                    # Rojo
        pygame.Rect(10*cell_size, 0, 5*cell_size, 5*cell_size),         # Verde
        pygame.Rect(10*cell_size, 10*cell_size, 5*cell_size, 5*cell_size),  # Azul
        pygame.Rect(0, 10*cell_size, 5*cell_size, 5*cell_size)          # Amarillo
    ]
    for i, rect in enumerate(house_rects):
        pygame.draw.rect(screen, LIGHT_COLORS[i], rect)
        pygame.draw.rect(screen, COLORS[i], rect, 3)  # Borde de color
    
    # Dibujar la cuadrícula
    for i in range(grid_size + 1):
        pygame.draw.line(screen, BLACK, (i * cell_size, 0), (i * cell_size, display_size))
        pygame.draw.line(screen, BLACK, (0, i * cell_size), (display_size, i * cell_size))
    
    # Dibujar el camino común
    for pos in main_path:
        x, y = pos
        pygame.draw.rect(screen, (220, 220, 220), 
                       (x * cell_size, y * cell_size, cell_size, cell_size))
    
    # Dibujar los caminos finales (llegada)
    for player, path in home_paths.items():
        for pos in path:
            x, y = pos
            pygame.draw.rect(screen, LIGHT_COLORS[player], 
                           (x * cell_size, y * cell_size, cell_size, cell_size))
    
    # Marcar el centro (meta) como un trofeo
    pygame.draw.rect(screen, (255, 215, 0),  # Dorado
                   (7 * cell_size, 7 * cell_size, cell_size, cell_size))
    pygame.draw.rect(screen, BLACK, 
                   (7 * cell_size, 7 * cell_size, cell_size, cell_size), 2)
    
    # Dibujar un trofeo simple en la meta
    x, y = central_cell
    # Base del trofeo
    pygame.draw.rect(screen, (218, 165, 32), 
                   (x * cell_size + cell_size//4, y * cell_size + 3*cell_size//5, 
                    cell_size//2, cell_size//5))
    # Copa del trofeo
    pygame.draw.rect(screen, (218, 165, 32), 
                   (x * cell_size + cell_size//3, y * cell_size + cell_size//5, 
                    cell_size//3, 2*cell_size//5))
    # Asas del trofeo
    pygame.draw.arc(screen, (218, 165, 32), 
                   [x * cell_size + cell_size//6, y * cell_size + cell_size//4, 
                    cell_size//4, cell_size//3], 1.5, 4.7, 2)
    pygame.draw.arc(screen, (218, 165, 32), 
                   [x * cell_size + cell_size//2 + cell_size//12, y * cell_size + cell_size//4, 
                    cell_size//4, cell_size//3], 4.7, 7.9, 2)
    
    text = small_font.render("META", True, BLACK)
    text_rect = text.get_rect(center=(x * cell_size + cell_size//2, y * cell_size + 4*cell_size//5))
    screen.blit(text, text_rect)
    
    # Marcar las casillas de salida
    for i, pos in enumerate(starting_positions):
        x, y = pos
        pygame.draw.rect(screen, COLORS[i], 
                       (x * cell_size, y * cell_size, cell_size, cell_size))
        text = small_font.render("SALIDA", True, WHITE)
        text_rect = text.get_rect(center=(x * cell_size + cell_size//2, y * cell_size + cell_size//2))
        screen.blit(text, text_rect)
    
    # Marcar las casillas seguras
    for pos in safe_spots:
        if pos not in starting_positions:  # No marcar las de salida dos veces
            x, y = pos
            pygame.draw.circle(screen, BLACK, 
                             (x * cell_size + cell_size//2, y * cell_size + cell_size//2), 
                             cell_size//6)
            text = small_font.render("SEGURO", True, WHITE)
            text_rect = text.get_rect(center=(x * cell_size + cell_size//2, y * cell_size + cell_size//2))
            screen.blit(text, text_rect)
            
    # Mostrar el recorrido de las fichas amarillas (como ejemplo)
    if turn == 3:  # Si es el turno amarillo, mostrar su recorrido
        # Trazar el recorrido desde la salida
        path_points = []
        
        # Añadir la posición de salida
        start_x, start_y = starting_positions[3]
        path_points.append((start_x * cell_size + cell_size//2, start_y * cell_size + cell_size//2))
        
        # Recorrer el camino principal hasta llegar a la entrada del camino final
        current_index = main_path.index(starting_positions[3])
        for i in range(1, len(main_path)):
            idx = (current_index + i) % len(main_path)
            x, y = main_path[idx]
            path_points.append((x * cell_size + cell_size//2, y * cell_size + cell_size//2))
            
            # Si llega a la salida de nuevo, entrar al camino final
            if main_path[idx] == starting_positions[3]:
                break
        
        # Añadir el camino final
        for pos in home_paths[3]:
            x, y = pos
            path_points.append((x * cell_size + cell_size//2, y * cell_size + cell_size//2))
        
        # Añadir la meta
        x, y = central_cell
        path_points.append((x * cell_size + cell_size//2, y * cell_size + cell_size//2))
        
        # Dibujar la línea del recorrido
        if len(path_points) > 1:
            pygame.draw.lines(screen, (255, 0, 255), False, path_points, 3)

def draw_pieces():
    for player, positions in player_positions.items():
        for i, pos in enumerate(positions):
            x, y = pos
            color = COLORS[player]
            pygame.draw.circle(screen, color, 
                             (x * cell_size + cell_size//2, y * cell_size + cell_size//2), 
                             cell_size//3)
            pygame.draw.circle(screen, WHITE, 
                             (x * cell_size + cell_size//2, y * cell_size + cell_size//2), 
                             cell_size//5)
            # Marcar la ficha seleccionada
            if player == turn and i == selected_piece:
                pygame.draw.circle(screen, BLACK, 
                                 (x * cell_size + cell_size//2, y * cell_size + cell_size//2), 
                                 cell_size//3 + 3, 3)
            # Dibujar número de ficha y vueltas
            piece_num = small_font.render(f"{i+1}", True, BLACK)
            text_rect = piece_num.get_rect(center=(x * cell_size + cell_size//2, y * cell_size + cell_size//2))
            screen.blit(piece_num, text_rect)
            
            # Mostrar número de vueltas cerca de cada ficha si no está en cárcel o meta
            if pos not in initial_positions[player] and pos != central_cell:
                lap_text = small_font.render(f"V:{piece_laps[player][i]}", True, BLACK)
                screen.blit(lap_text, (x * cell_size + cell_size//2 - 15, y * cell_size + cell_size//2 + 15))

def draw_dice():
    # Primer dado
    dice_rect1 = pygame.Rect(display_size//2 - 70, display_size - 100, 60, 60)
    pygame.draw.rect(screen, (220, 220, 220), dice_rect1)
    pygame.draw.rect(screen, BLACK, dice_rect1, 2)
    
    # Segundo dado
    dice_rect2 = pygame.Rect(display_size//2 + 10, display_size - 100, 60, 60)
    pygame.draw.rect(screen, (220, 220, 220), dice_rect2)
    pygame.draw.rect(screen, BLACK, dice_rect2, 2)
    
    # Dibujar los puntos para ambos dados
    for i, dice_value in enumerate(dice_values):
        dice_center_x = display_size//2 - 40 + i*80
        dice_center_y = display_size - 70
        
        if dice_value == 1:
            pygame.draw.circle(screen, BLACK, (dice_center_x, dice_center_y), 5)
        elif dice_value == 2:
            pygame.draw.circle(screen, BLACK, (dice_center_x - 15, dice_center_y - 15), 5)
            pygame.draw.circle(screen, BLACK, (dice_center_x + 15, dice_center_y + 15), 5)
        elif dice_value == 3:
            pygame.draw.circle(screen, BLACK, (dice_center_x - 15, dice_center_y - 15), 5)
            pygame.draw.circle(screen, BLACK, (dice_center_x, dice_center_y), 5)
            pygame.draw.circle(screen, BLACK, (dice_center_x + 15, dice_center_y + 15), 5)
        elif dice_value == 4:
            pygame.draw.circle(screen, BLACK, (dice_center_x - 15, dice_center_y - 15), 5)
            pygame.draw.circle(screen, BLACK, (dice_center_x + 15, dice_center_y - 15), 5)
            pygame.draw.circle(screen, BLACK, (dice_center_x - 15, dice_center_y + 15), 5)
            pygame.draw.circle(screen, BLACK, (dice_center_x + 15, dice_center_y + 15), 5)
        elif dice_value == 5:
            pygame.draw.circle(screen, BLACK, (dice_center_x - 15, dice_center_y - 15), 5)
            pygame.draw.circle(screen, BLACK, (dice_center_x + 15, dice_center_y - 15), 5)
            pygame.draw.circle(screen, BLACK, (dice_center_x, dice_center_y), 5)
            pygame.draw.circle(screen, BLACK, (dice_center_x - 15, dice_center_y + 15), 5)
            pygame.draw.circle(screen, BLACK, (dice_center_x + 15, dice_center_y + 15), 5)
        elif dice_value == 6:
            pygame.draw.circle(screen, BLACK, (dice_center_x - 15, dice_center_y - 15), 5)
            pygame.draw.circle(screen, BLACK, (dice_center_x + 15, dice_center_y - 15), 5)
            pygame.draw.circle(screen, BLACK, (dice_center_x - 15, dice_center_y), 5)
            pygame.draw.circle(screen, BLACK, (dice_center_x + 15, dice_center_y), 5)
            pygame.draw.circle(screen, BLACK, (dice_center_x - 15, dice_center_y + 15), 5)
            pygame.draw.circle(screen, BLACK, (dice_center_x + 15, dice_center_y + 15), 5)
    
    # Mostrar suma total
    total_text = small_font.render(f"Total: {dice_values[0] + dice_values[1]}", True, BLACK)
    screen.blit(total_text, (display_size//2 - 30, display_size - 30))

def roll_dice():
    global dice_values, dice_rolled
    if not dice_rolled:
        dice_values = [random.randint(1, 6), random.randint(1, 6)]
        dice_rolled = True

def can_leave_jail(dice_values):
    """
    Verifica si los valores de los dados permiten que una ficha salga de la cárcel
    Retorna True si un dado muestra 5 o la suma es 5
    """
    return (dice_values[0] == 5 or 
            dice_values[1] == 5 or 
            dice_values[0] + dice_values[1] == 5)

def get_next_position(player, piece_idx, steps):
    """
    Calcula la nueva posición de una ficha después de mover 'steps' pasos
    También actualiza el contador de vueltas si es necesario
    """
    global piece_laps
    
    current_pos = player_positions[player][piece_idx]
    
    # Si la ficha está en la meta, se queda ahí
    if current_pos == central_cell:
        return central_cell
    
    # Si la ficha está en el camino final
    if current_pos in home_paths[player]:
        home_index = home_paths[player].index(current_pos)
        new_home_index = home_index + steps
        
        if new_home_index < len(home_paths[player]):
            return home_paths[player][new_home_index]
        elif new_home_index == len(home_paths[player]):
            # Llega exactamente a la meta
            return central_cell
        else:
            # Si se pasa de la meta, se queda donde está
            return current_pos
    
    # Si la ficha está en el camino común o en la casilla de salida
    if current_pos in main_path or current_pos == starting_positions[player]:
        # Si está en la casilla de salida, tomarla como parte del camino principal
        if current_pos == starting_positions[player]:
            current_index = main_path.index(starting_positions[player])
        else:
            current_index = main_path.index(current_pos)
        
        # Índices de las casillas de salida en el camino principal para cada jugador
        starting_indices = {
            0: main_path.index(starting_positions[0]),
            1: main_path.index(starting_positions[1]),
            2: main_path.index(starting_positions[2]),
            3: main_path.index(starting_positions[3])
        }
        
        # Índice de la entrada al camino final para el jugador actual
        # En Parqués, la entrada al camino final está en la misma casilla que la salida
        entry_index = starting_indices[player]
        
        # Calcular el nuevo índice después de moverse
        new_index_raw = current_index + steps
        
        # Comprobar si la ficha completa una vuelta durante este movimiento
        if current_index < entry_index:
            # Si la ficha está antes de su entrada/salida y la va a pasar
            if new_index_raw >= entry_index and new_index_raw < len(main_path) + entry_index:
                piece_laps[player][piece_idx] += 1
        else:
            # Si la ficha está después de su entrada/salida y va a dar una vuelta completa
            if new_index_raw >= len(main_path) + entry_index:
                piece_laps[player][piece_idx] += 1
        
        # Normalizar el índice para que esté dentro del rango del camino principal
        new_index = new_index_raw % len(main_path)
        
        # Comprobar si debe entrar al camino final
        if piece_laps[player][piece_idx] > 0:  # Si ha dado al menos una vuelta completa
            # Comprobar si pasa exactamente por su punto de entrada
            goes_through_entry = False
            steps_after_entry = 0
            
            if current_index < entry_index and new_index_raw >= entry_index:
                # Pasa por la entrada en este movimiento
                steps_after_entry = new_index_raw - entry_index
                goes_through_entry = True
            elif current_index > entry_index and new_index < current_index:
                # Ha dado una vuelta y ha pasado por la entrada
                lap_completion_index = len(main_path) + entry_index
                if new_index_raw >= lap_completion_index:
                    steps_after_entry = new_index_raw - lap_completion_index
                    goes_through_entry = True
            
            # Si pasa por la entrada y tiene pasos restantes, entra al camino final
            if goes_through_entry:
                if steps_after_entry < len(home_paths[player]):
                    return home_paths[player][steps_after_entry]
                elif steps_after_entry == len(home_paths[player]):
                    return central_cell
        
        # Si no entra al camino final, se mueve por el camino común
        return main_path[new_index]
    
    # Si no está en ningún camino conocido, no se mueve
    return current_pos

def move_piece():
    global turn, dice_rolled, selected_piece, game_over, winner
    
    # Si el juego ha terminado, no hacer nada
    if game_over:
        return
    
    current_pos = player_positions[turn][selected_piece]
    dice_sum = dice_values[0] + dice_values[1]
    
    # Si está en la cárcel y no puede salir, pasar turno
    if current_pos in initial_positions[turn] and not can_leave_jail(dice_values):
        dice_rolled = False
        turn = (turn + 1) % 4
        return
    
    # Si está en la cárcel y puede salir, va a la casilla de salida
    if current_pos in initial_positions[turn] and can_leave_jail(dice_values):
        player_positions[turn][selected_piece] = starting_positions[turn]
        
        # Verificar captura en la casilla de salida
        if starting_positions[turn] not in safe_spots:
            check_capture(starting_positions[turn])
            
        # Verificar si todas las fichas han llegado a la meta
        if all(pos == central_cell for pos in player_positions[turn]):
            winner = turn
            game_over = True
        
        # Si sacó dobles, tiene otro turno
        if dice_values[0] == dice_values[1]:
            dice_rolled = False
        else:
            dice_rolled = False
            turn = (turn + 1) % 4
        return
    
    # Para fichas que ya están fuera de la cárcel, calcular la nueva posición usando la suma de los dados
    new_pos = get_next_position(turn, selected_piece, dice_sum)
    
    # Si la posición no cambió, pasar el turno
    if new_pos == current_pos:
        dice_rolled = False
        turn = (turn + 1) % 4
        return
    
    # Actualizar la posición de la ficha
    player_positions[turn][selected_piece] = new_pos
    
    # Verificar captura si no está en una casilla segura, camino final o meta
    if new_pos not in safe_spots and new_pos not in home_paths[turn] and new_pos != central_cell:
        check_capture(new_pos)
    
    # Verificar si todas las fichas han llegado a la meta
    if all(pos == central_cell for pos in player_positions[turn]):
        winner = turn
        game_over = True
    
    # Si sacó dobles, tiene otro turno; si no, pasa al siguiente jugador
    if dice_values[0] == dice_values[1]:
        dice_rolled = False
    else:
        dice_rolled = False
        turn = (turn + 1) % 4

def check_capture(new_pos):
    global turn
    
    # Verificar si hay fichas de otros jugadores en la misma casilla
    for player in range(4):
        if player != turn:  # No capturar fichas propias
            for i, pos in enumerate(player_positions[player]):
                if pos == new_pos:
                    # Enviar la ficha capturada a la cárcel
                    player_positions[player][i] = initial_positions[player][i]
                    # Reiniciar contador de vueltas para la ficha capturada
                    piece_laps[player][i] = 0

def draw_game_info():
    # Mostrar turno actual
    player_names = ["Rojo", "Verde", "Azul", "Amarillo"]
    turn_text = font.render(f"Turno: {player_names[turn]}", True, COLORS[turn])
    screen.blit(turn_text, (10, display_size - 50))
    
    # Mostrar ficha seleccionada
    piece_text = font.render(f"Ficha: {selected_piece + 1}", True, BLACK)
    screen.blit(piece_text, (10, display_size - 90))
    
    # Mostrar instrucciones para lanzar dado
    if not dice_rolled:
        roll_text = font.render("Presiona ESPACIO para lanzar los dados", True, BLACK)
        screen.blit(roll_text, (display_size//2 - 200, display_size - 140))
    
    # Mostrar ganador si el juego ha terminado
    if game_over:
        player_names = ["Rojo", "Verde", "Azul", "Amarillo"]
        winner_text = font.render(f"¡{player_names[winner]} ha ganado!", True, COLORS[winner])
        text_rect = winner_text.get_rect(center=(display_size//2, display_size//2))
        pygame.draw.rect(screen, WHITE, (text_rect.x - 10, text_rect.y - 10, text_rect.width + 20, text_rect.height + 20))
        pygame.draw.rect(screen, COLORS[winner], (text_rect.x - 10, text_rect.y - 10, text_rect.width + 20, text_rect.height + 20), 3)
        screen.blit(winner_text, text_rect)

def draw_instructions():
    instructions = [
        "Espacio: Lanzar dados",
        "Enter: Mover ficha",
        "1-4: Seleccionar ficha",
        "Para salir: 5 en un dado o suma 5",
        "Dobles dan turno extra",
        "R: Reiniciar juego",
        "T: Ver recorrido (turno amarillo)"
    ]
    
    for i, text in enumerate(instructions):
        instr_text = small_font.render(text, True, BLACK)
        screen.blit(instr_text, (display_size - 200, 10 + i * 25))

running = True
show_path = False
while running:
    screen.fill(WHITE)
    draw_board()
    draw_pieces()
    draw_dice()
    draw_game_info()
    draw_instructions()
    pygame.display.flip()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                roll_dice()
            elif event.key == pygame.K_RETURN and dice_rolled:
                move_piece()
            elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]:
                piece_index = int(event.unicode) - 1
                if 0 <= piece_index < len(player_positions[turn]):
                    selected_piece = piece_index
            # Tecla para mostrar recorrido
            elif event.key == pygame.K_t:
                turn = 3  # Cambiar al turno amarillo
                show_path = True
            # Reiniciar juego
            elif event.key == pygame.K_r:
                game_over = False
                winner = -1
                dice_values = [1, 1]
                dice_rolled = False
                turn = 0
                selected_piece = 0
                player_positions = {p: list(initial_positions[p]) for p in range(4)}
                piece_laps = {0: [0, 0, 0, 0], 1: [0, 0, 0, 0], 2: [0, 0, 0, 0], 3: [0, 0, 0, 0]}

pygame.quit()