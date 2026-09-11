"""
AeroCargo-Matrix
================
Modulo de funciones puras para auditoria y balance matricial de carga
en la bahia de una aeronave.

Todas las funciones son puras: no usan variables globales y no
modifican las matrices de entrada (se devuelven siempre estructuras
nuevas).
"""

from copy import deepcopy


# ---------------------------------------------------------------------
# 1. Modulo de Validacion y Coherencia Dimensional
# ---------------------------------------------------------------------
def validar_matrices(cargas, capacidades):
    """
    Verifica que 'cargas' y 'capacidades' sean matrices validas y
    compatibles para el analisis.

    Reglas:
      - Ambas deben tener las mismas dimensiones N x M (N >= 2, M >= 2).
      - Todas las filas de cada matriz deben tener igual longitud
        (matriz regular / rectangular).
      - Todos los pesos deben ser >= 0.
      - Todas las capacidades deben ser > 0.

    Parametros:
        cargas (list[list[float]]): matriz N x M de pesos reales (kg).
        capacidades (list[list[float]]): matriz N x M de capacidad
            maxima por celda (kg).

    Retorna:
        bool: True si ambas matrices son validas y compatibles,
              False en caso contrario.
    """
    # Ninguna matriz vacia
    if not cargas or not capacidades:
        return False

    n_cargas = len(cargas)
    n_caps = len(capacidades)

    if n_cargas < 2 or n_caps < 2:
        return False

    if n_cargas != n_caps:
        return False

    # Longitud de la primera fila define M
    m_cargas = len(cargas[0])
    m_caps = len(capacidades[0])

    if m_cargas < 2 or m_caps < 2:
        return False

    if m_cargas != m_caps:
        return False

    # Matriz regular: todas las filas de igual longitud
    for fila in cargas:
        if len(fila) != m_cargas:
            return False
    for fila in capacidades:
        if len(fila) != m_caps:
            return False

    # Rango de valores
    for fila in cargas:
        for peso in fila:
            if peso < 0:
                return False

    for fila in capacidades:
        for cap in fila:
            if cap <= 0:
                return False

    return True


# ---------------------------------------------------------------------
# 2. Modulo de Calculo de Ocupacion y Deteccion de Sobrecarga
# ---------------------------------------------------------------------
def calcular_ocupacion(cargas, capacidades):
    """
    Calcula el porcentaje de ocupacion de cada celda y detecta las
    celdas en estado de sobrecarga (> 100%).

    No modifica las matrices originales.

    Parametros:
        cargas (list[list[float]]): matriz N x M de pesos reales (kg).
        capacidades (list[list[float]]): matriz N x M de capacidad
            maxima por celda (kg).

    Retorna:
        dict: {
            "porcentajes": list[list[float]]  # matriz N x M nueva,
            "sobrecargas": list[tuple[int, int]]  # coords (fila, col)
        }
    """
    n = len(cargas)
    m = len(cargas[0])

    porcentajes = [[0.0 for _ in range(m)] for _ in range(n)]
    sobrecargas = []

    for i in range(n):
        for j in range(m):
            porcentaje = (cargas[i][j] / capacidades[i][j]) * 100.0
            porcentajes[i][j] = porcentaje
            if porcentaje > 100.0:
                sobrecargas.append((i, j))

    return {
        "porcentajes": porcentajes,
        "sobrecargas": sobrecargas,
    }


# ---------------------------------------------------------------------
# 3. Modulo de Evaluacion de Balance y Simetria
# ---------------------------------------------------------------------
def evaluar_balance(cargas, tolerancia):
    """
    Calcula el peso total por fila longitudinal y el desbalance
    lateral (babor vs estribor), evaluando si esta dentro de la
    tolerancia permitida.

    Si el numero de columnas M es par, la matriz se divide en dos
    mitades iguales. Si M es impar, la columna central (eje de
    simetria) se excluye de la comparacion.

    Parametros:
        cargas (list[list[float]]): matriz N x M de pesos reales (kg).
        tolerancia (float): tolerancia maxima de desbalance lateral (kg).

    Retorna:
        dict: {
            "pesos_por_fila": list[float],   # longitud N
            "desbalance_lateral": float,
            "balanceado": bool
        }
    """
    n = len(cargas)
    m = len(cargas[0])

    pesos_por_fila = [sum(fila) for fila in cargas]

    mitad = m // 2
    suma_izquierda = 0.0
    suma_derecha = 0.0

    if m % 2 == 0:
        # M par: dos mitades iguales
        for fila in cargas:
            suma_izquierda += sum(fila[0:mitad])
            suma_derecha += sum(fila[mitad:m])
    else:
        # M impar: se omite la columna central
        for fila in cargas:
            suma_izquierda += sum(fila[0:mitad])
            suma_derecha += sum(fila[mitad + 1:m])

    desbalance_lateral = abs(suma_izquierda - suma_derecha)
    balanceado = desbalance_lateral <= tolerancia

    return {
        "pesos_por_fila": pesos_por_fila,
        "desbalance_lateral": desbalance_lateral,
        "balanceado": balanceado,
    }


# ---------------------------------------------------------------------
# 4. Modulo de Extraccion de Submatriz de Sobrecarga Critica
# ---------------------------------------------------------------------
def extraer_submatriz_critica(matriz_porcentajes, k, p):
    """
    Recorre todas las submatrices contiguas de tamano k x p dentro de
    la matriz de porcentajes de ocupacion y devuelve la que presenta
    mayor promedio de ocupacion (criterio de mayor concentracion de
    sobrecarga).

    Parametros:
        matriz_porcentajes (list[list[float]]): matriz N x M de %
            de ocupacion.
        k (int): numero de filas de la ventana de busqueda.
        p (int): numero de columnas de la ventana de busqueda.

    Retorna:
        list[list[float]]: submatriz k x p con el mayor promedio de
            ocupacion encontrado. Lista vacia si k o p exceden las
            dimensiones de la matriz de entrada.
    """
    n = len(matriz_porcentajes)
    m = len(matriz_porcentajes[0]) if n > 0 else 0

    if k > n or p > m or k <= 0 or p <= 0:
        return []

    mejor_promedio = float("-inf")
    mejor_submatriz = []

    # Ventana deslizante sobre todas las posiciones de origen posibles
    for fila_inicio in range(n - k + 1):
        for col_inicio in range(m - p + 1):
            suma = 0.0
            for i in range(fila_inicio, fila_inicio + k):
                for j in range(col_inicio, col_inicio + p):
                    suma += matriz_porcentajes[i][j]
            promedio = suma / (k * p)

            if promedio > mejor_promedio:
                mejor_promedio = promedio
                mejor_submatriz = [
                    fila[col_inicio:col_inicio + p]
                    for fila in matriz_porcentajes[fila_inicio:fila_inicio + k]
                ]

    return deepcopy(mejor_submatriz)
