"""
Script principal de ejecucion - AeroCargo-Matrix

Demuestra el flujo completo: validacion -> ocupacion/sobrecarga ->
balance -> extraccion de submatriz critica, usando datos de prueba
que simulan una bahia de carga de 4x5.
"""

from src.aerocargo import (
    validar_matrices,
    calcular_ocupacion,
    evaluar_balance,
    extraer_submatriz_critica,
)


def imprimir_matriz(titulo, matriz):
    print(f"\n{titulo}")
    for fila in matriz:
        print("  " + "  ".join(f"{valor:7.2f}" for valor in fila))


def main():
    # Matriz de cargas reales (kg) - bahia de 4 filas x 5 columnas
    cargas = [
        [400, 500, 300, 450, 600],
        [700, 650, 200, 300, 400],
        [100, 900, 800, 250, 150],
        [500, 400, 300, 200, 100],
    ]

    # Matriz de capacidades maximas (kg) por celda
    capacidades = [
        [500, 500, 500, 500, 500],
        [500, 500, 500, 500, 500],
        [500, 500, 500, 500, 500],
        [500, 500, 500, 500, 500],
    ]

    print("=" * 60)
    print("AUDITORIA Y BALANCE MATRICIAL DE CARGA - AeroCargo-Matrix")
    print("=" * 60)

    # 1. Validacion
    es_valida = validar_matrices(cargas, capacidades)
    print(f"\n[1] Validacion dimensional y de coherencia: {es_valida}")

    if not es_valida:
        print("Las matrices de entrada no son validas. Abortando analisis.")
        return

    # 2. Ocupacion y sobrecarga
    resultado_ocupacion = calcular_ocupacion(cargas, capacidades)
    imprimir_matriz("[2] Matriz de porcentaje de ocupacion (%)",
                     resultado_ocupacion["porcentajes"])
    print(f"\nCeldas en sobrecarga (fila, columna): "
          f"{resultado_ocupacion['sobrecargas']}")

    # 3. Balance y simetria
    tolerancia_kg = 150.0
    resultado_balance = evaluar_balance(cargas, tolerancia_kg)
    print(f"\n[3] Peso total por fila: {resultado_balance['pesos_por_fila']}")
    print(f"Desbalance lateral: {resultado_balance['desbalance_lateral']:.2f} kg")
    print(f"Tolerancia: {tolerancia_kg} kg")
    print(f"Balanceado: {resultado_balance['balanceado']}")

    # 4. Submatriz de sobrecarga critica (ventana 2x2)
    k, p = 2, 2
    submatriz_critica = extraer_submatriz_critica(
        resultado_ocupacion["porcentajes"], k, p
    )
    imprimir_matriz(f"[4] Submatriz critica {k}x{p} (mayor % promedio)",
                     submatriz_critica)

    # Verificacion de inmutabilidad: las matrices originales no cambiaron
    print("\n[Verificacion] Matriz de cargas original sin alteraciones:")
    print(cargas)


if __name__ == "__main__":
    main()
