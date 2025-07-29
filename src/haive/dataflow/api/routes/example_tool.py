"""Example tool for testing the tools API."""

from pydantic import BaseModel, Field


class CalculatorInput(BaseModel):
    """Input schema for calculator tool."""

    expression: str = Field(..., description="Mathematical expression to evaluate")
    precision: int = Field(default=2, description="Number of decimal places")


class CalculatorTool:
    """Simple calculator tool for demonstrations."""

    name = "calculator"
    description = "Performs mathematical calculations"
    args_schema = CalculatorInput

    def run(self, expression: str, precision: int = 2) -> dict[str, any]:
        """Evaluate a mathematical expression.

        Args:
            expression: Mathematical expression to evaluate
            precision: Number of decimal places for the result

        Returns:
            Dictionary with the result and expression
        """
        try:
            # Safe evaluation of mathematical expressions
            result = eval(expression, {"__builtins__": {}}, {})
            return {
                "expression": expression,
                "result": round(result, precision),
                "success": True,
            }
        except Exception as e:
            return {"expression": expression, "error": str(e), "success": False}


class SearchToolInput(BaseModel):
    """Input schema for search tool."""

    query: str = Field(..., description="Search query")
    max_results: int = Field(default=10, description="Maximum number of results")


def simple_search(query: str, max_results: int = 10) -> list[str]:
    """Simple search function for testing.

    Args:
        query: Search query string
        max_results: Maximum number of results to return

    Returns:
        List of mock search results
    """
    # Mock search results
    results = []
    for i in range(min(max_results, 5)):
        results.append(f"Result {i+1} for '{query}'")
    return results
