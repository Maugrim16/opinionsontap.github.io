#!/usr/bin/env python3
"""
Rebuild the-tap/index.html from all published posts.
Runs after publish-posts.yml moves scheduled posts into the-tap/.
First post alphabetically by date becomes the featured card.
All others become regular grid cards.
"""

import os
import re
from datetime import datetime

THE_TAP_DIR = "the-tap"
INDEX_FILE = os.path.join(THE_TAP_DIR, "index.html")
SKIP_FILES = {"index.html"}


def parse_post_meta(filepath):
    """Extract POST_META block from a post file."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    meta = {}

    # Extract POST_META comment block
    meta_match = re.search(r"<!--\s*POST_META(.*?)-->", content, re.DOTALL)
    if not meta_match:
        return None

    meta_block = meta_match.group(1)

    for line in meta_block.strip().splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            meta[key.strip().lower()] = value.strip()

    # Also grab publish-date from meta tag for sorting
    date_match = re.search(r'name="publish-date"\s+content="([^"]+)"', content)
    if date_match:
        meta["publish_date"] = date_match.group(1)
    elif "date" in meta:
        # Parse from human date e.g. "17 April 2026"
        try:
            meta["publish_date"] = datetime.strptime(meta["date"], "%d %B %Y").strftime("%Y-%m-%d")
        except ValueError:
            meta["publish_date"] = "2026-01-01"

    meta["filename"] = os.path.basename(filepath)
    return meta


def get_all_posts():
    """Get metadata for all published posts, sorted by date descending."""
    posts = []
    for filename in os.listdir(THE_TAP_DIR):
        if filename in SKIP_FILES or not filename.endswith(".html"):
            continue
        filepath = os.path.join(THE_TAP_DIR, filename)
        meta = parse_post_meta(filepath)
        if meta:
            posts.append(meta)

    posts.sort(key=lambda p: p.get("publish_date", ""), reverse=True)
    return posts


def build_featured_card(post):
    """Build the featured (wide) card HTML for the most recent post."""
    return f"""
        <!-- Featured Post -->
        <article class="tap-card tap-card--featured">
          <div class="tap-card-image">
            <img src="../assets/{post.get('card_image', 'pub-card.jpg')}" alt="{post.get('card_alt', '')}" />
          </div>
          <div class="tap-card-body">
            <div class="tap-card-meta">
              <span class="tap-card-tag">{post.get('tag', 'Blog')}</span>
              <span class="tap-card-date">{post.get('date', '')}</span>
            </div>
            <h2><a href="{post['filename']}">{post.get('title', '')}</a></h2>
            <p class="tap-card-excerpt">{post.get('excerpt', '')}</p>
            <a href="{post['filename']}" class="tap-card-read">Read More →</a>
          </div>
        </article>"""


def build_regular_card(post):
    """Build a standard grid card for older posts."""
    return f"""
        <!-- Post -->
        <article class="tap-card">
          <div class="tap-card-image">
            <img src="../assets/{post.get('card_image', 'pub-card.jpg')}" alt="{post.get('card_alt', '')}" />
          </div>
          <div class="tap-card-body">
            <div class="tap-card-meta">
              <span class="tap-card-tag">{post.get('tag', 'Blog')}</span>
              <span class="tap-card-date">{post.get('date', '')}</span>
            </div>
            <h2><a href="{post['filename']}">{post.get('title', '')}</a></h2>
            <p class="tap-card-excerpt">{post.get('excerpt', '')}</p>
            <a href="{post['filename']}" class="tap-card-read">Read More →</a>
          </div>
        </article>"""


def rebuild_index(posts):
    """Write a fresh the-tap/index.html with all current posts."""

    if not posts:
        cards_html = '<p class="tap-coming-soon">Posts coming soon.</p>'
    else:
        featured = build_featured_card(posts[0])
        regulars = "".join(build_regular_card(p) for p in posts[1:])
        cards_html = featured + regulars

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>The Tap — Pub Culture, Travel & Golf Blog | Opinions on Tap</title>
  <meta name="description" content="Pub culture, travel, golf and the occasional opinion worth reading. The Tap is the blog from Opinions on Tap — a pub life brand built around the pint glass as a lens on the world." />
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
  <link rel="stylesheet" href="../style.css" />
  <style>
    .tap-hero {{
      background: var(--warm-dark);
      padding: 160px 24px 80px;
      position: relative;
      overflow: hidden;
      border-bottom: 1px solid rgba(201,168,76,0.12);
    }}
    .tap-hero::after {{
      content: '';
      position: absolute;
      inset: 0;
      background-image: url('../assets/tap-bg.jpg');
      background-size: cover;
      background-position: center 40%;
      z-index: 0;
    }}
    .tap-hero::before {{
      content: '';
      position: absolute;
      inset: 0;
      background: linear-gradient(to right, rgba(10,7,2,0.88) 0%, rgba(10,7,2,0.72) 50%, rgba(10,7,2,0.45) 100%);
      z-index: 1;
      pointer-events: none;
    }}
    .tap-hero-inner {{
      position: relative;
      z-index: 1;
      max-width: var(--max-width);
      margin: 0 auto;
    }}
    .tap-hero-inner h1 {{ font-size: clamp(3rem, 6vw, 6rem); line-height: 1; margin-bottom: 16px; color: var(--off-white); }}
    .tap-hero-inner h1 span {{ color: var(--gold); }}
    .tap-hero-inner p {{ font-size: 1.1rem; color: var(--text-body); opacity: 0.7; max-width: 480px; line-height: 1.7; }}
    .tap-posts {{ background: var(--black); padding: var(--section-pad); }}
    .tap-intro {{ background: var(--warm-dark); border-bottom: 1px solid rgba(201,168,76,0.1); padding: 48px 24px; }}
    .tap-intro-inner {{ max-width: 760px; margin: 0 auto; }}
    .tap-intro-inner p {{ font-size: 1.05rem; color: var(--text-body); opacity: 0.75; line-height: 1.8; }}
    .tap-posts-inner {{ max-width: var(--max-width); margin: 0 auto; }}
    .tap-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 32px; margin-top: 48px; }}
    .tap-card {{ background: var(--warm-dark); border: 1px solid rgba(201,168,76,0.1); border-radius: 2px; overflow: hidden; transition: border-color 0.2s, transform 0.2s; display: flex; flex-direction: column; }}
    .tap-card:hover {{ border-color: rgba(201,168,76,0.3); transform: translateY(-4px); }}
    .tap-card-image {{ width: 100%; aspect-ratio: 16/9; overflow: hidden; background: var(--mid-grey); position: relative; }}
    .tap-card-image img {{ width: 100%; height: 100%; object-fit: cover; transition: transform 0.4s ease; }}
    .tap-card:hover .tap-card-image img {{ transform: scale(1.04); }}
    .tap-card-body {{ padding: 28px 24px 24px; flex: 1; display: flex; flex-direction: column; }}
    .tap-card-meta {{ display: flex; align-items: center; gap: 12px; margin-bottom: 14px; }}
    .tap-card-tag {{ font-family: var(--font-body); font-weight: 700; font-size: 0.7rem; letter-spacing: 0.2em; text-transform: uppercase; color: var(--gold); background: rgba(201,168,76,0.1); padding: 4px 10px; border-radius: 2px; }}
    .tap-card-date {{ font-size: 0.8rem; color: var(--text-body); opacity: 0.4; }}
    .tap-card h2 {{ font-size: 1.2rem; line-height: 1.3; margin-bottom: 12px; color: var(--off-white); font-family: var(--font-body); font-weight: 700; -webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale; text-rendering: optimizeLegibility; }}
    .tap-card h2 a {{ color: inherit; transition: color 0.2s; }}
    .tap-card h2 a:hover {{ color: var(--gold); }}
    .tap-card-excerpt {{ font-size: 0.9rem; color: var(--text-body); opacity: 0.65; line-height: 1.7; flex: 1; margin-bottom: 20px; }}
    .tap-card-read {{ font-family: var(--font-body); font-weight: 700; font-size: 0.8rem; letter-spacing: 0.1em; text-transform: uppercase; color: var(--gold); opacity: 0.8; transition: opacity 0.2s; }}
    .tap-card-read:hover {{ opacity: 1; }}
    .tap-card--featured {{ grid-column: span 2; flex-direction: row; }}
    .tap-card--featured .tap-card-image {{ width: 45%; aspect-ratio: unset; flex-shrink: 0; }}
    .tap-card--featured .tap-card-body {{ padding: 36px 32px; }}
    .tap-card--featured h2 {{ font-size: 1.6rem; }}
    .tap-coming-soon {{ text-align: center; padding: 80px 24px; color: var(--text-body); opacity: 0.4; font-size: 1rem; }}
    @media (max-width: 900px) {{
      .tap-grid {{ grid-template-columns: 1fr 1fr; }}
      .tap-card--featured {{ grid-column: span 2; flex-direction: column; }}
      .tap-card--featured .tap-card-image {{ width: 100%; aspect-ratio: 16/9; }}
    }}
    @media (max-width: 600px) {{
      .tap-grid {{ grid-template-columns: 1fr; }}
      .tap-card--featured {{ grid-column: span 1; }}
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
