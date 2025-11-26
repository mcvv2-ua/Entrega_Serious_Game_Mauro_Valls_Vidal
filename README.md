# Serious Game: Ski Rehab - Estimación de Fragilidad Física

Este proyecto consiste en el desarrollo de un **Juego Serio (Serious Game)** para la asignatura de Interacción Persona-Máquina (IPM). Utiliza visión por computador mediante la librería **MediaPipe**  para crear una interfaz natural que permite la rehabilitación física y la evaluación de la fragilidad en usuarios.

## 🏥 Justificación Terapéutica y Objetivo

El videojuego ha sido diseñado con un propósito que va más allá del entretenimiento, centrándose específicamente en el ámbito de la salud y la estimación de la fragilidad:

1. **Evaluación de Fragilidad (Tren Inferior):** Una de las mecánicas requiere que el usuario realice sentadillas para esquivar obstáculos (túneles). Este movimiento simula el test clínico *Sit-to-Stand*, un indicador biomecánico fundamental para evaluar la fuerza muscular y la fragilidad en personas mayores.
2. Rehabilitación de Equilibrio (Control Postural): El control lateral del personaje mediante la inclinación y desplazamiento del cuerpo fomenta el control postural dinámico y la transferencia de peso, ayudando a la prevención de caídas.
3. **Estimulación Cognitiva:** El juego incluye dificultad progresiva y patrones de obstáculos aleatorios, trabajando la velocidad de reacción y la toma de decisiones bajo presión.

## 🛠️ Requisitos del Sistema

Para desplegar este proyecto en un equipo nuevo ("limpio"), se requiere:

* **Python 3.8** o superior.
* Una **webcam** funcional (para la detección del cuerpo).
* Sistema de audio (altavoces/auriculares) para el feedback sonoro del juego.

## 🚀 Instalación y Despliegue

Sigue estos pasos para ejecutar el juego en un entorno nuevo libre de configuraciones previas[cite: 70, 71]:

### 1. Configuración del Entorno (Opcional pero recomendado)

Es aconsejable aislar las dependencias del proyecto creando un entorno virtual:

```bash
conda create -n ipm_game python=3.9 -y
conda activate ipm_game
```

### 2. Instalación de Dependencias

Instala las librerías necesarias (`mediapipe`, `opencv-python`, `numpy`, `pygame`) listadas en el archivo de requisitos:

```bash
pip install -r requirements.txt
```

### 3. Descarga del Modelo de IA

El proyecto utiliza el modelo `pose_landmarker_full.task` de MediaPipe.

* El sistema intentará descargarlo automáticamente al iniciar.
* Si hubiera problemas de conexión, ejecuta manualmente el script de descarga:

```bash
python download_models.py
```

## ▶️ Ejecución

Para iniciar el videojuego, ejecuta el archivo principal desde la raíz del proyecto:

```bash
python app.py
```

## 🎮 Manual de Instrucciones

### Calibración Inicial

Al arrancar, el juego entrará en modo **CALIBRATING**.

1. Sitúate frente a la cámara (se recomienda estar de pie y visible de cintura para arriba, a unos 2 metros).
2. Permanece **RECTO y QUIETO** durante unos segundos hasta que la barra de progreso verde se llene.
3. El sistema medirá tu altura de reposo para establecer el umbral de la sentadilla.

### Mecánicas de Juego

Eres un esquiador bajando por una pista infinita. Tu cuerpo actúa como el controlador (interacción natural):

* **Movimiento Lateral:** Desplaza tu cuerpo a izquierda o derecha para mover al esquiador y esquivar los **Árboles**.
* **Agacharse (Sentadilla):** Cuando veas un **Túnel Azul** o el aviso "!!! TUNEL !!! ABAJO", realiza una sentadilla (baja la cadera/cabeza) para pasar por debajo. Aparecerá el mensaje "DOWN!".
* **Objetivo:** Sobrevivir el máximo tiempo posible acumulando puntos.

### Niveles de Dificultad (Progresivos)

El juego aumenta la dificultad automáticamente según la puntuación del paciente:

* **EASY (0-10 pts):** Velocidad moderada, obstáculos simples.
* **MEDIUM (10-25 pts):** Mayor frecuencia de obstáculos y velocidad aumentada.
* **HARD (25+ pts):** Velocidad extrema y formaciones complejas (muros de 3 árboles, trampas y aparición simultánea).

### Controles de Teclado

* **ESC:** Salir del juego (funciona tanto durante la partida como en la pantalla de Game Over).
* **ENTER:** Reiniciar la partida tras perder.

---

**Asignatura:** Interacción Persona-Máquina (IPM) **Fecha:** Noviembre 2025 **Autor:** Mauro Valls Vidal
