from urllib.parse import urljoin


async def get_events(page, group_url, max_events=20):
    """Fetch upcoming event URLs from a meetup group page using an existing page."""
    group_url = group_url.rstrip("/")
    events_url = group_url + "/events/"

    await page.goto(events_url)
    await page.wait_for_timeout(3000)

    event_urls = []
    for link in await page.query_selector_all("a"):
        href = await link.get_attribute("href")
        if not href:
            continue

        if href.startswith("/"):
            href = urljoin("https://www.meetup.com", href)

        if href.startswith(group_url + "/events/"):
            if "#/" in href or ("?" in href and "/events/" not in href):
                continue

            normalized = href.split("?")[0].rstrip("/") + "/"
            if normalized not in event_urls:
                event_urls.append(normalized)

        if len(event_urls) >= max_events:
            break

    return event_urls


if __name__ == "__main__":
    group = "https://www.meetup.com/forex-traders-funded/"
    events = get_events(group)
    for e in events:
        print(e)
