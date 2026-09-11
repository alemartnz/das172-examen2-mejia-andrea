"""
Pruebas unitarias para el modulo aerocargo.

Cubre casos tipicos y casos de borde:
- matrices minimas (2x2)
- columnas pares e impares
- celdas en cero
- dimensiones no coincidentes
- inmutabilidad de las matrices de entrada
"""

import sys
import os
import unittest
from copy import deepcopy

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.aerocargo import (
    validar_matrices,
    calcular_ocupacion,
    evaluar_balance,
    extraer_submatriz_critica,
)


class TestValidarMatrices(unittest.TestCase):

    def test_matriz_valida_tipica(self):
        cargas = [[100, 200], [300, 400]]
        capacidades = [[500, 500], [500, 500]]
        self.assertTrue(validar_matrices(cargas, capacidades))

    def test_matriz_minima_2x2_valida(self):
        cargas = [[0, 0], [0, 0]]
        capacidades = [[100, 100], [100, 100]]
        self.assertTrue(validar_matrices(cargas, capacidades))

    def test_dimensiones_no_coincidentes(self):
        cargas = [[100, 200, 300], [400, 500, 600]]
        capacidades = [[500, 500], [500, 500]]
        self.assertFalse(validar_matrices(cargas, capacidades))

    def test_matriz_irregular_filas_desiguales(self):
        cargas = [[100, 200], [300]]
        capacidades = [[500, 500], [500, 500]]
        self.assertFalse(validar_matrices(cargas, capacidades))

    def test_peso_negativo_invalido(self):
        cargas = [[-10, 200], [300, 400]]
        capacidades = [[500, 500], [500, 500]]
        self.assertFalse(validar_matrices(cargas, capacidades))

    def test_capacidad_cero_invalida(self):
        cargas = [[100, 200], [300, 400]]
        capacidades = [[0, 500], [500, 500]]
        self.assertFalse(validar_matrices(cargas, capacidades))

    def test_matriz_menor_a_2x2_invalida(self):
        cargas = [[100]]
        capacidades = [[500]]
        self.assertFalse(validar_matrices(cargas, capacidades))


class TestCalcularOcupacion(unittest.TestCase):

    def test_ocupacion_sin_sobrecarga(self):
        cargas = [[100, 200], [300, 400]]
        capacidades = [[500, 500], [500, 500]]
        resultado = calcular_ocupacion(cargas, capacidades)
        self.assertEqual(resultado["porcentajes"][0][0], 20.0)
        self.assertEqual(resultado["sobrecargas"], [])

    def test_ocupacion_con_sobrecarga(self):
        cargas = [[600, 200], [300, 400]]
        capacidades = [[500, 500], [500, 500]]
        resultado = calcular_ocupacion(cargas, capacidades)
        self.assertIn((0, 0), resultado["sobrecargas"])

    def test_celda_en_cero(self):
        cargas = [[0, 200], [300, 400]]
        capacidades = [[500, 500], [500, 500]]
        resultado = calcular_ocupacion(cargas, capacidades)
        self.assertEqual(resultado["porcentajes"][0][0], 0.0)

    def test_no_modifica_matrices_originales(self):
        cargas = [[100, 200], [300, 400]]
        capacidades = [[500, 500], [500, 500]]
        cargas_copia = deepcopy(cargas)
        capacidades_copia = deepcopy(capacidades)
        calcular_ocupacion(cargas, capacidades)
        self.assertEqual(cargas, cargas_copia)
        self.assertEqual(capacidades, capacidades_copia)


class TestEvaluarBalance(unittest.TestCase):

    def test_columnas_pares_balanceado(self):
        cargas = [[100, 100, 100, 100], [100, 100, 100, 100]]
        resultado = evaluar_balance(cargas, tolerancia=10.0)
        self.assertEqual(resultado["desbalance_lateral"], 0.0)
        self.assertTrue(resultado["balanceado"])

    def test_columnas_pares_desbalanceado(self):
        cargas = [[500, 100, 100, 100], [500, 100, 100, 100]]
        resultado = evaluar_balance(cargas, tolerancia=10.0)
        self.assertFalse(resultado["balanceado"])

    def test_columnas_impares_omite_columna_central(self):
        # M = 5, columna central (indice 2) se excluye del balance
        cargas = [[100, 100, 999, 100, 100]]
        resultado = evaluar_balance(cargas, tolerancia=0.0)
        self.assertEqual(resultado["desbalance_lateral"], 0.0)
        self.assertTrue(resultado["balanceado"])

    def test_pesos_por_fila_correctos(self):
        cargas = [[100, 200], [300, 400]]
        resultado = evaluar_balance(cargas, tolerancia=1000.0)
        self.assertEqual(resultado["pesos_por_fila"], [300, 700])


class TestExtraerSubmatrizCritica(unittest.TestCase):

    def test_submatriz_2x2_tipica(self):
        matriz = [
            [10, 20, 30],
            [40, 90, 95],
            [15, 85, 92],
        ]
        submatriz = extraer_submatriz_critica(matriz, 2, 2)
        # La zona de mayor concentracion esta en la esquina inferior derecha
        self.assertEqual(submatriz, [[90, 95], [85, 92]])

    def test_ventana_mayor_a_matriz_devuelve_vacio(self):
        matriz = [[10, 20], [30, 40]]
        submatriz = extraer_submatriz_critica(matriz, 3, 3)
        self.assertEqual(submatriz, [])

    def test_ventana_igual_a_matriz_completa(self):
        matriz = [[10, 20], [30, 40]]
        submatriz = extraer_submatriz_critica(matriz, 2, 2)
        self.assertEqual(submatriz, matriz)

    def test_ventana_1x1_devuelve_celda_maxima(self):
        matriz = [[10, 20], [99, 40]]
        submatriz = extraer_submatriz_critica(matriz, 1, 1)
        self.assertEqual(submatriz, [[99]])


if __name__ == "__main__":
    unittest.main()
