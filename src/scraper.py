import asyncio
from playwright.async_api import Browser
from playwright_stealth import Stealth

async def get_page_html(browser: Browser, url: str):
    # Tạo một ngữ cảnh trình duyệt riêng biệt (giống tab ẩn danh)
    context = await browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        viewport={'width': 1280, 'height': 720}
    )
    page = await context.new_page()

    # Kích hoạt chế độ tàng hình để tránh Cloudflare phát hiện bot
    await Stealth().apply_stealth_async(page)

    try:
        # Truy cập URL và đợi cho đến khi các script cơ bản tải xong
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)

        # Giả lập hành vi người dùng: Cuộn trang từ từ
        # Wattpad cần cuộn xuống để kích hoạt nạp nội dung thực sự (Lazy Load)
        for i in range(3):
            await page.mouse.wheel(0, 1000)
            await asyncio.sleep(1.5) # Nghỉ một chút để giả lập người thật đang đọc

        html = await page.content()
        title = await page.title()

        return {"html": html, "title": title}
    except Exception as e:
        raise e
    finally:
        await context.close()
