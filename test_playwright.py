from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()

    b64_script = """
    (url) => fetch(url).then(res => res.blob()).then(blob => new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onloadend = () => resolve(reader.result.split(',')[1]);
        reader.onerror = reject;
        reader.readAsDataURL(blob);
    }))
    """
    try:
        # we can't easily fetch an external file that returns CORS properly if it's not set up, but let's try a small data URI or anything
        # We can mock route
        page.route("https://example.com/test.txt", lambda route: route.fulfill(body="hello world", content_type="text/plain"))
        res = page.evaluate(b64_script, "https://example.com/test.txt")
        print("B64 Result:", res)
    except Exception as e:
        print("Error:", e)

    browser.close()
