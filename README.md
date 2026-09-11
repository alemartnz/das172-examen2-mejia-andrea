# AeroCargo-Matrix

**Universidad Don Bosco — Facultad de Aeronáutica**
**Asignatura:** DAS172 — Desarrollo de Algoritmos para la Simulación de Sistemas
**Evaluación:** EVA106 — Examen Teórico Unidad II: Funciones y Arreglos
**Reto:** Auditoría y Balance Matricial de Distribución de Carga en Bahía de Aeronave

---

## 1. Explicación del Problema

La distribución del peso dentro de la bodega de carga (*cargo hold*) de una
aeronave no es un detalle logístico menor: es una condición operativa y de
seguridad. El piso de carga se modela como una cuadrícula de **N filas
(dirección longitudinal, de proa a popa) por M columnas (dirección
transversal, de babor a estribor)**, donde cada celda representa un
compartimiento de estibado con un peso real colocado y una capacidad máxima
estructural.

Dos condiciones deben cumplirse simultáneamente en cada vuelo:

1. **Capacidad estructural del piso.** Ninguna celda puede exceder el peso
   máximo que su sección del fuselaje puede soportar. Superarlo (>100% de
   ocupación) compromete la integridad estructural de esa zona.
2. **Balance y simetría.** El peso debe repartirse de forma equilibrada
   entre el lado izquierdo y el derecho de la aeronave. Un desbalance
   lateral excesivo desplaza el centro de gravedad lateral, afectando la
   maniobrabilidad y estabilidad en vuelo.

Este proyecto automatiza esa auditoría: valida los datos de entrada,
calcula el porcentaje de ocupación de cada celda, detecta sobrecargas,
evalúa el balance lateral (respetando la regla de la columna central en
matrices de M impar) y localiza la subzona de mayor concentración crítica
dentro de la bodega mediante una ventana deslizante k×p.

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
