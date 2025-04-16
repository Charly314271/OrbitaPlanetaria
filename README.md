# Simulación de Gravitación N-Cuerpos con Tabla de Datos Físicos

## Descripción General
Esta simulación ilustra la dinámica de un sistema de cuerpos celestes interactuando bajo la influencia gravitatoria mutua. Se emplea el algoritmo de integración de Verlet para la evolución temporal del sistema, garantizando una mayor precisión en la conservación de la energía en comparación con métodos de primer orden como el de Euler. La interfaz incluye una tabla de datos físicos que presenta información detallada en tiempo real sobre cada cuerpo simulado y ofrece la visualización opcional de las trayectorias futuras predichas.

## Requisitos del Sistema
- Biblioteca Pygame (`pip install pygame`)

## Instrucciones de Ejecución
1. Asegúrese de tener instalada la biblioteca Pygame:
   ```bash
   pip install pygame

# Fundamentos Algorítmicos
-El núcleo de la simulación se basa en el método de integración de Verlet, un algoritmo numérico ampliamente utilizado en la simulación de sistemas dinámicos debido a su estabilidad y precisión en la conservación de la energía para sistemas conservativos como la gravedad. El algoritmo se desarrolla en los siguientes pasos iterativos:

-Cálculo de la Fuerza Gravitacional Neta: Para cada cuerpo en el sistema, se determina la fuerza gravitacional resultante ejercida por todos los demás cuerpos presentes. Este cálculo se fundamenta en la Ley de Gravitación Universal, modificada con un término de suavizado (ϵ) para prevenir singularidades cuando la distancia entre dos cuerpos tiende a cero. 

-Actualización de la Posición (Integración de Verlet): La nueva posición de cada cuerpo se calcula utilizando la posición actual, la velocidad actual y la aceleración en el instante actual

-Recálculo de las Fuerzas: Una vez que se han actualizado las posiciones de todos los cuerpos, se recalculan las fuerzas gravitacionales netas actuando sobre cada uno de ellos, utilizando las nuevas posiciones obtenidas en el paso anterior. Esto proporciona las aceleraciones en el instante 

Actualización de la Velocidad (Integración de Verlet): Finalmente, se actualiza la velocidad de cada cuerpo utilizando las aceleraciones en el instante actual 


# Arquitectura de la Implementación
Clase Body: Esta clase representa un cuerpo celeste individual y encapsula sus atributos físicos esenciales: masa (m), vector de posición (r), vector de velocidad (v), vector de fuerza resultante (F), color de representación visual y un nombre identificativo. La clase también implementa métodos para calcular la fuerza gravitacional ejercida sobre el cuerpo por otros cuerpos y para actualizar su posición y velocidad según el algoritmo de Verlet. Adicionalmente, gestiona el almacenamiento de la trayectoria histórica del cuerpo y la predicción de su trayectoria futura.

Predicción de Trayectorias: Para predecir la trayectoria futura de un cuerpo seleccionado, se realiza una simulación temporal limitada utilizando el mismo algoritmo de Verlet. Se toman las condiciones actuales del cuerpo (posición y velocidad) y se simulan varios pasos en el futuro, considerando la influencia gravitacional de todos los demás cuerpos en sus posiciones actuales. Las posiciones predichas se almacenan y se visualizan opcionalmente.

Visualización: La representación visual de la simulación se realiza utilizando la biblioteca Pygame. Los cuerpos se dibujan como círculos cuyo tamaño está escalado logarítmicamente con su masa. Se visualizan las trayectorias pasadas de los cuerpos mediante una serie de puntos conectados, y las trayectorias predichas se muestran con un color más tenue. Opcionalmente, se pueden dibujar vectores que representan la velocidad (en verde) y la fuerza neta (en rojo) actuando sobre cada cuerpo. El color de los cuerpos puede variar dinámicamente en función de su velocidad.

Tabla de Datos Físicos: Se implementa una tabla interactiva que se muestra en la parte inferior de la pantalla. Esta tabla presenta información en tiempo real sobre cada cuerpo simulado, incluyendo su nombre, masa (normalizada a una masa base), posición (coordenadas x e y), magnitud de la velocidad, magnitud de la fuerza neta y energía cinética. La fila correspondiente al cuerpo seleccionado (mediante las teclas numéricas) se resalta para facilitar su identificación.


# Análisis de la Eficiencia Computacional
Complejidad Temporal: El cálculo de las fuerzas gravitacionales entre todos los pares de cuerpos es la operación más costosa en cada paso de la simulación. Para un sistema de N cuerpos, cada cuerpo interactúa gravitacionalmente con los N−1 cuerpos restantes. Por lo tanto, la complejidad computacional de esta etapa es de orden O(N2) por cada paso de tiempo. La actualización de las posiciones y velocidades tiene una complejidad de O(N). En consecuencia, la complejidad total por paso de tiempo está dominada por el cálculo de las fuerzas, resultando en una complejidad de O(N2).

# Estrategias de Optimización:

Se utiliza la clase Vector2 de Pygame para realizar operaciones vectoriales de manera eficiente.
La longitud de las trayectorias históricas almacenadas para la visualización se limita a un valor constante (TRAIL_LENGTH) para evitar un consumo excesivo de memoria.
El cálculo y la visualización de las trayectorias predichas se realizan solo cuando el usuario lo solicita, lo que reduce la carga computacional cuando esta característica no está activa.


# Parametros que se pueden ajustar 
G = 6.674e-2           #Constante de gravitación universal (ajustada para la escala de la simulación)
BASE_MASS = 1e6        #Unidad de masa base para la normalización en la tabla
NUM_BODIES = 3         #Número inicial de cuerpos en la simulación
DT = 0.005             #Intervalo de tiempo (paso) de la simulación en segundos
TRAIL_LENGTH = 100     #Número máximo de puntos guardados para la visualización de la trayectoria
SOFTENING = 50         #Parámetro de suavizado para evitar singularidades gravitacionales
PREDICTION_STEPS = 50  #Número de pasos futuros a simular para la predicción de la trayectoria


# Bibliografia

Binney, J., & Tremaine, S. (2008). Galactic Dynamics (2nd ed.). Princeton University Press.

Frenkel, D., & Smit, B. (2002). Understanding Molecular Simulation (2nd ed.). Academic Press.

Pygame Contributors. (2023). Pygame Documentation [Software]. https://www.pygame.org/docs/