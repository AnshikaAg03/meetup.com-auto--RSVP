from playwright.sync_api import sync_playwright

PROFILE_PATH = "./chrome_profile"

def login():

    with sync_playwright() as p:

        context = p.chromium.launch_persistent_context(
            PROFILE_PATH,
            channel="chrome",
            headless=False
        )

        page = context.new_page()

        page.goto("https://www.meetup.com/login")

        print("Login manually in the browser.")
        print("Session will be saved automatically.")

        page.wait_for_timeout(1200000)

        context.close()


if __name__ == "__main__":
    login()