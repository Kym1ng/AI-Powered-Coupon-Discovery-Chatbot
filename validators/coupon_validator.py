import json
from playwright.sync_api import sync_playwright

EXTRACTED_JSON = 'data/extracted_coupons.json'
SIMPLYCODES_URL = 'https://simplycodes.com/category/beauty/makeup'

def validate_first_coupon():
    with open(EXTRACTED_JSON, 'r') as f:
        coupons = json.load(f)
    if not coupons:
        print('No coupons found.')
        return
    coupon = coupons[0]
    button_index = coupon['button_index']
    print(f"Validating coupon: {coupon['brand']} | {coupon['code']} | {coupon['description']} (button_index={button_index})")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto(SIMPLYCODES_URL)
        page.wait_for_load_state('networkidle')
        coupon_blocks = page.query_selector_all("div[role='button']")
        if button_index >= len(coupon_blocks):
            print(f"button_index {button_index} out of range.")
            return
        coupon_block = coupon_blocks[button_index]
        copy_btn = coupon_block.query_selector('button:has-text("Copy code")')
        if not copy_btn:
            print('Copy code button not found.')
            return
        with context.expect_page() as popup_info:
            copy_btn.click()
        popup = popup_info.value
        popup.wait_for_load_state('domcontentloaded')
        shop_btn = popup.query_selector('footer.modal-footer a')
        real_url = shop_btn.get_attribute('href') if shop_btn else None
        print(f"Real shopping URL: {real_url}")
        popup.close()
        page.close()
        browser.close()

if __name__ == '__main__':
    validate_first_coupon() 