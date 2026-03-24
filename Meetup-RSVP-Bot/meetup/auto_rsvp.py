import asyncio
import json
import logging
import argparse
from pathlib import Path
from time import sleep
from playwright.async_api import async_playwright

# Ensure local package imports work both as script and with python -m
import sys
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from meetup.events import get_events
except ModuleNotFoundError:
    from events import get_events

PROFILE_PATH = "./chrome_profile"

DEFAULT_CONFIG = {
    "groups": [
        "https://www.meetup.com/dungeons-and-dragons-campaigns/",
        "https://www.meetup.com/mumbai-ai-machine-learning-and-computer-vision-meetup/",
        "https://www.meetup.com/dubai-build-your-real-estate-team-meetup-group/",
        "https://www.meetup.com/https-chat-whatsapp-com-fpwhevld3kr3998n2swncw/",
        "https://www.meetup.com/gdg-cloud-hong-kong/"
    ],
    "max_events_per_group": 4,
    "headless": True,
    "pause_between_events_sec": 2,
    "pause_between_groups_sec": 2,
    "rsvp_button_text": ["RSVP", "Attend", "Yes", "Register"],
    "log_level": "INFO"
}


def load_config(path: Path) -> dict:
    if not path.exists():
        path.write_text(json.dumps(DEFAULT_CONFIG, indent=2))
        logging.warning("Default config created at %s. Please edit it with your group URLs.", path)
        return DEFAULT_CONFIG.copy()

    data = json.loads(path.read_text())
    for field in ["groups", "max_events_per_group"]:
        if field not in data:
            raise ValueError(f"Missing required configuration field: {field}")
    return data


async def rsvp_event(page, event_url, button_texts):
    await page.goto(event_url)
    await page.wait_for_timeout(3500)

    for text in button_texts:
        btn_selector = f"button:has-text(\"{text}\")"

        button = await page.query_selector(btn_selector)
        if button is None:
            continue

        if await button.is_disabled():
            continue

        ground_text = (await button.inner_text()).strip().lower()
        if "already" in ground_text or "pending" in ground_text:
            logging.info("Already RSVP/registered on %s (%s)", event_url, ground_text)
            return False

        logging.info("Clicking RSVP button '%s' for %s", text, event_url)
        # Wait for any blocking overlay to disappear
        try:
            await page.wait_for_selector("div[data-state='open']", state="hidden", timeout=5000)
        except:
            pass

        # Try closing modal if exists
        try:
            await page.click("button[aria-label='Close']", timeout=2000)
        except:
            pass
        # If login button exists → you are NOT logged in
        login_btn = await page.query_selector("a[href*='login']")
        if login_btn:
            logging.error("NOT LOGGED IN — session expired")
            return False
        await button.click()
        sleep(1)

        # Wait for modal to appear
        await page.wait_for_timeout(2000)

        # Try clicking Submit (for registration popup)
        submit_btn = await page.query_selector("button:has-text('Submit')")
        if submit_btn and not await submit_btn.is_disabled():
            logging.info("Clicking Submit button")
            await submit_btn.click()
            await page.wait_for_timeout(2000)
            return True

        # Fallback: other confirmation buttons
        confirm = await page.query_selector(
            "button:has-text('Yes'), button:has-text('RSVP'), button:has-text('Attend')"
        )
        if confirm and not await confirm.is_disabled():
            logging.info("Clicking confirmation button")
            await confirm.click()
            await page.wait_for_timeout(2000)
            return True

        await page.wait_for_timeout(2000)
        logging.info("RSVP attempt made for %s", event_url)
        return True

    logging.info("No RSVP-able button found for %s", event_url)
    return False


async def run_auto_rsvp(config):
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            PROFILE_PATH,
            channel="chrome",
            headless=False,
            slow_mo=500
        )
        page = await context.new_page()

        for group_url in config["groups"]:
            group_url = group_url.rstrip("/") + "/"
            logging.info("Scanning group: %s", group_url)

            try:
                event_urls = await get_events(
                    page,
                    group_url,
                    max_events=config.get("max_events_per_group", 4),
                )
            except Exception as e:
                logging.error("Failed to scrape events for %s: %s", group_url, e)
                continue

            logging.info("Found %d events in %s", len(event_urls), group_url)

            for event_url in event_urls[: config.get("max_events_per_group", 4)]:
                if not event_url.startswith("http"):
                    event_url = "https://www.meetup.com" + event_url

                try:
                    await rsvp_event(page, event_url, config.get("rsvp_button_text", DEFAULT_CONFIG["rsvp_button_text"]))
                except Exception as e:
                    logging.error("Error RSVPing %s: %s", event_url, e)

                sleep(config.get("pause_between_events_sec", 2))

            sleep(config.get("pause_between_groups_sec", 2))

        await context.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Meetup auto RSVP runner")
    parser.add_argument("--config", default="meetup_rsvp_config.json", help="Path to config JSON")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    cfg_path = Path(args.config)
    cfg = load_config(cfg_path)

    asyncio.run(run_auto_rsvp(cfg))
