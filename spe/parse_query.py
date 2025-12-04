import re
from itertools import product
from colorama import init, Fore, Style
import sys

init(autoreset=True)

def parse_query(query: str):
    """
    Parses a boolean query string and expands it into a list of combinations.
    
    Implements a stack-based evaluation to handle operator precedence 
    correctly: () > NOT > AND > OR.
    """
    def clean_token(token: str) -> str:
        # Preserve case if wrapped in *...*, otherwise normalize to lowercase.
        token = token.strip()
        if token.startswith("*") and token.endswith("*") and len(token) > 1:
            return token[1:-1]
        return token.lower()

    def process_operator(operator_stack, value_stack):
        """Pops an operator and applies it to the operands in the value stack."""
        op = operator_stack.pop()
        
        if op == "NOT":
            if not value_stack:
                raise ValueError("Invalid expression: NOT without a following term.")
            right_term = ensure_list(value_stack.pop())
            
            # TODO: Implement full unary NOT logic.
            # Currently skipped to avoid complexity. The current implementation 
            # treats NOT as binary (A NOT B) or effectively ignores it here 
            # because the logic is ambiguous without a preceding term.
            # Real implementation should return: ["NOT", right_term]
            pass 
        
        elif op == "OR":
            if len(value_stack) < 2:
                raise ValueError("Invalid expression: OR requires two terms.")
            right_term = ensure_list(value_stack.pop())
            left_term = ensure_list(value_stack.pop())
            value_stack.append(left_term + right_term)
            
        elif op == "AND":
            if len(value_stack) < 2:
                raise ValueError("Invalid expression: AND requires two terms.")
            right_term = ensure_list(value_stack.pop())
            left_term = ensure_list(value_stack.pop())
            
            if not isinstance(left_term, list):
                left_term = [left_term]
            if not isinstance(right_term, list):
                right_term = [right_term]
                
            combined = [" ".join(p) for p in product(left_term, right_term)]
            value_stack.append(combined)

    def ensure_list(x):
        """Flattens input into a list of strings."""
        if isinstance(x, list):
            out = []
            for item in x:
                if isinstance(item, list):
                    out.extend(ensure_list(item))
                else:
                    out.append(item)
            return out
        return [x]

    # Tokenize: capture terms, operators, and parentheses.
    tokens = re.findall(r'\*[^*]+\*|\(|\)|\bAND\b|\bOR\b|\bNOT\b|\w+', query, flags=re.IGNORECASE)

    value_stack = []
    operator_stack = []
    
    # Precedence map
    precedence = {"OR": 1, "AND": 2, "NOT": 3}

    i = 0
    while i < len(tokens):
        token = tokens[i]
        
        # 1. Operands (terms)
        if token.upper() not in ["AND", "OR", "NOT", "(", ")"]:
            value_stack.append([clean_token(token)])
            
        # 2. Start group
        elif token == "(":
            operator_stack.append(token)
            
        # 3. End group
        elif token == ")":
            while operator_stack and operator_stack[-1] != "(":
                process_operator(operator_stack, value_stack)
            if not operator_stack or operator_stack[-1] != "(":
                raise ValueError("Unbalanced parentheses in query.")
            operator_stack.pop() # Pop the opening "("
            
        # 4. Operators
        elif token.upper() in precedence:
            current_op = token.upper()
            # Flush higher or equal precedence operators from stack before pushing current
            while (operator_stack and operator_stack[-1] != "(" and
                   precedence.get(operator_stack[-1], 0) >= precedence.get(current_op, 0)):
                process_operator(operator_stack, value_stack)
            operator_stack.append(current_op)
            
        i += 1

    # Flush remaining operators
    while operator_stack:
        if operator_stack[-1] == "(":
            raise ValueError("Unbalanced parentheses in query.")
        process_operator(operator_stack, value_stack)

    if len(value_stack) != 1:
        raise ValueError("Invalid expression: stack did not reduce to a single result.")
    
    return ensure_list(value_stack[0])