
import asyncio
from playwright.async_api import async_playwright
import os

async def run():
    profile_path = os.path.expanduser("~/Documents/MusicBot_Workspace/chrome_profile")
    async with async_playwright() as p:
        # Note: This will fail if the user already has the browser open with this profile
        try:
            browser = await p.chromium.launch_persistent_context(
                user_data_dir=profile_path,
                headless=True
            )
            page = await browser.new_page()
            await page.goto("https://suno.com/create")
            await page.wait_for_timeout(10000) # Simple wait
            
            # Find the main layout containers
            layout_data = await page.evaluate('''() => {
                const results = {};
                
                const safeClass = (el) => el ? el.className : 'Not found';
                
                // Sidebar candidate
                const nav = document.querySelector('nav');
                results.sidebar_parent = safeClass(nav ? nav.parentElement : null);
                
                // Content area candidate
                const createBtn = document.querySelector('button[aria-label="Create"]');
                results.create_parent = safeClass(createBtn ? createBtn.closest('div') : null);
                
                // Workspace candidate
                const allDivs = Array.from(document.querySelectorAll('div, button, h2, span'));
                const wsText = allDivs.find(el => el.innerText?.includes('Workspaces'));
                results.workspace_parent = safeClass(wsText ? wsText.closest('div[class*="css-"]') : null);
                
                // Also check for common sidebars with data attributes
                const dataSidebar = document.querySelector('[data-collapsed]');
                results.data_sidebar_class = safeClass(dataSidebar ? dataSidebar.closest('div') : null);
                
                results.viewport = {w: window.innerWidth, h: window.innerHeight};
                results.scroll = {x: window.scrollX, y: window.scrollY, sw: document.documentElement.scrollWidth};
                return results;
            }''')
            print(f"DIAGNOSTIC_DATA: {layout_data}")
            await browser.close()
        except Exception as e:
            print(f"DIAGNOSTIC_ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(run())
