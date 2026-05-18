"""
Process Apify scrape results into a clean lead list for email campaigns.
Usage: python process_leads.py --input google_maps_results.json --output leads.csv
"""

import json
import csv
import argparse
import re
from pathlib import Path


def extract_emails_from_text(text: str) -> list[str]:
    pattern = r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}"
    return re.findall(pattern, text or "")


def process_google_maps(data: list[dict]) -> list[dict]:
    leads = []
    for place in data:
        rating = place.get("totalScore") or place.get("rating", 0)
        if not rating or float(rating) > 3.5:
            continue

        emails = place.get("emails") or []
        if not emails:
            website = place.get("website", "")
            emails = extract_emails_from_text(website)

        if not emails:
            continue

        top_complaints = []
        reviews = place.get("reviews") or []
        for review in reviews:
            if review.get("stars", 5) <= 2:
                top_complaints.append(review.get("text", "")[:120])

        leads.append({
            "name": place.get("title", ""),
            "email": emails[0],
            "phone": place.get("phone", ""),
            "website": place.get("website", ""),
            "rating": rating,
            "review_count": place.get("reviewsCount", 0),
            "address": place.get("address", ""),
            "top_complaint": top_complaints[0] if top_complaints else "",
            "google_maps_url": place.get("url", ""),
            "lead_type": "b2b_pet_store",
        })

    return leads


def process_amazon_reviews(data: list[dict]) -> list[dict]:
    """Extract pain points from Amazon reviews — used for email copy, not direct leads."""
    pain_points: dict[str, int] = {}
    categories = [
        "broke", "cheap", "quality", "size", "smell", "clean",
        "refund", "waste", "disappointed", "doesn't work", "misleading"
    ]

    for review in data:
        text = (review.get("reviewText") or review.get("body") or "").lower()
        for keyword in categories:
            if keyword in text:
                pain_points[keyword] = pain_points.get(keyword, 0) + 1

    sorted_pain_points = sorted(pain_points.items(), key=lambda x: x[1], reverse=True)
    print("\n=== TOP PAIN POINTS FROM AMAZON REVIEWS ===")
    for keyword, count in sorted_pain_points[:10]:
        print(f"  '{keyword}' mentioned {count} times")
    print("Use these to write subject lines and email body copy.\n")
    return []


def process_instagram(data: list[dict]) -> list[dict]:
    leads = []
    for account in data:
        bio = account.get("biography", "")
        emails = extract_emails_from_text(bio)
        external_url = account.get("externalUrl", "")
        if not emails and external_url:
            emails = extract_emails_from_text(external_url)

        if not emails:
            continue

        followers = account.get("followersCount", 0)
        if followers < 1000:
            continue

        leads.append({
            "name": account.get("fullName", account.get("username", "")),
            "email": emails[0],
            "instagram_handle": f"@{account.get('username', '')}",
            "followers": followers,
            "bio": bio[:100],
            "profile_url": f"https://instagram.com/{account.get('username', '')}",
            "lead_type": "influencer",
        })

    return leads


def save_csv(leads: list[dict], output_path: str):
    if not leads:
        print("No leads found to export.")
        return

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=leads[0].keys())
        writer.writeheader()
        writer.writerows(leads)

    print(f"Exported {len(leads)} leads to {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Process Apify results into lead list")
    parser.add_argument("--input", required=True, help="Path to Apify JSON export")
    parser.add_argument("--output", default="leads.csv", help="Output CSV path")
    parser.add_argument("--type", choices=["google_maps", "amazon", "instagram"],
                        default="google_maps", help="Type of Apify data")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)

    if args.type == "google_maps":
        leads = process_google_maps(data)
    elif args.type == "amazon":
        leads = process_amazon_reviews(data)
    elif args.type == "instagram":
        leads = process_instagram(data)
    else:
        leads = []

    save_csv(leads, args.output)


if __name__ == "__main__":
    main()
