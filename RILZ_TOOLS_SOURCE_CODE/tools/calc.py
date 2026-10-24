import ast
import math
import operator
from typing import Any
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

# Allowed operators
OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

# Allowed functions & constants
MATH_FUNCTIONS = {
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "asin": math.asin,
    "acos": math.acos,
    "atan": math.atan,
    "sqrt": math.sqrt,
    "cbrt": math.cbrt if hasattr(math, "cbrt") else lambda x: x ** (1 / 3),
    "log": math.log,
    "ln": math.log,
    "log10": math.log10,
    "log2": math.log2,
    "exp": math.exp,
    "abs": abs,
    "round": round,
    "floor": math.floor,
    "ceil": math.ceil,
    "factorial": math.factorial,
    "deg": math.degrees,
    "rad": math.radians,
}

MATH_CONSTANTS = {
    "pi": math.pi,
    "e": math.e,
    "tau": math.tau,
}


class SafeMathEvaluator(ast.NodeVisitor):
    """Safely evaluate arithmetic and scientific expressions using Python AST."""

    def visit(self, node: ast.AST) -> Any:
        method = "visit_" + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node: ast.AST):
        raise ValueError(f"Ekspresi atau simbol tidak didukung: {node.__class__.__name__}")

    def visit_Expression(self, node: ast.Expression):
        return self.visit(node.body)

    def visit_Constant(self, node: ast.Constant):
        if isinstance(node.value, (int, float, complex)):
            return node.value
        raise ValueError(f"Konstanta tidak valid: {node.value}")

    def visit_BinOp(self, node: ast.BinOp):
        op_type = type(node.op)
        if op_type in OPERATORS:
            left = self.visit(node.left)
            right = self.visit(node.right)
            return OPERATORS[op_type](left, right)
        raise ValueError(f"Operator tidak didukung: {op_type.__name__}")

    def visit_UnaryOp(self, node: ast.UnaryOp):
        op_type = type(node.op)
        if op_type in OPERATORS:
            operand = self.visit(node.operand)
            return OPERATORS[op_type](operand)
        raise ValueError(f"Operator unary tidak didukung: {op_type.__name__}")

    def visit_Name(self, node: ast.Name):
        name = node.id.lower()
        if name in MATH_CONSTANTS:
            return MATH_CONSTANTS[name]
        raise ValueError(f"Variabel atau konstanta tidak dikenal: '{node.id}'")

    def visit_Call(self, node: ast.Call):
        if not isinstance(node.func, ast.Name):
            raise ValueError("Panggilan fungsi tidak valid.")
        func_name = node.func.id.lower()
        if func_name in MATH_FUNCTIONS:
            args = [self.visit(arg) for arg in node.args]
            return MATH_FUNCTIONS[func_name](*args)
        raise ValueError(f"Fungsi tidak didukung: '{node.func.id}'")


def evaluate_expression(expr: str) -> str:
    """Evaluate a mathematical expression string safely."""
    clean_expr = expr.replace("^", "**")
    try:
        tree = ast.parse(clean_expr, mode="eval")
        evaluator = SafeMathEvaluator()
        result = evaluator.visit(tree)
        # Format float nicely
        if isinstance(result, float) and result.is_integer():
            return str(int(result))
        return f"{result:.8g}"
    except Exception as e:
        return f"Error: {e}"


def interactive_calculator():
    """Run an interactive calculator session in terminal."""
    console.print(
        Panel(
            "[bold white]Kalkulator Terminal Ilmiah[/bold white]\n"
            "[dim]Mendukung operator (+, -, *, /, //, %, ^) & fungsi: sin, cos, tan, sqrt, log, abs, factorial, pi, e.\n"
            "Ketik [bold cyan]'exit'[/bold cyan] atau [bold cyan]'q'[/bold cyan] untuk kembali ke menu.[/dim]",
            title="🧮 Terminal Calculator",
            border_style="bright_blue",
        )
    )

    history = []

    while True:
        try:
            expr = console.input("[bold cyan]calc>[/bold cyan] ").strip()
            if not expr:
                continue
            if expr.lower() in ("exit", "quit", "q"):
                break
            if expr.lower() == "history":
                table = Table(title="Riwayat Perhitungan")
                table.add_column("No", style="dim", width=4)
                table.add_column("Ekspresi", style="yellow")
                table.add_column("Hasil", style="bold green")
                for i, (q, a) in enumerate(history, 1):
                    table.add_row(str(i), q, str(a))
                console.print(table)
                continue

            result = evaluate_expression(expr)
            if not result.startswith("Error:"):
                history.append((expr, result))
                console.print(f"[bold green]= {result}[/bold green]\n")
            else:
                console.print(f"[bold red]{result}[/bold red]\n")

        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Keluar dari kalkulator.[/dim]")
            break
