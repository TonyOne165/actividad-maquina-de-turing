"""
Pruebas Unitarias para el Simulador de Máquina de Turing
"""

import unittest
import sys
import os

# Importar las clases del simulador
from turing_simulator import TuringMachine, Tape, TransitionFunction, Direction


class TestTape(unittest.TestCase):
    """Pruebas para la clase Tape"""
    
    def test_tape_initialization(self):
        """Verifica la inicialización correcta de la cinta"""
        tape = Tape("01")
        self.assertEqual(tape.read(), '0')
        self.assertEqual(tape.head_position, 0)
    
    def test_tape_empty_string(self):
        """Verifica el comportamiento con cadena vacía"""
        tape = Tape("")
        self.assertEqual(tape.read(), '_')
    
    def test_tape_read_write(self):
        """Verifica lectura y escritura en la cinta"""
        tape = Tape("01")
        self.assertEqual(tape.read(), '0')
        tape.write('X')
        self.assertEqual(tape.read(), 'X')
    
    def test_tape_movement_right(self):
        """Verifica movimiento a la derecha"""
        tape = Tape("01")
        tape.move(Direction.RIGHT)
        self.assertEqual(tape.head_position, 1)
        self.assertEqual(tape.read(), '1')
    
    def test_tape_movement_left(self):
        """Verifica movimiento a la izquierda"""
        tape = Tape("01")
        tape.move(Direction.RIGHT)
        tape.move(Direction.LEFT)
        self.assertEqual(tape.head_position, 0)
        self.assertEqual(tape.read(), '0')
    
    def test_tape_negative_positions(self):
        """Verifica que la cinta maneje posiciones negativas"""
        tape = Tape("01")
        tape.move(Direction.LEFT)
        self.assertEqual(tape.head_position, -1)
        self.assertEqual(tape.read(), '_')
    
    def test_tape_get_content(self):
        """Verifica la obtención del contenido de la cinta"""
        tape = Tape("0011")
        content = tape.get_content()
        self.assertIn('0', content)
        self.assertIn('1', content)
    
    def test_tape_multiple_writes(self):
        """Verifica múltiples escrituras en diferentes posiciones"""
        tape = Tape("000")
        tape.write('X')
        tape.move(Direction.RIGHT)
        tape.write('Y')
        self.assertEqual(tape.tape[0], 'X')
        self.assertEqual(tape.tape[1], 'Y')


class TestTransitionFunction(unittest.TestCase):
    """Pruebas para la clase TransitionFunction"""
    
    def test_add_transition(self):
        """Verifica agregar transiciones"""
        tf = TransitionFunction()
        tf.add_transition('q0', '0', 'q1', 'X', 'R')
        
        result = tf.get_transition('q0', '0')
        self.assertIsNotNone(result)
        self.assertEqual(result[0], 'q1')
        self.assertEqual(result[1], 'X')
        self.assertEqual(result[2], Direction.RIGHT)
    
    def test_add_transition_left(self):
        """Verifica agregar transición con movimiento izquierdo"""
        tf = TransitionFunction()
        tf.add_transition('q0', '1', 'q2', 'Y', 'L')
        
        result = tf.get_transition('q0', '1')
        self.assertEqual(result[2], Direction.LEFT)
    
    def test_undefined_transition(self):
        """Verifica comportamiento con transición no definida"""
        tf = TransitionFunction()
        result = tf.get_transition('q0', '1')
        self.assertIsNone(result)
    
    def test_load_from_dict(self):
        """Verifica carga de transiciones desde diccionario"""
        tf = TransitionFunction()
        transitions = [
            {
                'current_state': 'q0',
                'read_symbol': '0',
                'next_state': 'q1',
                'write_symbol': 'X',
                'direction': 'R'
            }
        ]
        tf.load_from_dict(transitions)
        
        result = tf.get_transition('q0', '0')
        self.assertIsNotNone(result)
    
    def test_multiple_transitions(self):
        """Verifica múltiples transiciones desde el mismo estado"""
        tf = TransitionFunction()
        tf.add_transition('q0', '0', 'q1', 'X', 'R')
        tf.add_transition('q0', '1', 'q2', 'Y', 'L')
        
        result1 = tf.get_transition('q0', '0')
        result2 = tf.get_transition('q0', '1')
        
        self.assertEqual(result1[0], 'q1')
        self.assertEqual(result2[0], 'q2')


class TestTuringMachineBasic(unittest.TestCase):
    """Pruebas básicas para la Máquina de Turing"""
    
    def setUp(self):
        """Configuración inicial para cada prueba"""
        # Crear una MT simple que acepta solo "0"
        self.tf = TransitionFunction()
        self.tf.add_transition('q0', '0', 'q_accept', '0', 'R')
        
        self.tm = TuringMachine(
            states={'q0', 'q_accept', 'q_reject'},
            input_alphabet={'0', '1'},
            tape_alphabet={'0', '1', '_'},
            transition_function=self.tf,
            initial_state='q0',
            accept_states={'q_accept'},
            reject_states={'q_reject'},
            blank_symbol='_'
        )
    
    def test_load_input(self):
        """Verifica la carga de entrada"""
        self.tm.load_input("0")
        self.assertEqual(self.tm.current_state, 'q0')
        self.assertEqual(self.tm.step_count, 0)
    
    def test_simple_acceptance(self):
        """Verifica aceptación de cadena simple"""
        accepted, result = self.tm.run("0")
        self.assertTrue(accepted)
        self.assertEqual(result, "ACEPTADA")
    
    def test_simple_rejection(self):
        """Verifica rechazo de cadena simple"""
        accepted, result = self.tm.run("1")
        self.assertFalse(accepted)
    
    def test_history_recording(self):
        """Verifica que se registre el historial de configuraciones"""
        self.tm.run("0")
        history = self.tm.get_history()
        self.assertGreater(len(history), 0)
    
    def test_step_count(self):
        """Verifica el conteo de pasos"""
        self.tm.run("0")
        self.assertGreater(self.tm.step_count, 0)


class TestTuringMachineEqual01(unittest.TestCase):
    """Pruebas para la MT que acepta igual número de 0s y 1s"""
    
    @classmethod
    def setUpClass(cls):
        """Configuración única para todas las pruebas"""
        try:
            cls.tm = TuringMachine.from_json('mt_equal_01.json')
        except FileNotFoundError:
            cls.tm = None
    
    def setUp(self):
        """Verifica que la MT esté cargada"""
        if self.tm is None:
            self.skipTest("Archivo de configuración mt_equal_01.json no encontrado")
    
    def test_empty_string(self):
        """Caso límite: cadena vacía (debe aceptar)"""
        accepted, result = self.tm.run("")
        self.assertTrue(accepted, "La cadena vacía debe ser aceptada")
        self.assertEqual(result, "ACEPTADA")
    
    def test_simple_01(self):
        """Caso básico: '01' (debe aceptar)"""
        accepted, result = self.tm.run("01")
        self.assertTrue(accepted, "La cadena '01' debe ser aceptada")
        self.assertEqual(result, "ACEPTADA")
    
    def test_simple_10(self):
        """Caso básico: '10' (debe aceptar)"""
        accepted, result = self.tm.run("10")
        self.assertTrue(accepted, "La cadena '10' debe ser aceptada")
        self.assertEqual(result, "ACEPTADA")
    
    def test_balanced_0011(self):
        """Caso: '0011' (debe aceptar)"""
        accepted, result = self.tm.run("0011")
        self.assertTrue(accepted, "La cadena '0011' debe ser aceptada")
        self.assertEqual(result, "ACEPTADA")
    
    def test_balanced_1100(self):
        """Caso: '1100' (debe aceptar)"""
        accepted, result = self.tm.run("1100")
        self.assertTrue(accepted, "La cadena '1100' debe ser aceptada")
        self.assertEqual(result, "ACEPTADA")
    
    def test_balanced_0101(self):
        """Caso: '0101' (debe aceptar)"""
        accepted, result = self.tm.run("0101")
        self.assertTrue(accepted, "La cadena '0101' debe ser aceptada")
        self.assertEqual(result, "ACEPTADA")
    
    def test_balanced_1010(self):
        """Caso: '1010' (debe aceptar)"""
        accepted, result = self.tm.run("1010")
        self.assertTrue(accepted, "La cadena '1010' debe ser aceptada")
        self.assertEqual(result, "ACEPTADA")
    
    def test_unbalanced_001(self):
        """Caso: '001' - más 0s (debe rechazar)"""
        accepted, result = self.tm.run("001")
        self.assertFalse(accepted, "La cadena '001' debe ser rechazada")
        self.assertEqual(result, "RECHAZADA")
    
    def test_unbalanced_011(self):
        """Caso: '011' - más 1s (debe rechazar)"""
        accepted, result = self.tm.run("011")
        self.assertFalse(accepted, "La cadena '011' debe ser rechazada")
        self.assertEqual(result, "RECHAZADA")
    
    def test_single_0(self):
        """Caso: '0' - solo un 0 (debe rechazar)"""
        accepted, result = self.tm.run("0")
        self.assertFalse(accepted, "La cadena '0' debe ser rechazada")
        self.assertEqual(result, "RECHAZADA")
    
    def test_single_1(self):
        """Caso: '1' - solo un 1 (debe rechazar)"""
        accepted, result = self.tm.run("1")
        self.assertFalse(accepted, "La cadena '1' debe ser rechazada")
        self.assertEqual(result, "RECHAZADA")
    
    def test_balanced_000111(self):
        """Caso: '000111' - tres 0s y tres 1s (debe aceptar)"""
        accepted, result = self.tm.run("000111")
        self.assertTrue(accepted, "La cadena '000111' debe ser aceptada")
        self.assertEqual(result, "ACEPTADA")
    
    def test_unbalanced_00011(self):
        """Caso: '00011' - desbalanceada (debe rechazar)"""
        accepted, result = self.tm.run("00011")
        self.assertFalse(accepted, "La cadena '00011' debe ser rechazada")
        self.assertEqual(result, "RECHAZADA")
    
    def test_unbalanced_0001111(self):
        """Caso: '0001111' - desbalanceada (debe rechazar)"""
        accepted, result = self.tm.run("0001111")
        self.assertFalse(accepted, "La cadena '0001111' debe ser rechazada")
        self.assertEqual(result, "RECHAZADA")
    
    def test_balanced_01010101(self):
        """Caso: '01010101' - alternados (debe aceptar)"""
        accepted, result = self.tm.run("01010101")
        self.assertTrue(accepted, "La cadena '01010101' debe ser aceptada")
        self.assertEqual(result, "ACEPTADA")
    
    def test_step_limit(self):
        """Verifica que la MT no entre en bucle infinito"""
        # Usar una cadena balanceada para verificar que termina en tiempo razonable
        accepted, result = self.tm.run("0011", max_steps=1000)
        self.assertNotEqual(result, "BUCLE DETECTADO (límite de pasos alcanzado)")


class TestTuringMachineFromJSON(unittest.TestCase):
    """Pruebas para la carga desde JSON"""
    
    def test_load_from_json_success(self):
        """Verifica que se pueda cargar una MT desde JSON"""
        try:
            tm = TuringMachine.from_json('mt_equal_01.json')
            self.assertIsNotNone(tm)
            self.assertIsNotNone(tm.states)
            self.assertIsNotNone(tm.initial_state)
            self.assertIsNotNone(tm.accept_states)
            self.assertIsNotNone(tm.reject_states)
        except FileNotFoundError:
            self.skipTest("Archivo mt_equal_01.json no encontrado")
    
    def test_json_structure(self):
        """Verifica la estructura básica de la MT cargada"""
        try:
            tm = TuringMachine.from_json('mt_equal_01.json')
            self.assertIn(tm.initial_state, tm.states)
            self.assertTrue(tm.accept_states.issubset(tm.states))
            self.assertTrue(tm.reject_states.issubset(tm.states))
        except FileNotFoundError:
            self.skipTest("Archivo mt_equal_01.json no encontrado")


def run_tests():
    """Función para ejecutar todas las pruebas con información detallada"""
    # Crear el test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Agregar todas las clases de prueba
    suite.addTests(loader.loadTestsFromTestCase(TestTape))
    suite.addTests(loader.loadTestsFromTestCase(TestTransitionFunction))
    suite.addTests(loader.loadTestsFromTestCase(TestTuringMachineBasic))
    suite.addTests(loader.loadTestsFromTestCase(TestTuringMachineEqual01))
    suite.addTests(loader.loadTestsFromTestCase(TestTuringMachineFromJSON))
    
    # Ejecutar las pruebas con verbosidad
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Imprimir resumen
    print("\n" + "="*70)
    print("RESUMEN DE PRUEBAS")
    print("="*70)
    print(f"Pruebas ejecutadas: {result.testsRun}")
    print(f"Pruebas exitosas: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Pruebas fallidas: {len(result.failures)}")
    print(f"Errores: {len(result.errors)}")
    print(f"Pruebas omitidas: {len(result.skipped)}")
    print("="*70)
    
    return result


if __name__ == "__main__":
    # Si se ejecuta directamente, correr todas las pruebas
    run_tests()
