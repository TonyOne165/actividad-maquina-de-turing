"""
Simulador de Máquina de Turing
Implementación completa de una Máquina de Turing con interfaz CLI
"""

import json
from typing import Dict, List, Set, Tuple, Optional
from enum import Enum


class Direction(Enum):
    """Dirección de movimiento del cabezal"""
    LEFT = 'L'
    RIGHT = 'R'


class Tape:
    """
    Representa la cinta infinita de la Máquina de Turing.
    Implementada como un diccionario para simular infinitud.
    """
    
    def __init__(self, input_string: str, blank_symbol: str = '_'):
        self.blank_symbol = blank_symbol
        self.tape: Dict[int, str] = {}
        
        # Inicializar la cinta con la cadena de entrada
        for i, symbol in enumerate(input_string):
            self.tape[i] = symbol
        
        self.head_position = 0
    
    def read(self) -> str:
        """Lee el símbolo en la posición actual del cabezal"""
        return self.tape.get(self.head_position, self.blank_symbol)
    
    def write(self, symbol: str):
        """Escribe un símbolo en la posición actual"""
        self.tape[self.head_position] = symbol
    
    def move(self, direction: Direction):
        """Mueve el cabezal en la dirección especificada"""
        if direction == Direction.LEFT:
            self.head_position -= 1
        elif direction == Direction.RIGHT:
            self.head_position += 1
    
    def get_content(self, window: int = 20) -> str:
        """
        Retorna el contenido visible de la cinta
        window: número de posiciones a mostrar alrededor del cabezal
        """
        if not self.tape:
            return self.blank_symbol
        
        min_pos = min(min(self.tape.keys()), self.head_position - window // 2)
        max_pos = max(max(self.tape.keys()), self.head_position + window // 2)
        
        content = ""
        for i in range(min_pos, max_pos + 1):
            content += self.tape.get(i, self.blank_symbol)
        
        return content
    
    def get_head_indicator(self, window: int = 20) -> str:
        """Retorna una cadena que indica la posición del cabezal"""
        if not self.tape:
            return "^"
        
        min_pos = min(min(self.tape.keys()), self.head_position - window // 2)
        offset = self.head_position - min_pos
        
        return " " * offset + "^"


class TransitionFunction:
    """
    Representa la función de transición δ: Q × Γ → Q × Γ × {L, R}
    """
    
    def __init__(self):
        # Diccionario: (estado_actual, símbolo_leído) -> (nuevo_estado, símbolo_escribir, dirección)
        self.transitions: Dict[Tuple[str, str], Tuple[str, str, Direction]] = {}
    
    def add_transition(self, current_state: str, read_symbol: str,
                      next_state: str, write_symbol: str, direction: str):
        """Agrega una transición a la función"""
        dir_enum = Direction.LEFT if direction == 'L' else Direction.RIGHT
        self.transitions[(current_state, read_symbol)] = (next_state, write_symbol, dir_enum)
    
    def get_transition(self, current_state: str, read_symbol: str) -> Optional[Tuple[str, str, Direction]]:
        """Obtiene la transición para un estado y símbolo dados"""
        return self.transitions.get((current_state, read_symbol))
    
    def load_from_dict(self, transitions_dict: List[Dict]):
        """Carga transiciones desde un diccionario"""
        for trans in transitions_dict:
            self.add_transition(
                trans['current_state'],
                trans['read_symbol'],
                trans['next_state'],
                trans['write_symbol'],
                trans['direction']
            )


class TuringMachine:
    """
    Implementación de una Máquina de Turing
    M = (Q, Σ, Γ, δ, q0, qaccept, qreject)
    """
    
    def __init__(self, states: Set[str], input_alphabet: Set[str],
                 tape_alphabet: Set[str], transition_function: TransitionFunction,
                 initial_state: str, accept_states: Set[str],
                 reject_states: Set[str], blank_symbol: str = '_'):
        
        self.states = states
        self.input_alphabet = input_alphabet
        self.tape_alphabet = tape_alphabet
        self.transition_function = transition_function
        self.initial_state = initial_state
        self.accept_states = accept_states
        self.reject_states = reject_states
        self.blank_symbol = blank_symbol
        
        self.current_state = initial_state
        self.tape: Optional[Tape] = None
        self.step_count = 0
        self.history: List[str] = []
    
    def load_input(self, input_string: str):
        """Carga una cadena de entrada en la cinta"""
        self.tape = Tape(input_string, self.blank_symbol)
        self.current_state = self.initial_state
        self.step_count = 0
        self.history = []
        self._record_configuration()
    
    def _record_configuration(self):
        """Registra la configuración actual en el historial"""
        if self.tape:
            config = f"Paso {self.step_count}: Estado={self.current_state}, " \
                    f"Posición={self.tape.head_position}, " \
                    f"Cinta={self.tape.get_content()}"
            self.history.append(config)
    
    def step(self) -> bool:
        """
        Ejecuta un paso de la máquina
        Retorna True si puede continuar, False si termina
        """
        if not self.tape:
            raise ValueError("No hay entrada cargada")
        
        # Verificar si estamos en un estado final
        if self.current_state in self.accept_states:
            return False
        if self.current_state in self.reject_states:
            return False
        
        # Leer símbolo actual
        current_symbol = self.tape.read()
        
        # Obtener transición
        transition = self.transition_function.get_transition(
            self.current_state, current_symbol
        )
        
        if transition is None:
            # No hay transición definida -> rechazar
            self.current_state = list(self.reject_states)[0]
            return False
        
        next_state, write_symbol, direction = transition
        
        # Ejecutar transición
        self.tape.write(write_symbol)
        self.tape.move(direction)
        self.current_state = next_state
        self.step_count += 1
        
        self._record_configuration()
        
        return True
    
    def run(self, input_string: str, max_steps: int = 1000, step_by_step: bool = False) -> Tuple[bool, str]:
        """
        Ejecuta la máquina sobre una cadena de entrada
        
        Args:
            input_string: cadena a procesar
            max_steps: límite de pasos para detectar bucles
            step_by_step: si True, muestra cada paso
        
        Returns:
            (aceptada, mensaje)
        """
        self.load_input(input_string)
        
        if step_by_step:
            print(f"\n{'='*60}")
            print(f"Ejecutando MT con entrada: '{input_string}'")
            print(f"{'='*60}\n")
            self.print_configuration()
        
        while self.step_count < max_steps:
            can_continue = self.step()
            
            if step_by_step:
                self.print_configuration()
                input("Presione Enter para continuar...")
            
            if not can_continue:
                break
        
        # Determinar resultado
        if self.current_state in self.accept_states:
            return True, "ACEPTADA"
        elif self.current_state in self.reject_states:
            return False, "RECHAZADA"
        else:
            return False, "BUCLE DETECTADO (límite de pasos alcanzado)"
    
    def print_configuration(self):
        """Imprime la configuración actual de la máquina"""
        if not self.tape:
            return
        
        print(f"\nPaso {self.step_count}:")
        print(f"Estado actual: {self.current_state}")
        print(f"Posición del cabezal: {self.tape.head_position}")
        print(f"Cinta: {self.tape.get_content()}")
        print(f"       {self.tape.get_head_indicator()}")
        print(f"Símbolo leído: '{self.tape.read()}'")
    
    def get_history(self) -> List[str]:
        """Retorna el historial de configuraciones"""
        return self.history
    
    @classmethod
    def from_json(cls, json_file: str) -> 'TuringMachine':
        """Carga una Máquina de Turing desde un archivo JSON"""
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Crear función de transición
        trans_func = TransitionFunction()
        trans_func.load_from_dict(data['transitions'])
        
        # Crear máquina
        return cls(
            states=set(data['states']),
            input_alphabet=set(data['input_alphabet']),
            tape_alphabet=set(data['tape_alphabet']),
            transition_function=trans_func,
            initial_state=data['initial_state'],
            accept_states=set(data['accept_states']),
            reject_states=set(data['reject_states']),
            blank_symbol=data.get('blank_symbol', '_')
        )


def main():
    """Función principal - Interfaz CLI"""
    print("="*60)
    print("SIMULADOR DE MÁQUINA DE TURING")
    print("="*60)
    
    # Cargar máquina desde archivo
    try:
        tm = TuringMachine.from_json('mt_equal_01.json')
        print("\n✓ Máquina de Turing cargada correctamente")
        print(f"  Estados: {tm.states}")
        print(f"  Estado inicial: {tm.initial_state}")
        print(f"  Estados de aceptación: {tm.accept_states}")
    except FileNotFoundError:
        print("\n✗ Error: No se encontró el archivo 'mt_equal_01.json'")
        print("  Por favor, cree el archivo de configuración primero.")
        return
    
    # Menú principal
    while True:
        print("\n" + "="*60)
        print("MENÚ PRINCIPAL")
        print("="*60)
        print("1. Ejecutar en modo paso a paso")
        print("2. Ejecutar en modo automático")
        print("3. Ejecutar pruebas de casos")
        print("4. Salir")
        
        opcion = input("\nSeleccione una opción: ").strip()
        
        if opcion == '1':
            cadena = input("\nIngrese la cadena de entrada: ").strip()
            accepted, result = tm.run(cadena, step_by_step=True)
            print(f"\n{'='*60}")
            print(f"RESULTADO: {result}")
            print(f"{'='*60}")
            
        elif opcion == '2':
            cadena = input("\nIngrese la cadena de entrada: ").strip()
            accepted, result = tm.run(cadena, step_by_step=False)
            print(f"\nResultado: {result}")
            print(f"Pasos ejecutados: {tm.step_count}")
            
        elif opcion == '3':
            run_test_cases(tm)
            
        elif opcion == '4':
            print("\n¡Hasta luego!")
            break
        
        else:
            print("\n✗ Opción inválida")


def run_test_cases(tm: TuringMachine):
    """Ejecuta casos de prueba predefinidos"""
    test_cases = [
        ("", True, "Cadena vacía"),
        ("01", True, "01 - Un 0 y un 1"),
        ("0011", True, "0011 - Dos 0s y dos 1s"),
        ("001", False, "001 - Desbalanceada (más 0s)"),
        ("011", False, "011 - Desbalanceada (más 1s)"),
        ("000111", True, "000111 - Tres 0s y tres 1s"),
        ("10", True, "10 - Un 1 y un 0"),
        ("0", False, "0 - Solo un 0"),
        ("1", False, "1 - Solo un 1"),
    ]
    
    print("\n" + "="*60)
    print("EJECUTANDO CASOS DE PRUEBA")
    print("="*60)
    
    passed = 0
    failed = 0
    
    for input_str, expected, description in test_cases:
        accepted, result = tm.run(input_str, step_by_step=False)
        status = "✓ PASS" if accepted == expected else "✗ FAIL"
        
        print(f"\n{status} | {description}")
        print(f"  Entrada: '{input_str}'")
        print(f"  Esperado: {'ACEPTAR' if expected else 'RECHAZAR'}")
        print(f"  Obtenido: {result}")
        print(f"  Pasos: {tm.step_count}")
        
        if accepted == expected:
            passed += 1
        else:
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"RESUMEN: {passed} pasaron, {failed} fallaron de {len(test_cases)} pruebas")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
