import asyncio
import os
import glob
from playwright.async_api import async_playwright

async def main():
    video_dir = "/config/Desktop/BuildWithGemini/raw_video"
    os.makedirs(video_dir, exist_ok=True)
    for old_f in glob.glob(os.path.join(video_dir, "*")):
        try:
            os.remove(old_f)
        except Exception:
            pass
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--window-size=1280,720",
            ]
        )
        context = await browser.new_context(
            viewport={"width": 1280, "height": 720},
            record_video_dir=video_dir,
            record_video_size={"width": 1280, "height": 720}
        )
        page = await context.new_page()
        
        print("1. Loading PrimeCuts Concierge...")
        await page.goto("http://localhost:8080")
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(2)
        
        # --- SCENE 1: Click first prompt pill (Live catalog lookup & A2UI cards) ---
        print("2. Clicking 'Show Available Cuts' prompt pill...")
        first_pill = page.locator(".suggestion-pill").first
        await first_pill.click()
        
        print("3. Waiting for Agent to return live meat catalog...")
        # Poll until the second agent message bubble exists and does NOT contain "…"
        for _ in range(60):
            agent_msgs = await page.locator(".msg-row.agent .bubble").all_text_contents()
            if len(agent_msgs) >= 2 and agent_msgs[-1].strip() != "…":
                print("First response received!")
                break
            await asyncio.sleep(1)
            
        await asyncio.sleep(3)
        print("4. Scrolling to admire catalog cards...")
        await page.evaluate("window.scrollBy({top: 400, behavior: 'smooth'})")
        await asyncio.sleep(3)
        
        # --- SCENE 2: Richer prompt with portioning, cut pairing, and recipe inquiry ---
        richer_prompt = "I want to cook Dum Biryani for 6 people. Which cut should I choose and how much do I need?"
        print("5. Typing Prompt 2:", richer_prompt)
        input_box = page.locator("#input")
        await input_box.click()
        
        for char in richer_prompt:
            await input_box.type(char, delay=28)
            
        await asyncio.sleep(1)
        send_btn = page.locator("#send-btn")
        await send_btn.click()
        
        print("6. Waiting for Agent response to Prompt 2 (recommendations & portion calculations)...")
        for _ in range(60):
            agent_msgs = await page.locator(".msg-row.agent .bubble").all_text_contents()
            if len(agent_msgs) >= 3 and agent_msgs[-1].strip() != "…":
                print("Second response received!")
                break
            await asyncio.sleep(1)
            
        await asyncio.sleep(3)
        print("7. Scrolling to inspect rich portioning recommendation...")
        await page.evaluate("window.scrollBy({top: 600, behavior: 'smooth'})")
        await asyncio.sleep(3)
        await page.evaluate("window.scrollBy({top: 400, behavior: 'smooth'})")
        await asyncio.sleep(3)
        
        print("8. Finalizing video recording...")
        await context.close()
        await browser.close()
        print("Recording completed successfully!")

if __name__ == "__main__":
    asyncio.run(main())
