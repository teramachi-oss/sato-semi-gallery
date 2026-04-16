#!/usr/bin/env python3
"""
佐藤ゼミ 投稿ギャラリー生成スクリプト

使い方:
  1. このスクリプトと同じフォルダに画像を入れる
  2. ファイル名ルール: 投稿者名__コメント.png（コメント省略可）
  3. python3 generate.py を実行
  4. gallery.html が生成される

対応画像: png, jpg, jpeg, gif, webp
"""

import os
import sys
import base64
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent
IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.webp'}
OUTPUT_FILE = SCRIPT_DIR / 'gallery.html'


def parse_filename(filepath: Path) -> dict:
    """ファイル名から投稿者名とコメントを抽出"""
    stem = filepath.stem
    if '__' in stem:
        name, comment = stem.split('__', 1)
    else:
        name = stem
        comment = ''
    return {
        'name': name.strip(),
        'comment': comment.strip(),
        'path': filepath.name,
    }


def image_to_base64(filepath: Path) -> str:
    """画像をbase64エンコード（HTML埋め込み用）"""
    suffix = filepath.suffix.lower()
    mime_map = {
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif',
        '.webp': 'image/webp',
    }
    mime = mime_map.get(suffix, 'image/png')
    with open(filepath, 'rb') as f:
        data = base64.b64encode(f.read()).decode('utf-8')
    return f'data:{mime};base64,{data}'


def collect_images() -> list:
    """フォルダ内の画像を収集してパース"""
    entries = []
    for f in sorted(SCRIPT_DIR.iterdir()):
        if f.suffix.lower() in IMAGE_EXTENSIONS:
            entry = parse_filename(f)
            entry['src'] = f.name
            entries.append(entry)
    return entries


def generate_html(entries: list) -> str:
    """HTMLギャラリーを生成"""
    generated = datetime.now().strftime('%Y-%m-%d %H:%M')
    count = len(entries)

    cards_html = ''
    for i, e in enumerate(entries):
        comment_html = f'<p class="comment">{e["comment"]}</p>' if e['comment'] else ''
        cards_html += f'''
      <div class="card" onclick="openLightbox({i})">
        <span class="card-num">{i+1:02d}</span>
        <div class="thumb-wrap">
          <img src="{e['src']}" alt="{e['name']}" loading="lazy">
        </div>
        <div class="info">
          <div class="author-row">
            <span class="author-dot"></span>
            <p class="author">{e['name']}</p>
          </div>
          {comment_html}
        </div>
      </div>'''

    lightbox_items = []
    for e in entries:
        name = e["name"].replace('"', '\\"')
        comment = e["comment"].replace('"', '\\"')
        src = e["src"].replace('"', '\\"')
        lightbox_items.append(f'{{"name":"{name}","comment":"{comment}","src":"{src}"}}')
    lightbox_data = ','.join(lightbox_items)

    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>佐藤ゼミ 投稿ギャラリー</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&family=Noto+Sans+JP:wght@400;600;700&display=swap');

  * {{ margin: 0; padding: 0; box-sizing: border-box; }}

  body {{
    font-family: 'Inter', 'Noto Sans JP', -apple-system, sans-serif;
    background: #FFFFFF;
    color: #333;
    min-height: 100vh;
    overflow-x: hidden;
  }}

  /* ===== Hero Header ===== */
  .hero {{
    position: relative;
    text-align: center;
    padding: 80px 20px 56px;
    overflow: hidden;
  }}
  .hero::before {{
    content: '';
    position: absolute;
    inset: 0;
    background:
      radial-gradient(ellipse 60% 50% at 20% 50%, rgba(236,0,140,0.08) 0%, transparent 70%),
      radial-gradient(ellipse 60% 50% at 80% 50%, rgba(139,82,232,0.08) 0%, transparent 70%),
      radial-gradient(ellipse 80% 40% at 50% 100%, rgba(139,82,232,0.05) 0%, transparent 60%);
    z-index: 0;
  }}
  .hero::after {{
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, transparent, #EC008C, #8B52E8, transparent);
  }}
  .hero > * {{ position: relative; z-index: 1; }}

  .hero-badge {{
    display: inline-block;
    padding: 4px 16px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #fff;
    background: linear-gradient(135deg, #EC008C, #8B52E8);
    border-radius: 20px;
    margin-bottom: 16px;
  }}
  .hero h1 {{
    font-size: 36px;
    font-weight: 800;
    color: #1a1a1a;
    letter-spacing: -0.01em;
    line-height: 1.3;
  }}
  .hero h1 span {{
    background: linear-gradient(135deg, #EC008C, #8B52E8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }}
  .hero-meta {{
    display: inline-flex;
    align-items: center;
    gap: 20px;
    margin-top: 20px;
    padding: 8px 24px;
    background: #fff;
    border-radius: 24px;
    box-shadow: 0 2px 12px rgba(139,82,232,0.1);
    font-size: 13px;
    color: #888;
    font-weight: 600;
  }}
  .hero-meta .count {{
    color: #8B52E8;
  }}

  /* ===== Gallery Grid ===== */
  .gallery {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 28px;
    padding: 40px 48px 100px;
    max-width: 1440px;
    margin: 0 auto;
  }}

  /* ===== Card ===== */
  .card {{
    position: relative;
    background: #fff;
    border-radius: 20px;
    overflow: hidden;
    cursor: pointer;
    transition: transform 0.3s cubic-bezier(0.23,1,0.32,1), box-shadow 0.3s ease;
    box-shadow: 0 4px 16px rgba(0,0,0,0.06);
  }}
  .card::before {{
    content: '';
    position: absolute;
    inset: 0;
    border-radius: 20px;
    padding: 2px;
    background: linear-gradient(135deg, rgba(236,0,140,0.3), rgba(139,82,232,0.3));
    -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
    -webkit-mask-composite: xor;
    mask-composite: exclude;
    opacity: 0;
    transition: opacity 0.3s ease;
    pointer-events: none;
    z-index: 2;
  }}
  .card:hover {{
    transform: translateY(-8px) scale(1.01);
    box-shadow:
      0 20px 40px rgba(139,82,232,0.15),
      0 8px 20px rgba(236,0,140,0.08);
  }}
  .card:hover::before {{
    opacity: 1;
  }}

  .card-num {{
    position: absolute;
    top: 12px;
    left: 12px;
    z-index: 3;
    font-size: 11px;
    font-weight: 800;
    color: #fff;
    background: linear-gradient(135deg, #EC008C, #8B52E8);
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 10px;
    box-shadow: 0 2px 8px rgba(139,82,232,0.3);
    letter-spacing: 0.02em;
  }}

  .thumb-wrap {{
    width: 100%;
    aspect-ratio: 4/3;
    overflow: hidden;
    background: linear-gradient(135deg, #f8f4ff, #fff2f8);
  }}
  .thumb-wrap img {{
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.4s cubic-bezier(0.23,1,0.32,1);
  }}
  .card:hover .thumb-wrap img {{
    transform: scale(1.06);
  }}

  .info {{
    padding: 20px 24px 24px;
    position: relative;
  }}
  .info::before {{
    content: '';
    position: absolute;
    top: 0; left: 24px; right: 24px;
    height: 2px;
    background: linear-gradient(90deg, #EC008C, #8B52E8);
    border-radius: 2px;
  }}

  .author-row {{
    display: flex;
    align-items: center;
    gap: 8px;
    margin-top: 4px;
  }}
  .author-dot {{
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: linear-gradient(135deg, #EC008C, #8B52E8);
    flex-shrink: 0;
  }}
  .author {{
    font-weight: 700;
    font-size: 15px;
    color: #1a1a1a;
  }}
  .comment {{
    font-size: 13px;
    color: #777;
    margin-top: 8px;
    margin-left: 16px;
    line-height: 1.6;
    padding-left: 8px;
    border-left: 2px solid rgba(139,82,232,0.2);
  }}

  /* ===== Lightbox ===== */
  .lightbox {{
    display: none;
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,0.88);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    z-index: 1000;
    justify-content: center;
    align-items: center;
    flex-direction: column;
  }}
  .lightbox.active {{
    display: flex;
    animation: lbFadeIn 0.25s ease;
  }}
  @keyframes lbFadeIn {{
    from {{ opacity: 0; }}
    to {{ opacity: 1; }}
  }}
  .lightbox .lb-img-wrap {{
    width: 80vw;
    height: 72vh;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }}
  .lightbox img {{
    max-width: 100%;
    max-height: 100%;
    object-fit: contain;
    border-radius: 12px;
    box-shadow: 0 8px 40px rgba(0,0,0,0.5);
  }}
  .lightbox .lb-info {{
    text-align: center;
    margin-top: 20px;
    padding: 12px 32px;
    background: rgba(255,255,255,0.06);
    border-radius: 16px;
    backdrop-filter: blur(4px);
  }}
  .lightbox .lb-author {{
    font-size: 20px;
    font-weight: 700;
    color: #fff;
  }}
  .lightbox .lb-comment {{
    font-size: 14px;
    color: rgba(255,255,255,0.6);
    margin-top: 4px;
  }}
  .lightbox .lb-counter {{
    font-size: 12px;
    color: rgba(255,255,255,0.35);
    margin-top: 8px;
    font-weight: 600;
    letter-spacing: 0.08em;
  }}
  .lightbox .lb-close {{
    position: absolute;
    top: 24px;
    right: 32px;
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    color: rgba(255,255,255,0.5);
    cursor: pointer;
    border-radius: 50%;
    background: rgba(255,255,255,0.08);
    transition: all 0.2s;
  }}
  .lightbox .lb-close:hover {{
    color: #fff;
    background: rgba(255,255,255,0.15);
  }}
  .lb-nav {{
    position: absolute;
    top: 50%;
    transform: translateY(-50%);
    width: 48px;
    height: 48px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 28px;
    color: rgba(255,255,255,0.5);
    cursor: pointer;
    user-select: none;
    border-radius: 50%;
    background: rgba(255,255,255,0.08);
    transition: all 0.2s;
  }}
  .lb-nav:hover {{
    color: #fff;
    background: rgba(255,255,255,0.15);
  }}
  .lb-prev {{ left: 20px; }}
  .lb-next {{ right: 20px; }}
</style>
</head>
<body>

<div class="hero">
  <div class="hero-badge">SHIFT AI</div>
  <h1>佐藤ゼミ <span>投稿ギャラリー</span></h1>
  <div class="hero-meta">
    <span class="count">{count} posts</span>
    <span>{generated}</span>
  </div>
</div>

<div class="gallery">{cards_html}
</div>

<div class="lightbox" id="lightbox">
  <span class="lb-close" onclick="closeLightbox()">&times;</span>
  <span class="lb-nav lb-prev" onclick="navLightbox(-1)">&lsaquo;</span>
  <span class="lb-nav lb-next" onclick="navLightbox(1)">&rsaquo;</span>
  <div class="lb-img-wrap"><img id="lb-img" src="" alt=""></div>
  <div class="lb-info">
    <p class="lb-author" id="lb-author"></p>
    <p class="lb-comment" id="lb-comment"></p>
    <p class="lb-counter" id="lb-counter"></p>
  </div>
</div>

<script>
const items = [{lightbox_data}];
let currentIndex = 0;

function openLightbox(i) {{
  currentIndex = i;
  updateLightbox();
  document.getElementById('lightbox').classList.add('active');
  document.body.style.overflow = 'hidden';
}}

function closeLightbox() {{
  document.getElementById('lightbox').classList.remove('active');
  document.body.style.overflow = '';
}}

function navLightbox(dir) {{
  currentIndex = (currentIndex + dir + items.length) % items.length;
  updateLightbox();
}}

function updateLightbox() {{
  const item = items[currentIndex];
  document.getElementById('lb-img').src = item.src;
  document.getElementById('lb-author').textContent = item.name;
  document.getElementById('lb-comment').textContent = item.comment || '';
  document.getElementById('lb-counter').textContent = (currentIndex+1) + ' / ' + items.length;
}}

document.getElementById('lightbox').addEventListener('click', function(e) {{
  if (e.target === this) closeLightbox();
}});

document.addEventListener('keydown', function(e) {{
  const lb = document.getElementById('lightbox');
  if (!lb.classList.contains('active')) return;
  if (e.key === 'Escape') closeLightbox();
  if (e.key === 'ArrowLeft') navLightbox(-1);
  if (e.key === 'ArrowRight') navLightbox(1);
}});
</script>

</body>
</html>'''


def main():
    entries = collect_images()
    if not entries:
        print('画像が見つかりません。このスクリプトと同じフォルダに画像を入れてください。')
        sys.exit(1)

    html = generate_html(entries)
    OUTPUT_FILE.write_text(html, encoding='utf-8')
    print(f'gallery.html を生成しました（{len(entries)}件）')


if __name__ == '__main__':
    main()
