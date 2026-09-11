# AeroCargo-Matrix

Universidad Don Bosco — Facultad de Aeronáutica

Asignatura:DAS172 — Desarrollo de Algoritmos para la Simulación de Sistemas

Evaluación: EVA106 — Examen Teórico Unidad II: Funciones y Arreglos

Reto: Auditoría y Balance Matricial de Distribución de Carga en Bahía de Aeronave

Nombre: Andrea Alejandra Mejia Martinez-MM210136
---

## 1. Explicación del Problema

En la aviación de carga, la forma en que se distribuye el peso dentro de la bodega de una aeronave no es un detalle secundario: incide directamente en la seguridad del vuelo. El piso de la bahía de carga se representa como una cuadrícula de N filas por M columnas, donde cada celda equivale a un compartimiento con un peso real depositado y un límite estructural que no debe sobrepasarse.

Existen dos riesgos principales que este proyecto busca controlar mediante análisis matricial:

Por un lado, la resistencia estructural: cada sección del piso soporta un peso máximo definido por el fabricante, y sobrepasarlo en cualquier celda puede debilitar el fuselaje en esa zona, incluso si el peso total de la aeronave está dentro de lo permitido.

Por otro lado, el equilibrio de la aeronave: el peso debe repartirse de manera simétrica entre el lado izquierdo y el derecho. Un desbalance lateral significativo desplaza el centro de gravedad transversal, afectando la estabilidad y la capacidad de maniobra durante el vuelo.

AeroCargo-Matrix automatiza esta verificación: valida que los datos de entrada sean consistentes, calcula el porcentaje de ocupación de cada compartimiento para detectar sobrecargas puntuales, evalúa el balance lateral considerando si el número de columnas es par o impar, y localiza la subzona de la bodega con mayor concentración de riesgo mediante una ventana de búsqueda deslizante.

---

## 2. Diagrama de Arquitectura Modular

El diseño sigue un flujo lineal de transformación de datos: cada función es
**pura** (no usa variables globales, no muta sus argumentos) y recibe como
entrada la salida de la etapa anterior.

```
                    ┌───────────────────────────┐
                    │   main.py (orquestador)   │
                    └─────────────┬─────────────┘
                                  │
        matriz_cargas, matriz_capacidades (datos de prueba)
                                  │
                                  ▼
              ┌───────────────────────────────────┐
              │ 1. validar_matrices(cargas, caps)  │
              │    -> bool                         │
              └─────────────────┬───────────────────┘
                                  │ (si True, continúa)
                                  ▼
              ┌───────────────────────────────────┐
              │ 2. calcular_ocupacion(cargas, caps)│
              │    -> {porcentajes, sobrecargas}   │
              └─────────────────┬───────────────────┘
                     │                        │
                     │ cargas                 │ porcentajes
                     ▼                        ▼
     ┌─────────────────────────┐   ┌───────────────────────────────┐
     │ 3. evaluar_balance(      │   │ 4. extraer_submatriz_critica( │
     │    cargas, tolerancia)   │   │    porcentajes, k, p)         │
     │    -> {pesos_por_fila,   │   │    -> submatriz k x p         │
     │        desbalance,       │   │                                │
     │        balanceado}       │   │                                │
     └─────────────────────────┘   └───────────────────────────────┘
                     │                        │
                     └───────────┬────────────┘
                                  ▼
                    ┌───────────────────────────┐
                    │  Reporte final en consola │
                    └───────────────────────────┘
```

**Comunicación entre funciones:** cada módulo recibe únicamente los
parámetros que necesita (nunca el estado completo de la aplicación) y
retorna una estructura de datos (`dict` o `list`) que el orquestador
(`main.py`) reenvía al siguiente módulo. Esto permite probar cada función
de forma aislada (ver `tests/test_aerocargo.py`) sin depender de las demás.

---

## 3. Análisis de Complejidad Computacional

| Función                        | Tiempo        | Espacio       |
|---------------------------------|---------------|---------------|
| `validar_matrices`              | O(N × M)      | O(1)          |
| `calcular_ocupacion`            | O(N × M)      | O(N × M)      |
| `evaluar_balance`                | O(N × M)      | O(N)          |
| `extraer_submatriz_critica`     | O(N × M × k × p) | O(k × p)  |

**Justificación general — O(N × M):**
Las tres primeras funciones recorren cada celda de la matriz exactamente
una vez (un doble ciclo anidado sobre filas y columnas), por lo que su
costo crece linealmente con el número total de celdas N×M. El espacio
adicional que requieren es también proporcional al tamaño de la matriz
que generan (por ejemplo, `calcular_ocupacion` crea una matriz nueva de
igual tamaño para no alterar la original), o constante cuando solo se
acumulan escalares (como en `validar_matrices`).

**Caso especial — `extraer_submatriz_critica`:**
Esta función desliza una ventana de tamaño k×p sobre las (N-k+1)×(M-p+1)
posiciones posibles, y en cada posición suma sus k×p celdas para calcular
el promedio. Esto da un costo de **O(N × M × k × p)** en el peor caso. En
el contexto de este problema k y p son pequeños y fijos en comparación con
N y M (representan una subzona de inspección, no la bodega completa), por
lo que en la práctica el algoritmo se comporta de forma cercana a lineal
respecto al tamaño de la matriz completa. El espacio adicional es O(k × p),
correspondiente a la submatriz que se retorna.

---

## 4. Estructura del Repositorio

```
das172-examen2-apellido-nombre/
├── src/
│   ├── __init__.py
│   └── aerocargo.py        # Los 4 módulos puros requeridos
├── tests/
│   └── test_aerocargo.py   # Casos típicos y de borde
├── main.py                 # Script principal con datos de prueba
├── README.md
└── .gitignore
```

## 5. Ejecución

```bash
# Ejecutar el flujo completo de demostración
python main.py

# Ejecutar las pruebas unitarias
python -m unittest discover tests
```

## 6. Casos de Borde Contemplados

- Matrices mínimas de 2×2.
- Número de columnas M par vs. impar (regla de exclusión de la columna
  central en el balance lateral).
- Celdas con peso en cero.
- Matrices con dimensiones no coincidentes entre cargas y capacidades.
- Matrices irregulares (filas de distinta longitud).
- Ventana de búsqueda k×p mayor a las dimensiones de la matriz de entrada.
