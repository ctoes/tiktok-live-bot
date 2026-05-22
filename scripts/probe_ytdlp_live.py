import yt_dlp

url = 'https://www.tiktok.com/@beautybasetv/live'
opts = {
    'quiet': True,
    'no_warnings': True,
    'skip_download': True,
    'noplaylist': True,
}

with yt_dlp.YoutubeDL(opts) as ydl:
    info = ydl.extract_info(url, download=False)
    print('is_live=', info.get('is_live'))
    print('title=', info.get('title'))
    print('webpage_url=', info.get('webpage_url'))
    print('url=', info.get('url'))
    print('keys=', list(info.keys())[:20])
