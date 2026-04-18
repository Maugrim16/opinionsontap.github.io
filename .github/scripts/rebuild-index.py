#!/usr/bin/env python3
"""
Rebuild the-tap/index.html from all published posts.
Most recent post becomes the hero card (full width).
Posts tagged The Pursuit or The Culture become Tier 1 two-column cards.
All others become standard single-column cards.
Why the Pub is hardcoded as it predates the POST_META system.
"""

import os
import re
from datetime import datetime

THE_TAP_DIR = "the-tap"
INDEX_FILE = os.path.join(THE_TAP_DIR, "index.html")
SKIP_FILES = {"index.html"}
TIER1_TAGS = {"The Pursuit", "The Culture"}

# Hardcoded legacy post -- predates POST_META system
WHY_THE_PUB = {
    "filename": "why-the-pub-is-the-last-honest-place-left.html",
    "title": "Why the Pub is the Last Honest Place Left",
    "date": "11 April 2026",
    "publish_date": "2026-04-11",
    "tag": "Pub Culture",
    "excerpt": "Everywhere else you go, people are performing. The pub is where that stops.",
    "card_image": "pub-card.jpg",
}


def parse_post_meta(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    meta = {}
    meta_match = re.search(r"<!--\s*POST_META(.*?)-->", content, re.DOTALL)
    if not meta_match:
        return None
    for line in meta_match.group(1).strip().splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            meta[key.strip().lower()] = value.strip()
    date_match = re.search(r'name="publish-date"\s+content="([^"]+)"', content)
    if date_match:
        meta["publish_date"] = date_match.group(1)
    elif "date" in meta:
        try:
            meta["publish_date"] = datetime.strptime(meta["date"], "%d %B %Y").strftime("%Y-%m-%d")
        except ValueError:
            meta["publish_date"] = "2026-01-01"
    meta["filename"] = os.path.basename(filepath)
    return meta


def get_all_posts():
    posts = []
    found_why_the_pub = False
    for filename in os.listdir(THE_TAP_DIR):
        if filename in SKIP_FILES or not filename.endswith(".html"):
            continue
        if filename == WHY_THE_PUB["filename"]:
            found_why_the_pub = True
            posts.append(WHY_THE_PUB)
            continue
        meta = parse_post_meta(os.path.join(THE_TAP_DIR, filename))
        if meta:
            # Use bg image as fallback if card image not yet available
            if meta.get("card_image", "").endswith("-card.jpg"):
                bg = meta["card_image"].replace("-card.jpg", "-bg.jpg")
                bg_path = os.path.join("assets", bg)
                if not os.path.exists(bg_path):
                    pass  # keep card_image as-is, will resolve when card is uploaded
            posts.append(meta)
    if not found_why_the_pub:
        # File exists in the-tap but has no META -- add it anyway
        why_path = os.path.join(THE_TAP_DIR, WHY_THE_PUB["filename"])
        if os.path.exists(why_path):
            posts.append(WHY_THE_PUB)
    posts.sort(key=lambda p: p.get("publish_date", ""), reverse=True)
    return posts


def build_hero_card(post):
    img = post.get("card_image", "pub-card.jpg")
    return f"""
        <a href="{post['filename']}" class="tap-card tap-card--hero">
          <div class="tap-card-image">
            <img src="../assets/{img}" alt="{post.get('title', '')}" />
          </div>
          <div class="tap-card-body">
            <span class="tap-card-date">{post.get('date', '')}</span>
            <h2>{post.get('title', '')}</h2>
            <p class="tap-card-subhead">{post.get('excerpt', '')}</p>
          </div>
        </a>"""


def build_tier1_card(post):
    img = post.get("card_image", "pub-card.jpg")
    return f"""
        <a href="{post['filename']}" class="tap-card tap-card--tier1">
          <div class="tap-card-image">
            <img src="../assets/{img}" alt="{post.get('title', '')}" />
          </div>
          <div class="tap-card-body">
            <span class="tap-card-date">{post.get('date', '')}</span>
            <h2>{post.get('title', '')}</h2>
            <p class="tap-card-subhead">{post.get('excerpt', '')}</p>
          </div>
        </a>"""


def build_standard_card(post):
    img = post.get("card_image", "pub-card.jpg")
    return f"""
        <a href="{post['filename']}" class="tap-card">
          <div class="tap-card-image">
            <img src="../assets/{img}" alt="{post.get('title', '')}" />
          </div>
          <div class="tap-card-body">
            <span class="tap-card-date">{post.get('date', '')}</span>
            <h2>{post.get('title', '')}</h2>
            <p class="tap-card-subhead">{post.get('excerpt', '')}</p>
          </div>
        </a>"""


def rebuild_index(posts):
    if not posts:
        cards_html = '<p class="tap-coming-soon">Posts coming soon.</p>'
    else:
        hero = build_hero_card(posts[0])
        rest = ""
        for p in posts[1:]:
            tag = p.get("tag", "")
            if tag in TIER1_TAGS:
                rest += build_tier1_card(p)
            else:
                rest += build_standard_card(p)
        cards_html = hero + rest

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>The Tap — Pub Culture, Travel & Golf Blog | Opinions on Tap</title>
  <meta name="description" content="Pub culture, travel, golf and the occasional opinion worth reading. The Tap is the blog from Opinions on Tap." />
  <meta property="og:type" content="website" />
  <meta property="og:url" content="https://opinionsontap.com/the-tap/" />
  <meta property="og:title" content="The Tap — Pub Culture, Travel & Golf Blog" />
  <meta property="og:description" content="Pub culture, great views, cold ones and the occasional take worth reading. Pull up a stool." />
  <meta property="og:image" content="https://opinionsontap.com/assets/pub-card.jpg" />
  <meta property="og:site_name" content="Opinions on Tap" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="The Tap — Pub Culture, Travel & Golf Blog" />
  <meta name="twitter:description" content="Pub culture, great views, cold ones and the occasional take worth reading." />
  <meta name="twitter:image" content="https://opinionsontap.com/assets/pub-card.jpg" />
  <link rel="canonical" href="https://opinionsontap.com/the-tap/" />
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;600&family=Inter:wght@400;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="../style.css" />
  <style>
    .tap-card h2, .tap-card--hero h2, .tap-card--tier1 h2 {{
      font-family: 'Playfair Display', Georgia, serif;
      font-weight: 500;
      letter-spacing: 0.012em;
      -webkit-font-smoothing: antialiased;
    }}
    .tap-card-date, .tap-card-subhead, .tap-card-subhead-2 {{
      font-family: 'Inter', sans-serif;
      font-weight: 400;
    }}
    .tap-hero-inner h1 {{
      font-family: 'Playfair Display', Georgia, serif;
      font-weight: 500;
      letter-spacing: 0.01em;
    }}
    .tap-intro-inner p {{ font-family: 'Inter', sans-serif; }}
    .tap-hero {{ background: var(--warm-dark); padding: 160px 24px 80px; position: relative; overflow: hidden; border-bottom: 1px solid rgba(201,168,76,0.12); }}
    .tap-hero::after {{ content: ''; position: absolute; inset: 0; background-image: url('../assets/tap-bg.jpg'); background-size: cover; background-position: center 40%; z-index: 0; }}
    .tap-hero::before {{ content: ''; position: absolute; inset: 0; background: linear-gradient(to right, rgba(10,7,2,0.88) 0%, rgba(10,7,2,0.72) 50%, rgba(10,7,2,0.45) 100%); z-index: 1; pointer-events: none; }}
    .tap-hero-inner {{ position: relative; z-index: 1; max-width: var(--max-width); margin: 0 auto; }}
    .tap-hero-inner h1 {{ font-size: clamp(3rem, 6vw, 6rem); line-height: 1; margin-bottom: 16px; color: var(--off-white); }}
    .tap-hero-inner h1 span {{ color: var(--gold); }}
    .tap-hero-inner p {{ font-size: 1.05rem; color: var(--text-body); opacity: 0.7; max-width: 480px; line-height: 1.7; }}
    .tap-intro {{ background: var(--warm-dark); border-bottom: 1px solid rgba(201,168,76,0.1); padding: 48px 24px; }}
    .tap-intro-inner {{ max-width: 760px; margin: 0 auto; }}
    .tap-intro-inner p {{ font-size: 1rem; color: var(--text-body); opacity: 0.72; line-height: 1.8; }}
    .tap-posts {{ background: var(--black); padding: var(--section-pad); }}
    .tap-posts-inner {{ max-width: var(--max-width); margin: 0 auto; }}
    .tap-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px; align-items: start; }}
    a.tap-card {{ text-decoration: none; display: flex; flex-direction: column; }}
    .tap-card {{ background: var(--warm-dark); border: 1px solid rgba(201,168,76,0.08); border-radius: 2px; overflow: hidden; transition: border-color 0.25s, transform 0.25s; display: flex; flex-direction: column; cursor: pointer; }}
    .tap-card:hover {{ border-color: rgba(201,168,76,0.25); transform: translateY(-4px); }}
    .tap-card--hero {{ grid-column: span 3; flex-direction: row !important; min-height: 360px; border-color: rgba(201,168,76,0.1); }}
    .tap-card--hero:hover {{ transform: translateY(-3px); border-color: rgba(201,168,76,0.3); }}
    .tap-card--hero .tap-card-image {{ width: 52%; flex-shrink: 0; min-height: 360px; position: relative; }}
    .tap-card--hero .tap-card-image img {{ position: absolute; inset: 0; width: 100% !important; height: 100% !important; max-width: none !important; object-fit: cover; }}
    .tap-card--hero .tap-card-body {{ padding: 52px 56px; justify-content: center; }}
    .tap-card--hero h2 {{ font-size: clamp(1.9rem, 2.8vw, 2.7rem); line-height: 1.15; margin-bottom: 20px; }}
    .tap-card--hero .tap-card-date {{ margin-bottom: 18px; font-size: 0.72rem; }}
    .tap-card--hero .tap-card-subhead {{ font-size: 1.05rem; line-height: 1.55; max-width: 400px; }}
    .tap-card--tier1 {{ grid-column: span 2; flex-direction: row !important; }}
    .tap-card--tier1 .tap-card-image {{ width: 44%; flex-shrink: 0; min-height: 240px; position: relative; }}
    .tap-card--tier1 .tap-card-image img {{ position: absolute; inset: 0; width: 100% !important; height: 100% !important; max-width: none !important; object-fit: cover; }}
    .tap-card--tier1 .tap-card-body {{ padding: 28px 28px 24px; }}
    .tap-card--tier1 h2 {{ font-size: 1.45rem; line-height: 1.2; margin-bottom: 14px; }}
    .tap-card--tier1 .tap-card-subhead {{ font-size: 0.95rem; }}
    .tap-card-image {{ overflow: hidden; background: #1a1508; }}
    .tap-card:not(.tap-card--tier1):not(.tap-card--hero) .tap-card-image {{ width: 100%; aspect-ratio: 16/9; }}
    .tap-card-image img {{ width: 100%; height: 100%; object-fit: cover; display: block; transition: transform 0.4s ease; }}
    .tap-card:hover .tap-card-image img {{ transform: scale(1.04); }}
    .tap-card-body {{ padding: 20px 20px 20px; flex: 1; display: flex; flex-direction: column; }}
    .tap-card-date {{ font-size: 0.68rem; color: var(--text-body); opacity: 0.28; margin-bottom: 10px; display: block; letter-spacing: 0.04em; }}
    .tap-card h2 {{ font-size: 1.12rem; line-height: 1.3; color: var(--off-white); margin-bottom: 10px; letter-spacing: 0.012em; }}
    .tap-card-subhead {{ font-size: 0.88rem; color: var(--text-body); opacity: 0.55; line-height: 1.55; margin-bottom: 4px; }}
    .tap-card-subhead-2 {{ font-size: 0.83rem; color: var(--text-body); opacity: 0.28; line-height: 1.55; font-style: italic; }}
    .tap-coming-soon {{ text-align: center; padding: 80px 24px; color: var(--text-body); opacity: 0.4; font-size: 1rem; }}
    @media (max-width: 900px) {{
      .tap-grid {{ grid-template-columns: 1fr 1fr; }}
      .tap-card--hero {{ grid-column: span 2; min-height: auto; }}
      .tap-card--tier1 {{ grid-column: span 2; }}
    }}
    @media (max-width: 600px) {{
      .tap-grid {{ grid-template-columns: 1fr; }}
      .tap-card--hero {{ grid-column: span 1; }}
      .tap-card--hero .tap-card-image {{ width: 100%; min-height: 220px; }}
      .tap-card--hero .tap-card-body {{ padding: 28px 24px; }}
      .tap-card--tier1 {{ grid-column: span 1; }}
      .tap-card--tier1 .tap-card-image {{ width: 100%; min-height: 200px; }}
    }}
  </style>
</head>
<body>
  <nav class="nav" id="mainNav">
    <a href="../index.html" class="nav-logo">
      <img src="../assets/logo.png" alt="Opinions on Tap" />
      <span class="nav-logo-text">Opinions on Tap</span>
    </a>
    <ul class="nav-links">
      <li><a href="../index.html">Home</a></li>
      <li><a href="../our-story.html">Our Story</a></li>
      <li><a href="../shop.html">Shop</a></li>
      <li><a href="../contact.html">Contact</a></li>
      <li><a href="index.html">The Tap</a></li>
    </ul>
    <div class="nav-cta"><a href="../shop.html" class="btn btn-primary">Shop</a></div>
    <button class="nav-toggle" aria-label="Open menu"><span></span><span></span><span></span></button>
  </nav>
  <section class="tap-hero">
    <div class="tap-hero-inner">
      <p class="concept-label">The Tap</p>
      <h1>Opinions. <span>On tap.</span></h1>
      <p>Pub culture, great views, cold ones and the occasional take worth reading. Pull up a stool.</p>
    </div>
  </section>
  <section class="tap-intro">
    <div class="tap-intro-inner">
      <p>The Tap covers pub culture, travel, golf, fishing and the kind of opinions that come out after the second round. Stories about the road, the fairway, the water and the bar. Written for people who wear their experience rather than talk about it.</p>
    </div>
  </section>
  <section class="tap-posts">
    <div class="tap-posts-inner">
      <div class="tap-grid">
        {cards_html}
      </div>
    </div>
  </section>
  <footer class="footer">
    <div class="footer-inner">
      <div class="footer-brand">
        <img src="../assets/logo.png" alt="Opinions on Tap" class="footer-logo" />
        <p class="footer-tagline">It's My Pint of View</p>
        <p class="footer-desc">Pub life gear for people with opinions. Designed in Australia. Shipped worldwide via Amazon.</p>
      </div>
      <nav class="footer-nav">
        <h4>Navigate</h4>
        <ul>
          <li><a href="../index.html">Home</a></li>
          <li><a href="../our-story.html">Our Story</a></li>
          <li><a href="../shop.html">Shop</a></li>
          <li><a href="../contact.html">Contact</a></li>
          <li><a href="index.html">The Tap</a></li>
        </ul>
      </nav>
      <div class="footer-social">
        <h4>Follow Along</h4>
        <div class="social-links">
          <a href="https://www.instagram.com/opinionsontapofficial/" target="_blank" rel="noopener" class="social-link" aria-label="Instagram">📷</a>
          <a href="https://www.facebook.com/profile.php?id=61575730448745" target="_blank" rel="noopener" class="social-link" aria-label="Facebook">📘</a>
        </div>
      </div>
    </div>
    <div class="footer-bottom">
      <span>© 2026 Opinions on Tap. All rights reserved.</span>
      <span>opinionsontap.com</span>
    </div>
  </footer>
  <script>
    const nav = document.getElementById('mainNav');
    window.addEventListener('scroll', () => {{ nav.classList.toggle('scrolled', window.scrollY > 60); }});
  </script>
</body>
</html>"""

    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Rebuilt {INDEX_FILE} with {len(posts)} post(s).")


if __name__ == "__main__":
    posts = get_all_posts()
    rebuild_index(posts)
