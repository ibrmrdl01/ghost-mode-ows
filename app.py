from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import random
import json
import os

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


app = FastAPI(title="Ghost Mode Simulator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OWS mock layer
OWS_API_KEY = os.getenv("OWS_API_KEY")


def execute_with_ows():
    if not OWS_API_KEY:
        return "OWS not configured"
    return "Execution request sent to OWS (simulated)"


SYSTEM_PROMPT = """
You are an AI trading copilot called "Ghost Mode".

Your job is to simulate a crypto transaction BEFORE execution and help the user make a better decision.

You DO NOT execute trades. You ONLY analyze, explain, and guide.

You must:
1. Analyze the trade using given data
2. Identify risks (slippage, liquidity, gas, volatility)
3. Explain the situation in simple human language
4. Give a clear verdict: GOOD / WARNING / BAD
5. Suggest a better alternative if needed

Be concise but insightful.
Avoid technical jargon unless necessary.
Think like a professional trader explaining to a beginner.

Always structure your response in JSON format.

Fields:
- summary
- verdict
- risks
- suggestions
- explanation

Never leave fields empty.
""".strip()


class TradeRequest(BaseModel):
    chain: str
    from_token: str
    to_token: str
    amount: float


def simulate_trade(chain: str, from_token: str, to_token: str, amount: float) -> dict:
    liquidity_level = random.choice(["LOW", "MEDIUM", "HIGH"])

    if liquidity_level == "LOW":
        slippage = round(random.uniform(6.0, 15.0), 2)
        price_impact = round(random.uniform(4.0, 14.0), 2)
    elif liquidity_level == "MEDIUM":
        slippage = round(random.uniform(2.0, 6.0), 2)
        price_impact = round(random.uniform(1.5, 5.0), 2)
    else:
        slippage = round(random.uniform(0.1, 2.0), 2)
        price_impact = round(random.uniform(0.1, 1.5), 2)

    gas_fee = round(random.uniform(0.20, 4.50), 2)
    token_price_factor = random.uniform(0.7, 1.3)
    expected_output = round((amount * token_price_factor) * (1 - slippage / 100), 4)

    return {
        "chain": chain,
        "from_token": from_token,
        "to_token": to_token,
        "amount": amount,
        "expected_output": expected_output,
        "price_impact": price_impact,
        "slippage": slippage,
        "gas_fee": f"${gas_fee}",
        "liquidity_level": liquidity_level,
    }


def build_user_prompt(sim: dict) -> str:
    return f"""
Analyze this simulated trade:

Chain: {sim['chain']}
From Token: {sim['from_token']}
To Token: {sim['to_token']}
Amount: {sim['amount']}

Simulation Results:
- Expected Output: {sim['expected_output']} {sim['to_token']}
- Price Impact: {sim['price_impact']}%
- Slippage: {sim['slippage']}%
- Estimated Gas Fee: {sim['gas_fee']}
- Liquidity Level: {sim['liquidity_level']}

Give your analysis.
""".strip()


def fallback_analysis(sim: dict) -> dict:
    risks = []
    suggestions = []
    score = 0

    if sim["slippage"] > 5:
        risks.append(f"High slippage ({sim['slippage']}%)")
        suggestions.append("Consider splitting the trade into smaller parts")
        score += 35

    if sim["price_impact"] > 3:
        risks.append(f"High price impact ({sim['price_impact']}%)")
        suggestions.append("Use a more liquid pair or reduce trade size")
        score += 30

    if sim["liquidity_level"] == "LOW":
        risks.append("Low liquidity pool")
        suggestions.append("Wait for better liquidity before trading")
        score += 25

    gas_value = float(sim["gas_fee"].replace("$", ""))
    if gas_value > 3:
        risks.append(f"Gas cost is relatively high ({sim['gas_fee']})")
        suggestions.append("Try executing later when network fees are lower")
        score += 10

    if score >= 60:
        verdict = "BAD"
        summary = "This trade looks inefficient and risky."
        explanation = (
            "The simulated trade shows poor execution quality. "
            "Low liquidity, high slippage, or large price impact may cause you to receive much less value than expected."
        )
    elif score >= 30:
        verdict = "WARNING"
        summary = "This trade is possible, but conditions are not ideal."
        explanation = (
            "The trade may still go through, but current route conditions suggest avoidable inefficiencies. "
            "A smaller size or better timing may improve the result."
        )
    else:
        verdict = "GOOD"
        summary = "This trade looks relatively healthy."
        explanation = (
            "The route appears reasonably efficient based on the simulated data. "
            "Slippage and price impact are within a tolerable range."
        )

    if not risks:
        risks = ["No major execution risk detected in the simulation"]
    if not suggestions:
        suggestions = ["Proceed if this matches your intended strategy"]

    return {
        "summary": summary,
        "verdict": verdict,
        "risks": risks,
        "suggestions": suggestions,
        "explanation": explanation,
    }


def ai_analysis(sim: dict) -> dict:
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key or OpenAI is None:
        return fallback_analysis(sim)

    try:
        client = OpenAI(api_key=api_key)
        user_prompt = build_user_prompt(sim)

        response = client.responses.create(
            model="gpt-5",
            input=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
        )

        raw_text = response.output_text.strip()

        if raw_text.startswith("```"):
            raw_text = raw_text.strip("`")
            raw_text = raw_text.replace("json", "", 1).strip()

        parsed = json.loads(raw_text)

        return {
            "summary": parsed.get("summary", "No summary provided."),
            "verdict": parsed.get("verdict", "WARNING"),
            "risks": parsed.get("risks", ["No risks returned."]),
            "suggestions": parsed.get("suggestions", ["No suggestions returned."]),
            "explanation": parsed.get("explanation", "No explanation provided."),
        }

    except Exception as exc:
        local = fallback_analysis(sim)
        local["summary"] += f" (Fallback mode: {str(exc)})"
        return local


@app.get("/", response_class=HTMLResponse)
def serve_index():
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return """
        <h1>index.html not found</h1>
        <p>Place index.html in the same directory as app.py</p>
        """


@app.post("/analyze")
def analyze_trade(payload: TradeRequest):
    sim = simulate_trade(
        chain=payload.chain,
        from_token=payload.from_token,
        to_token=payload.to_token,
        amount=payload.amount,
    )
    analysis = ai_analysis(sim)

    return JSONResponse({
        "simulation": sim,
        "analysis": analysis
    })


@app.post("/execute")
def execute_trade():
    result = execute_with_ows()

    return JSONResponse({
        "status": "success",
        "message": result
    })