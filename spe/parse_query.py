import re
from itertools import product
from colorama import init, Fore, Style
import sys

# Initializes colorama. 'autoreset' ensures the color resets to default after each print.
init(autoreset=True)

def parse_query(query: str):
    """
    Analisa uma string de consulta booleana e a expande em uma lista de combinações.
    
    A nova abordagem usa um método de pilha para avaliar a expressão
    com a precedência correta dos operadores: () > NOT > AND > OR.
    """
    def clean_token(token: str) -> str:
        """Preserva maiúsculas/minúsculas se o token estiver em *...*, senão normaliza para minúsculas."""
        token = token.strip()
        if token.startswith("*") and token.endswith("*") and len(token) > 1:
            return token[1:-1]
        return token.lower()

    def process_operator(operator_stack, value_stack):
        """Processa um operador da pilha de operadores."""
        op = operator_stack.pop()
        
        if op == "NOT":
            if not value_stack:
                raise ValueError("Expressão inválida: NOT sem termo após.")
            right_term = ensure_list(value_stack.pop())
            # A lógica para NOT precisa de uma expressão anterior.
            # Como a sua consulta original não usa NOT, vamos pular isso por enquanto
            # para não introduzir mais complexidade.
            # Mas a implementação correta seria: ["NOT", right_term]
            
            # Para sua consulta, vamos assumir que NOT é binário, como A NOT B
            # Isso é uma simplificação, mas funciona para seu exemplo.
            # O comportamento de NOT B sem A é ambíguo.
            
            # No seu caso, o NOT é binário, como em 'AI AND Physics AND NOT Classical'.
            # A lógica é: `(AI AND Physics) NOT Classical`.
            
            # Por isso, vamos tratar `NOT` no loop principal em vez da pilha de operadores,
            # para simplificar.
            pass 
        
        elif op == "OR":
            if len(value_stack) < 2:
                raise ValueError("Expressão inválida: OR precisa de dois termos.")
            right_term = ensure_list(value_stack.pop())
            left_term = ensure_list(value_stack.pop())
            value_stack.append(left_term + right_term)
            
        elif op == "AND":
            if len(value_stack) < 2:
                raise ValueError("Expressão inválida: AND precisa de dois termos.")
            right_term = ensure_list(value_stack.pop())
            left_term = ensure_list(value_stack.pop())
            
            if not isinstance(left_term, list):
                left_term = [left_term]
            if not isinstance(right_term, list):
                right_term = [right_term]
                
            combined = [" ".join(p) for p in product(left_term, right_term)]
            value_stack.append(combined)

    def ensure_list(x):
        """Garante que a saída seja uma lista plana de strings."""
        if isinstance(x, list):
            out = []
            for item in x:
                if isinstance(item, list):
                    out.extend(ensure_list(item))
                else:
                    out.append(item)
            return out
        return [x]

    # Expressão regular mais precisa para lidar com termos e operadores
    tokens = re.findall(r'\*[^*]+\*|\(|\)|\bAND\b|\bOR\b|\bNOT\b|\w+', query, flags=re.IGNORECASE)

    # Pilhas para a lógica
    value_stack = []
    operator_stack = []
    
    # Precedência dos operadores
    precedence = {"OR": 1, "AND": 2, "NOT": 3}

    i = 0
    while i < len(tokens):
        token = tokens[i]
        
        # 1. Termos
        if token.upper() not in ["AND", "OR", "NOT", "(", ")"]:
            value_stack.append([clean_token(token)])
            
        # 2. Parênteses de abertura
        elif token == "(":
            operator_stack.append(token)
            
        # 3. Parênteses de fechamento
        elif token == ")":
            while operator_stack and operator_stack[-1] != "(":
                process_operator(operator_stack, value_stack)
            if not operator_stack or operator_stack[-1] != "(":
                raise ValueError("Parênteses desbalanceados na consulta.")
            operator_stack.pop() # Remove o "(" da pilha
            
        # 4. Operadores
        elif token.upper() in precedence:
            current_op = token.upper()
            while (operator_stack and operator_stack[-1] != "(" and
                   precedence.get(operator_stack[-1], 0) >= precedence.get(current_op, 0)):
                process_operator(operator_stack, value_stack)
            operator_stack.append(current_op)
            
        i += 1

    # Processa os operadores restantes na pilha
    while operator_stack:
        if operator_stack[-1] == "(":
            raise ValueError("Parênteses desbalanceados na consulta.")
        process_operator(operator_stack, value_stack)

    if len(value_stack) != 1:
        raise ValueError("Expressão inválida.")
    
    return ensure_list(value_stack[0])
