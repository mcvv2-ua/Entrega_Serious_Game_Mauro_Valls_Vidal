import sys
import cv2
import mediapipe as mp
import numpy as np
import time
import os
import random
import pygame
from config import config

# --- 1. CARGA DE RECURSOS ---
# Inicialización y carga de recursos del sistema
current_dir = os.path.dirname(os.path.abspath(__file__))
model_path_abs = os.path.join(current_dir, 'models', 'pose_landmarker_full.task')

# Inicializar Pygame Mixer (Audio)
try:
    pygame.mixer.pre_init(44100, -16, 2, 2048)
    pygame.mixer.init()
    print("🔊 Sistema de audio iniciado.")
except Exception as e:
    print(f"⚠️ Error iniciando audio: {e}")

try:
    with open(model_path_abs, 'rb') as f:
        model_data = f.read()
except FileNotFoundError:
    print("❌ Error: No se encuentra el modelo. Ejecuta download_models.py")
    sys.exit(1)

# --- GESTOR DE IMÁGENES ---
# Gestión y procesamiento de imágenes
def load_sprite(filename):
    path = os.path.join(current_dir, 'images', filename)
    stream = open(path, "rb")
    bytes = bytearray(stream.read())
    numpyarray = np.asarray(bytes, dtype=np.uint8)
    img = cv2.imdecode(numpyarray, cv2.IMREAD_UNCHANGED)
    
    if len(img.shape) == 3: img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
    return img

def create_dummy(color, w=60, h=60):
    dummy = np.zeros((h, w, 4), dtype=np.uint8)
    dummy[:] = color
    return dummy

# --- GESTOR DE SONIDOS ---
# Sistema de audio y efectos de sonido
def load_sound(filename):
    path = os.path.join(current_dir, 'sounds', filename)
    return pygame.mixer.Sound(path)

# --- CARGA DE ASSETS INTELIGENTE ---
# Carga dinámica de activos gráficos

# 1. Jugador y Tunel
img_player = load_sprite('player.png')
img_tunnel = load_sprite('tunnel.png')

# Carga de sprites para obstáculos
tree_sprites = [
    load_sprite('tree1.png'),
    load_sprite('tree2.png'),
    load_sprite('tree3.png')
]

# Cargar Efectos de Sonido (SFX)
sfx_die = load_sound('die.wav')
sfx_start = load_sound('start.wav')
sfx_start.set_volume(1.0) 

# Rutas de música
path_music_game = os.path.join(current_dir, 'sounds', 'music.mp3')
path_music_gameover = os.path.join(current_dir, 'sounds', 'gameover.mp3')

def play_music(path, loops=-1):
    pygame.mixer.music.load(path)
    pygame.mixer.music.play(loops)
    pygame.mixer.music.set_volume(0.4)

def draw_sprite(frame, sprite, x_center, y_center, width=None, height=None):
    h_bg, w_bg = frame.shape[:2]
    if width is not None and height is not None:
        sprite_resized = cv2.resize(sprite, (int(width), int(height)))
    else:
        sprite_resized = sprite
    h_sp, w_sp = sprite_resized.shape[:2]
    x = int(x_center - w_sp / 2)
    y = int(y_center - h_sp / 2)
    y1, y2 = max(0, y), min(h_bg, y + h_sp)
    x1, x2 = max(0, x), min(w_bg, x + w_sp)
    y1o, y2o = max(0, -y), min(h_sp, h_bg - y)
    x1o, x2o = max(0, -x), min(w_sp, w_bg - x)
    if y1 >= y2 or x1 >= x2 or y1o >= y2o or x1o >= x2o: return frame
    sprite_crop = sprite_resized[y1o:y2o, x1o:x2o]
    frame_crop = frame[y1:y2, x1:x2]
    if sprite_crop.shape[2] < 4: return frame 
    alpha = sprite_crop[:, :, 3] / 255.0
    alpha_inv = 1.0 - alpha
    for c in range(3):
        frame_crop[:, :, c] = (alpha * sprite_crop[:, :, c] + alpha_inv * frame_crop[:, :, c])
    frame[y1:y2, x1:x2] = frame_crop
    return frame

# --- MEDIAPIPE SETUP ---
# Configuración del modelo de visión artificial (MediaPipe)
BaseOptions = mp.tasks.BaseOptions
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

options = PoseLandmarkerOptions(
    base_options=BaseOptions(model_asset_buffer=model_data), 
    running_mode=VisionRunningMode.VIDEO,
    num_poses=1
)

# --- CLASES DEL JUEGO ---
# Definición de entidades del juego
class Player:
    def __init__(self, w, h):
        self.x = w // 2
        self.y = h - 150 
        self.base_size = 90 
        self.is_squatting = False
    
    def draw(self, frame):
        h_draw = self.base_size * 0.6 if self.is_squatting else self.base_size
        w_draw = self.base_size
        draw_sprite(frame, img_player, self.x, self.y, w_draw, h_draw)
        if self.is_squatting:
            cv2.putText(frame, "DOWN!", (int(self.x)-30, int(self.y)-60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

class Obstacle:
    def __init__(self, w, type_obs, speed, fixed_x=None):
        self.y = -150 
        self.type = type_obs 
        self.speed = speed 
        self.passed = False
        
        if self.type == 'TREE':
            # Textura Aleatoria
            self.image = random.choice(tree_sprites)
            # Variación de tamaño
            scale_var = random.uniform(0.9, 1.1) 
            self.width = int(100 * scale_var)
            self.height = int(120 * scale_var)
            
            if fixed_x is not None:
                self.x = fixed_x
            else:
                self.x = random.randint(60, w - 60)
        else: 
            self.image = img_tunnel
            self.width = w * 0.95 
            self.height = 100
            self.x = w // 2 

    def move(self):
        self.y += self.speed

    def draw(self, frame):
        draw_sprite(frame, self.image, self.x, self.y, self.width, self.height)

    def check_collision(self, player):
        p_h = 40 if player.is_squatting else 70
        p_w = 30 
        o_h = self.height * 0.6 
        o_w = self.width * 0.6

        if (self.y + o_h/2 > player.y - p_h/2) and (self.y - o_h/2 < player.y + p_h/2):
            if self.type == 'TREE':
                if (player.x + p_w/2 > self.x - o_w/2) and (player.x - p_w/2 < self.x + o_w/2):
                    return True
            elif self.type == 'TUNNEL':
                if not player.is_squatting:
                     return True
        return False

# --- BUCLE PRINCIPAL ---
# Función principal y bucle de ejecución
def main():
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    
    game_state = "CALIBRATING" 
    score = 0
    obstacles = []
    spawn_timer = 0
    
    base_nose_y = 0
    calibration_frames = 0
    player = None 
    
    current_mode = "EASY" 
    current_speed = 15    
    spawn_rate = 40 

    music_playing_state = None      

    with PoseLandmarker.create_from_options(options) as landmarker:
        print("✅ Sistema de juego inicializado correctamente.")
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break
            
            frame = cv2.flip(frame, 1)
            h, w = frame.shape[:2]
            
            if player is None: player = Player(w, h)

            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
            result = landmarker.detect_for_video(mp_image, int(time.time() * 1000))

            detected = False
            if result.pose_landmarks:
                detected = True
                landmarks = result.pose_landmarks[0]
                nose = landmarks[0] 
                nx, ny = int(nose.x * w), int(nose.y * h)
                
                if game_state == "CALIBRATING":
                    if music_playing_state != "CALIBRATING":
                        pygame.mixer.music.stop()
                        music_playing_state = "CALIBRATING"

                    cv2.rectangle(frame, (w//2 - 220, h//2 - 100), (w//2 + 220, h//2 + 100), (0,0,0), -1)
                    cv2.putText(frame, "CALIBRANDO...", (w//2 - 120, h//2 - 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
                    cv2.putText(frame, "Ponte RECTO y QUIETO", (w//2 - 150, h//2 + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255), 2)
                    
                    bar_width = 300
                    fill = int((calibration_frames/60) * bar_width)
                    cv2.rectangle(frame, (w//2 - bar_width//2, h//2 + 50), (w//2 - bar_width//2 + fill, h//2 + 70), (0,255,0), -1)
                    
                    base_nose_y += ny
                    calibration_frames += 1
                    if calibration_frames > 60: 
                        base_nose_y /= 60 
                        game_state = "PLAYING"
                        play_music(path_music_game) 
                        music_playing_state = "GAME"
                
                elif game_state == "PLAYING":
                    player.x = int(player.x * 0.3 + nx * 0.7)
                    squat_limit = base_nose_y + (h * 0.10) 
                    player.is_squatting = (ny > squat_limit)

            # --- LÓGICA DE JUEGO ---
            if game_state == "PLAYING":
                spawn_timer += 1
                
                # NIVELES
                if score < 10:
                    current_mode = "EASY"
                    current_speed = 12
                    spawn_rate = 45 
                    color_mode = (0, 255, 0)
                elif score < 25:
                    current_mode = "MEDIUM"
                    current_speed = 16
                    spawn_rate = 25    
                    color_mode = (0, 165, 255)
                else:
                    current_mode = "HARD"
                    current_speed = 22
                    spawn_rate = 15    
                    color_mode = (0, 0, 255)

                if spawn_timer > spawn_rate:
                    
                    # === IA DEL DIRECTOR DE JUEGO (SPAWNER) ===
                    # Lógica de generación procedural de obstáculos
                    
                    if current_mode == "EASY":
                        type_obs = 'TUNNEL' if random.random() < 0.3 else 'TREE'
                        
                        # Probabilidad aumentada de generar obstáculo en la trayectoria del jugador
                        if type_obs == 'TREE' and random.random() < 0.7:
                            obstacles.append(Obstacle(w, 'TREE', current_speed, fixed_x=player.x))
                        else:
                            obstacles.append(Obstacle(w, type_obs, current_speed))

                    elif "MEDIUM" in current_mode:
                        # 30% Dobles
                        if random.random() < 0.3: 
                            obstacles.append(Obstacle(w, 'TREE', current_speed, fixed_x=w//3))
                            obstacles.append(Obstacle(w, 'TREE', current_speed, fixed_x=w - w//3))
                        else:
                            type_obs = 'TUNNEL' if random.random() < 0.2 else 'TREE'
                            # Alta probabilidad de interceptación en modo medio
                            target_x = player.x if random.random() < 0.9 else None
                            obstacles.append(Obstacle(w, type_obs, current_speed, fixed_x=target_x))

                    else: # HARD
                        roll = random.random()
                        if roll < 0.3: # Muro de 3
                             obstacles.append(Obstacle(w, 'TREE', current_speed, fixed_x=w//2))
                             obstacles.append(Obstacle(w, 'TREE', current_speed, fixed_x=80))   
                             obstacles.append(Obstacle(w, 'TREE', current_speed, fixed_x=w-80)) 
                        elif roll < 0.6: # Tunel
                             obstacles.append(Obstacle(w, 'TUNNEL', current_speed))
                        else:
                             # Generación determinista de obstáculo en la posición actual
                             obstacles.append(Obstacle(w, 'TREE', current_speed, fixed_x=player.x))

                    spawn_timer = 0
                
                # --- ALERTA DE TÚNEL ---
                tunnel_alert = False
                for obs in obstacles:
                    obs.move()
                    obs.draw(frame)
                    
                    # Detectar túneles activos
                    if obs.type == 'TUNNEL' and obs.y > -50 and obs.y < h:
                        tunnel_alert = True
                    
                    if obs.check_collision(player):
                        game_state = "GAME_OVER"
                        pygame.mixer.music.stop()
                        if sfx_die: sfx_die.play()
                        play_music(path_music_gameover)
                        music_playing_state = "GAMEOVER"
                    
                    if obs.y > h and not obs.passed:
                        row_cleared = True
                        for other in obstacles:
                             if abs(other.y - obs.y) < 20 and other.passed:
                                 row_cleared = False
                        if row_cleared: score += 1
                        obs.passed = True

                obstacles = [o for o in obstacles if o.y < h + 100]
                
                if detected: player.draw(frame)
                
                # UI
                cv2.rectangle(frame, (0,0), (w, 60), (0,0,0), -1)
                cv2.putText(frame, f"SCORE: {score}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                cv2.putText(frame, f"{current_mode}", (w - 350, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color_mode, 2)
                
                # Dibujar Alerta
                if tunnel_alert:
                    if score % 2 == 0 or int(time.time()*10)%2 == 0:
                        cv2.rectangle(frame, (w//2 - 250, 80), (w//2 + 250, 140), (0,0,255), -1)
                        cv2.putText(frame, "!!! TUNEL !!! ABAJO", (w//2 - 200, 125), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 3)

            elif game_state == "GAME_OVER":
                overlay = frame.copy()
                cv2.rectangle(overlay, (0, 0), (w, h), (0,0,0), -1)
                cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
                
                cv2.putText(frame, "GAME OVER", (w//2 - 180, h//2 - 20), cv2.FONT_HERSHEY_SIMPLEX, 2, (0,0,255), 4)
                cv2.putText(frame, f"Score: {score}", (w//2 - 80, h//2 + 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255,255,255), 2)
                
                cv2.putText(frame, "ENTER para reiniciar", (w//2 - 160, h//2 + 120), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200,200,200), 1)
                cv2.putText(frame, "ESC para salir", (w//2 - 110, h//2 + 160), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (100,100,100), 1)
                
                key = cv2.waitKey(1) & 0xFF
                
                if key == 13: 
                    if sfx_start: sfx_start.play()
                    pygame.mixer.music.stop()
                    game_state = "CALIBRATING"
                    obstacles = []
                    score = 0
                    calibration_frames = 0
                    base_nose_y = 0
                    music_playing_state = None 
                
                elif key == 27:
                    break

            cv2.imshow("Serious Game - FINAL VERSION", frame)
            if cv2.waitKey(1) & 0xFF == 27 and game_state != "GAME_OVER": 
                break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()