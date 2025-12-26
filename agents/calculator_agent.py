from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import math
import re
import statistics
import numpy as np
from typing import List, Dict, Any
from utils.models import model_manager
from config.settings import settings

app = FastAPI()

class CalculatorAgent:
    def __init__(self):
        self.name = "Calculator Agent"
        self.description = "Performs mathematical calculations, statistical analysis, and data extraction from text content"
    
    def extract_numbers_from_text(self, text: str) -> List[float]:
        """Extract all numbers from text content"""
        # Find numbers (including decimals, percentages, and currency)
        number_patterns = [
            r'\$?(\d+(?:,\d{3})*(?:\.\d+)?)\%?',  # Currency and percentages
            r'(\d+(?:\.\d+)?)\s*(?:percent|%)',    # Percentages with words
            r'(\d+(?:,\d{3})*(?:\.\d+)?)',         # Regular numbers with commas
        ]
        
        numbers = []
        for pattern in number_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0] if match[0] else match[1]
                # Remove commas and convert to float
                try:
                    clean_number = match.replace(',', '')
                    numbers.append(float(clean_number))
                except ValueError:
                    continue
        
        return list(set(numbers))  # Remove duplicates
    
    def calculate_statistics(self, numbers: List[float]) -> Dict[str, Any]:
        """Calculate comprehensive statistics for a list of numbers"""
        if not numbers:
            return {"error": "No numbers found for statistical analysis"}
        
        try:
            stats = {
                "count": len(numbers),
                "sum": sum(numbers),
                "mean": statistics.mean(numbers),
                "median": statistics.median(numbers),
                "min": min(numbers),
                "max": max(numbers),
                "range": max(numbers) - min(numbers),
            }
            
            if len(numbers) > 1:
                stats["std_dev"] = statistics.stdev(numbers)
                stats["variance"] = statistics.variance(numbers)
            
            # Calculate percentiles if numpy is available
            try:
                stats["q1"] = np.percentile(numbers, 25)
                stats["q3"] = np.percentile(numbers, 75)
                stats["iqr"] = stats["q3"] - stats["q1"]
            except:
                pass
                
            return stats
        except Exception as e:
            return {"error": f"Statistical calculation error: {str(e)}"}
    
    def analyze_trends(self, numbers: List[float]) -> Dict[str, Any]:
        """Analyze trends in numerical data"""
        if len(numbers) < 2:
            return {"error": "Need at least 2 data points for trend analysis"}
        
        try:
            # Calculate percentage changes
            changes = []
            for i in range(1, len(numbers)):
                if numbers[i-1] != 0:
                    change = ((numbers[i] - numbers[i-1]) / numbers[i-1]) * 100
                    changes.append(change)
            
            trend_analysis = {
                "total_change_percent": ((numbers[-1] - numbers[0]) / numbers[0]) * 100 if numbers[0] != 0 else 0,
                "average_change_percent": statistics.mean(changes) if changes else 0,
                "trend_direction": "increasing" if numbers[-1] > numbers[0] else "decreasing" if numbers[-1] < numbers[0] else "stable",
                "volatility": statistics.stdev(changes) if len(changes) > 1 else 0,
                "data_points": len(numbers)
            }
            
            return trend_analysis
        except Exception as e:
            return {"error": f"Trend analysis error: {str(e)}"}
    
    def intelligent_calculate(self, text: str) -> str:
        """Enhanced calculation that can handle various types of input"""
        # Check if it's a simple mathematical expression first
        simple_expr_patterns = [
            r'^[\d\+\-\*/\(\)\.\s%]+$',  # Simple math expression
            r'calculate\s+(.+)',          # "calculate X"
            r'what\s+is\s+(.+)',         # "what is X"
        ]
        
        for pattern in simple_expr_patterns:
            match = re.search(pattern, text.strip(), re.IGNORECASE)
            if match and (text.count('(') == text.count(')')) and len(text.split()) < 10:
                # Likely a simple expression
                try:
                    parsed = self.parse_math_expression(text)
                    result = eval(parsed, {"__builtins__": {}, "math": math})
                    return f"Calculation result: {result}"
                except:
                    pass  # Fall through to statistical analysis
        
        # Extract numbers for statistical analysis
        numbers = self.extract_numbers_from_text(text)
        
        if not numbers:
            # Use LLM to analyze the content and extract insights
            prompt = f"""You are a statistical analyst. Analyze the following content and extract any numerical insights, trends, or calculations that can be performed:

            Content: {text}

            Please provide:
            1. Any numerical data or statistics you can identify
            2. Key trends or patterns in the data
            3. Relevant calculations or metrics
            4. Statistical insights

            If there are specific numbers, provide calculations. If the content describes trends without exact numbers, provide qualitative analysis."""

            try:
                response = model_manager.azure_llm.invoke(prompt)
                content = response.content if hasattr(response, 'content') else str(response)
                return f"Statistical Analysis:\n{content}"
            except Exception as e:
                return f"Unable to perform numerical analysis on the provided content. Error: {str(e)}"
        
        # Perform statistical analysis on extracted numbers
        stats = self.calculate_statistics(numbers)
        trends = self.analyze_trends(numbers) if len(numbers) >= 2 else {}
        
        # Format comprehensive response
        response_parts = [f"Statistical Analysis of {len(numbers)} numerical values found:"]
        
        if "error" not in stats:
            response_parts.extend([
                f"\n📊 **Descriptive Statistics:**",
                f"• Count: {stats['count']}",
                f"• Sum: {stats['sum']:.2f}",
                f"• Mean: {stats['mean']:.2f}",
                f"• Median: {stats['median']:.2f}",
                f"• Range: {stats['min']:.2f} to {stats['max']:.2f}",
                f"• Standard Deviation: {stats.get('std_dev', 'N/A'):.2f}" if 'std_dev' in stats else ""
            ])
        
        if trends and "error" not in trends:
            response_parts.extend([
                f"\n📈 **Trend Analysis:**",
                f"• Overall Change: {trends['total_change_percent']:.2f}%",
                f"• Average Change: {trends['average_change_percent']:.2f}%",
                f"• Trend Direction: {trends['trend_direction'].title()}",
                f"• Volatility: {trends['volatility']:.2f}%"
            ])
        
        return "\n".join(filter(None, response_parts))
    
    def parse_math_expression(self, text: str) -> str:
        # Try to extract expression inside quotes if present
        import re
        match = re.search(r'"([^"]+)"|\'([^\']+)\'', text)
        if match:
            expr = match.group(1) or match.group(2)
        else:
            expr = text
        expr = expr.lower()
        # Replace 'percent' and 'number%' (as percentage) with '/100', but keep modulo %
        # Only replace % with /100 if followed by space, end, or non-digit (not another number or parenthesis)
        expr = re.sub(r'(\d+(?:\.\d+)?)\s*percent', r'(\1/100)', expr)
        expr = re.sub(r'(\d+(?:\.\d+)?)(%)((?![\d\(]))', r'(\1/100)', expr)
        expr = expr.replace('percent', '/100')
        expr = expr.replace('of', '*')
        # Insert * for implied multiplication: e.g. 2(3+4) -> 2*(3+4)
        expr = re.sub(r'(\d)\s*\(', r'\1*(', expr)
        expr = re.sub(r'\)(\d)', r')*\1', expr)
        # Remove non-math words/characters except modulo %
        expr = re.sub(r'[^0-9\.\+\-\*/%\(\) ]', '', expr)
        return expr.strip()

calculator_agent = CalculatorAgent()

@app.get("/.well-known/agent.json")
async def agent_card():
    return {
        "name": calculator_agent.name,
        "description": calculator_agent.description,
        "version": "1.0.0",
        "capabilities": ["mathematical_calculations", "statistical_analysis", "data_extraction", "trend_analysis", "expression_evaluation"],
        "endpoints": {"a2a": "/"}
    }

@app.post("/")
async def handle_a2a(request: Request):
    data = await request.json()
    method = data.get("method")
    params = data.get("params", {})
    
    if method == "sendTask":
        user_message = params.get("message", {}).get("parts", [{}])[0].get("text", "")
        result = calculator_agent.intelligent_calculate(user_message)
        
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": data.get("id"),
            "result": {
                "message": {
                    "role": "agent",
                    "parts": [{"type": "text", "text": result}]
                }
            }
        })
    
    return JSONResponse({"error": "Invalid method"}, status_code=400)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5106)