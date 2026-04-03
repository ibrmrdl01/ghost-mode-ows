# Ghost Mode 👻

Ghost Mode is an AI-powered execution copilot for Web3 transactions.

It simulates trades before execution, analyzes execution risks such as slippage, liquidity, and price impact, and provides a simple AI verdict before the user proceeds.

## Features

- Trade simulation
- AI-based risk explanation
- GOOD / WARNING / BAD verdict
- Mock execution flow
- OWS-ready execution architecture

## Run locally

Install dependencies:

```bash
pip install -r requirements.txt

Start the server:

```bash
python -m uvicorn app:app --reload

OPEN BROWSER
http://127.0.0.1:8000
