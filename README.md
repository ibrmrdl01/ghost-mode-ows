# Ghost Mode 👻

Ghost Mode is an AI-powered execution copilot for Web3 transactions.

Instead of blindly executing trades, Ghost Mode simulates transactions first, analyzes execution risks, and provides a clear AI-driven decision before execution.

## ✨ What it does

- Simulates token swaps before execution  
- Analyzes slippage, liquidity, and price impact  
- Explains risks in simple human language  
- Gives a clear verdict: GOOD / WARNING / BAD  
- Provides suggestions to improve execution  
- Prepares execution flow using OWS (mock integration)

## 🧠 Why this matters

Most users execute trades blindly.

Ghost Mode introduces a new paradigm:

simulate → explain → decide → execute

This improves:
- user safety  
- execution efficiency  
- decision clarity  

## 🔐 OWS Integration

Ghost Mode is designed to integrate with Open Wallet Standard (OWS):

- Private keys remain secure  
- AI never directly accesses wallets  
- Execution requests are routed safely  

Current version uses a mock execution layer, ready for real OWS policy integration.

## 🚀 Run locally

Install dependencies:

`bash
pip install -r requirements.txt

##start the server 

python -m uvicorn app:app --reload

##Open in browser 

http://127.0.0.1:8000/

⚠️ Notes
This is a demo / MVP
Execution is simulated
Built for the OpenWallet Hackathon

🛠 Future Work
Real OWS policy integration
Live DEX routing
Wallet connection
Multi-chain support

Built with ❤️ for @OpenWallet
