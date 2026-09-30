"""Standalone Web App and Interactive Delivery UI for Fresh Chicken & Mutton Delivery."""
from dotenv import load_dotenv
load_dotenv()


import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict
import uvicorn

from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai import types

from app.agent import app as adk_app, root_agent
from app.meat_catalog import CATALOG, ORDERS
from app.meat_tools import (
    list_fresh_cuts,
    recommend_cut_for_dish,
    check_delivery_slots,
    place_meat_order,
    track_order_status,
)

session_service = InMemorySessionService()
runner = Runner(
    app=adk_app,
    session_service=session_service,
    auto_create_session=True,
)

web = FastAPI(title="PrimeCuts - Fresh Chicken & Mutton Delivery")

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "web-default-session"

class OrderRequest(BaseModel):
    item_id: str
    quantity: int
    customer_name: str
    customer_phone: str
    delivery_address: str
    delivery_slot: str = "Express (45 mins)"

@web.get("/api/catalog")
def get_catalog():
    return list(CATALOG.values())

@web.get("/api/orders")
def get_orders():
    return list(ORDERS.values())

@web.post("/api/order")
def create_order(req: OrderRequest):
    result = place_meat_order(
        item_id=req.item_id,
        quantity=req.quantity,
        delivery_address=req.delivery_address,
        customer_name=req.customer_name,
        customer_phone=req.customer_phone,
        delivery_slot=req.delivery_slot,
    )
    return {"message": result}

@web.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    try:
        user_msg = types.Content(
            role="user",
            parts=[types.Part.from_text(text=req.message)]
        )
        response_text = ""
        async for event in runner.run_async(
            user_id="web-user",
            session_id=req.session_id,
            new_message=user_msg,
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if hasattr(part, "text") and part.text:
                        response_text += part.text

        return {"reply": response_text or "Processed request."}
    except Exception as e:
        return {"reply": f"Error: {str(e)}"}

HTML_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>🥩 PrimeCuts - Fresh Chicken & Mutton Delivery</title>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap">
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Plus Jakarta Sans', sans-serif; }
    body { background: #0f172a; color: #f8fafc; display: flex; height: 100vh; overflow: hidden; }
    
    /* Left: Catalog & Store View */
    .catalog-panel { flex: 1.1; border-right: 1px solid #1e293b; display: flex; flex-direction: column; overflow-y: auto; background: #0b1120; }
    .header { padding: 20px 24px; background: #111827; border-bottom: 1px solid #1e293b; display: flex; justify-content: space-between; align-items: center; }
    .brand { display: flex; align-items: center; gap: 12px; }
    .brand-icon { font-size: 28px; background: #b91c1c; padding: 8px 12px; border-radius: 12px; box-shadow: 0 4px 12px rgba(185, 28, 28, 0.4); }
    .brand-title { font-size: 20px; font-weight: 800; color: #fff; }
    .brand-subtitle { font-size: 12px; color: #94a3b8; }
    .badge { background: #166534; color: #bbf7d0; font-size: 11px; font-weight: 700; padding: 4px 10px; border-radius: 999px; text-transform: uppercase; }
    
    .filters { display: flex; gap: 8px; padding: 16px 24px; border-bottom: 1px solid #1e293b; background: #0f172a; }
    .filter-btn { background: #1e293b; border: 1px solid #334155; color: #cbd5e1; padding: 8px 16px; border-radius: 8px; font-size: 13px; font-weight: 600; cursor: pointer; transition: 0.2s; }
    .filter-btn.active, .filter-btn:hover { background: #dc2626; border-color: #ef4444; color: white; }
    
    .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 16px; padding: 20px 24px; }
    .card { background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 16px; display: flex; flex-direction: column; justify-content: space-between; transition: transform 0.15s, border-color 0.15s; }
    .card:hover { transform: translateY(-2px); border-color: #e11d48; }
    .card-category { font-size: 11px; text-transform: uppercase; font-weight: 700; color: #f87171; margin-bottom: 4px; }
    .card-title { font-size: 15px; font-weight: 700; color: #fff; margin-bottom: 6px; }
    .card-desc { font-size: 12px; color: #94a3b8; margin-bottom: 12px; line-height: 1.4; flex-grow: 1; }
    .card-meta { font-size: 11px; color: #38bdf8; background: #0c4a6e; padding: 4px 8px; border-radius: 6px; margin-bottom: 12px; }
    .card-footer { display: flex; justify-content: space-between; align-items: center; border-top: 1px solid #334155; padding-top: 10px; }
    .card-price { font-size: 17px; font-weight: 800; color: #22c55e; }
    .order-btn { background: #dc2626; color: white; border: none; padding: 6px 14px; border-radius: 6px; font-weight: 600; font-size: 12px; cursor: pointer; }
    .order-btn:hover { background: #b91c1c; }

    /* Right: AI Agent Chat & Order Tracker */
    .chat-panel { flex: 0.9; display: flex; flex-direction: column; background: #090d16; }
    .chat-header { padding: 18px 20px; background: #111827; border-bottom: 1px solid #1e293b; display: flex; justify-content: space-between; align-items: center; }
    .chat-title { font-size: 16px; font-weight: 700; display: flex; align-items: center; gap: 8px; }
    .status-dot { width: 8px; height: 8px; border-radius: 50%; background: #22c55e; box-shadow: 0 0 8px #22c55e; }
    
    .chat-messages { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 14px; }
    .msg { max-width: 85%; padding: 12px 16px; border-radius: 12px; font-size: 13.5px; line-height: 1.5; white-space: pre-wrap; }
    .msg-user { align-self: flex-end; background: #dc2626; color: white; border-bottom-right-radius: 2px; }
    .msg-bot { align-self: flex-start; background: #1e293b; color: #f1f5f9; border-bottom-left-radius: 2px; border: 1px solid #334155; }
    
    .quick-prompts { display: flex; gap: 6px; padding: 8px 16px; overflow-x: auto; background: #0f172a; border-top: 1px solid #1e293b; }
    .quick-chip { background: #1e293b; border: 1px solid #334155; color: #94a3b8; font-size: 11px; padding: 5px 10px; border-radius: 16px; white-space: nowrap; cursor: pointer; }
    .quick-chip:hover { color: #f8fafc; border-color: #64748b; }
    
    .chat-input-area { padding: 16px; background: #111827; border-top: 1px solid #1e293b; display: flex; gap: 10px; }
    .chat-input { flex: 1; background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 12px 14px; color: #fff; font-size: 13.5px; outline: none; }
    .chat-input:focus { border-color: #ef4444; }
    .send-btn { background: #dc2626; border: none; color: white; padding: 0 18px; border-radius: 8px; font-weight: 700; cursor: pointer; transition: 0.2s; }
    .send-btn:hover { background: #b91c1c; }
    
    /* Order Modal */
    .modal-backdrop { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.7); backdrop-filter: blur(4px); align-items: center; justify-content: center; z-index: 100; }
    .modal { background: #1e293b; border: 1px solid #475569; width: 420px; border-radius: 16px; padding: 24px; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.5); }
    .modal-title { font-size: 18px; font-weight: 700; margin-bottom: 16px; }
    .form-group { margin-bottom: 12px; }
    .form-group label { display: block; font-size: 12px; color: #94a3b8; margin-bottom: 4px; font-weight: 600; }
    .form-group input, .form-group select { width: 100%; padding: 10px; background: #0f172a; border: 1px solid #334155; border-radius: 8px; color: #fff; font-size: 13px; }
    .modal-actions { display: flex; justify-content: flex-end; gap: 8px; margin-top: 18px; }
    .cancel-btn { background: #334155; color: white; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; font-size: 13px; }
    .confirm-btn { background: #dc2626; color: white; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; font-weight: 700; font-size: 13px; }
  </style>
</head>
<body>

  <!-- Catalog View -->
  <div class="catalog-panel">
    <div class="header">
      <div class="brand">
        <div class="brand-icon">🥩</div>
        <div>
          <div class="brand-title">PrimeCuts Express</div>
          <div class="brand-subtitle">Fresh Chicken & Mutton • Cold-Chamber Delivered (0-4°C)</div>
        </div>
      </div>
      <span class="badge">● Express 45 Min</span>
    </div>

    <div class="filters">
      <button class="filter-btn active" onclick="filterCuts('all', this)">All Meats</button>
      <button class="filter-btn" onclick="filterCuts('chicken', this)">🍗 Fresh Chicken</button>
      <button class="filter-btn" onclick="filterCuts('mutton', this)">🍖 Fresh Goat Mutton</button>
    </div>

    <div class="grid" id="catalogGrid">
      <!-- Items loaded dynamically -->
    </div>
  </div>

  <!-- AI Delivery Concierge -->
  <div class="chat-panel">
    <div class="chat-header">
      <div class="chat-title">
        <span class="status-dot"></span>
        PrimeCuts AI Concierge (ADK Agent)
      </div>
      <span style="font-size: 12px; color: #94a3b8;">Gemini 2.5 Flash</span>
    </div>

    <div class="chat-messages" id="chatMessages">
      <div class="msg msg-bot">👋 Hello! I am your <b>PrimeCuts Concierge</b>.

Looking for fresh chicken or goat mutton today?
• Ask me for dish recommendations (e.g. <i>"What cut is best for Dum Biryani?"</i>)
• Ask about cold-chain freshness & express delivery slots
• Or tell me what you'd like to order, and I'll book it right away!</div>
    </div>

    <div class="quick-prompts">
      <div class="quick-chip" onclick="sendPrompt('What cut is best for Dum Biryani?')">🥘 Best cut for Biryani?</div>
      <div class="quick-chip" onclick="sendPrompt('Do you have fresh goat keema in stock?')">🥩 Fresh Mutton Keema?</div>
      <div class="quick-chip" onclick="sendPrompt('Check delivery slots for Indiranagar')">🚚 Delivery times?</div>
      <div class="quick-chip" onclick="sendPrompt('Tell me about your chicken cuts and prices')">🍗 Chicken cuts list</div>
    </div>

    <div class="chat-input-area">
      <input type="text" id="userInput" class="chat-input" placeholder="Ask for recommendations or order meat..." onkeydown="if(event.key==='Enter') sendMessage()" />
      <button class="send-btn" onclick="sendMessage()">Send</button>
    </div>
  </div>

  <!-- Order Modal -->
  <div class="modal-backdrop" id="orderModal">
    <div class="modal">
      <div class="modal-title" id="modalCutTitle">Express Meat Order</div>
      <input type="hidden" id="modalItemId">
      
      <div class="form-group">
        <label>Quantity (Packs)</label>
        <input type="number" id="orderQty" min="1" max="10" value="1">
      </div>
      <div class="form-group">
        <label>Your Name</label>
        <input type="text" id="custName" placeholder="e.g. Alex Johnson">
      </div>
      <div class="form-group">
        <label>Phone Number</label>
        <input type="text" id="custPhone" placeholder="e.g. 9876543210">
      </div>
      <div class="form-group">
        <label>Delivery Address</label>
        <input type="text" id="custAddress" placeholder="Street, Apartment, Area">
      </div>
      <div class="form-group">
        <label>Delivery Slot</label>
        <select id="custSlot">
          <option>Express (45 mins)</option>
          <option>Evening (06:00 PM - 08:00 PM)</option>
          <option>Tomorrow Morning (07:00 AM - 09:00 AM)</option>
        </select>
      </div>

      <div class="modal-actions">
        <button class="cancel-btn" onclick="closeOrderModal()">Cancel</button>
        <button class="confirm-btn" onclick="submitModalOrder()">Confirm & Place Order</button>
      </div>
    </div>
  </div>

  <script>
    let allProducts = [];

    async function loadCatalog() {
      try {
        const res = await fetch('/api/catalog');
        allProducts = await res.json();
        renderCatalog(allProducts);
      } catch (e) {
        console.error(e);
      }
    }

    function renderCatalog(items) {
      const grid = document.getElementById('catalogGrid');
      grid.innerHTML = items.map(p => `
        <div class="card">
          <div>
            <div class="card-category">${p.category === 'chicken' ? '🍗 Chicken' : '🍖 Mutton'} • ${p.id}</div>
            <div class="card-title">${p.name}</div>
            <div class="card-desc">${p.description}</div>
            <div class="card-meta">👨‍🍳 Best for: ${p.best_for}</div>
          </div>
          <div class="card-footer">
            <div class="card-price">₹${p.price.toFixed(0)} <span style="font-size:12px;color:#94a3b8;font-weight:normal;">/ ${p.weight}</span></div>
            <button class="order-btn" onclick="openOrderModal('${p.id}', '${p.name}')">Order Now</button>
          </div>
        </div>
      `).join('');
    }

    function filterCuts(cat, btn) {
      document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      if (cat === 'all') {
        renderCatalog(allProducts);
      } else {
        renderCatalog(allProducts.filter(p => p.category === cat));
      }
    }

    function openOrderModal(id, name) {
      document.getElementById('modalItemId').value = id;
      document.getElementById('modalCutTitle').innerText = 'Order ' + name;
      document.getElementById('orderModal').style.display = 'flex';
    }

    function closeOrderModal() {
      document.getElementById('orderModal').style.display = 'none';
    }

    async function submitModalOrder() {
      const payload = {
        item_id: document.getElementById('modalItemId').value,
        quantity: parseInt(document.getElementById('orderQty').value) || 1,
        customer_name: document.getElementById('custName').value || 'Guest Customer',
        customer_phone: document.getElementById('custPhone').value || '9999999999',
        delivery_address: document.getElementById('custAddress').value || 'Downtown Express',
        delivery_slot: document.getElementById('custSlot').value
      };

      const res = await fetch('/api/order', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      closeOrderModal();
      appendMessage('user', `Placed order for ${payload.item_id} (${payload.quantity} pack) to ${payload.delivery_address}`);
      appendMessage('bot', data.message);
    }

    function appendMessage(role, text) {
      const container = document.getElementById('chatMessages');
      const div = document.createElement('div');
      div.className = 'msg ' + (role === 'user' ? 'msg-user' : 'msg-bot');
      div.innerText = text;
      container.appendChild(div);
      container.scrollTop = container.scrollHeight;
    }

    async function sendMessage() {
      const input = document.getElementById('userInput');
      const text = input.value.trim();
      if (!text) return;
      input.value = '';

      appendMessage('user', text);
      const botPlaceholder = document.createElement('div');
      botPlaceholder.className = 'msg msg-bot';
      botPlaceholder.innerText = 'Thinking...';
      document.getElementById('chatMessages').appendChild(botPlaceholder);
      document.getElementById('chatMessages').scrollTop = document.getElementById('chatMessages').scrollHeight;

      try {
        const res = await fetch('/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: text })
        });
        const data = await res.json();
        botPlaceholder.innerText = data.reply;
      } catch (e) {
        botPlaceholder.innerText = 'Error connecting to agent: ' + e;
      }
    }

    function sendPrompt(text) {
      document.getElementById('userInput').value = text;
      sendMessage();
    }

    loadCatalog();
  </script>
</body>
</html>
"""

@web.get("/", response_class=HTMLResponse)
def index():
    return HTMLResponse(content=HTML_CONTENT)

if __name__ == "__main__":
    uvicorn.run(web, host="0.0.0.0", port=8000)
