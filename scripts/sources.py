"""
Liste des sources RSS pour la veille technologique
"""

SOURCES = {
    "US": [
        {"name": "OpenAI Blog", "url": "https://openai.com/blog/rss.xml"},
        {"name": "Google AI", "url": "https://blog.google/technology/ai/rss/"},
        {"name": "Microsoft AI", "url": "https://blogs.microsoft.com/ai/feed/"},
        {"name": "Anthropic", "url": "https://www.anthropic.com/news/rss.xml"},
        {"name": "TechCrunch AI", "url": "https://techcrunch.com/category/artificial-intelligence/feed/"},
    ],
    "EU": [
        {"name": "Mistral AI", "url": "https://mistral.ai/news/rss.xml"},
        {"name": "N8N Blog", "url": "https://blog.n8n.io/rss/"},
        {"name": "Sifted", "url": "https://sifted.eu/feed"},
    ],
    "CN": [
        {"name": "TechNode", "url": "https://technode.com/feed/"},
        {"name": "SCMP Tech", "url": "https://www.scmp.com/rss/91/feed"},
    ],
    "COMPETITORS": [
        {"name": "Zapier Blog", "url": "https://zapier.com/blog/feed/"},
        {"name": "Make Blog", "url": "https://www.make.com/en/blog/rss"},
    ],
    "N8N_RELEASES": [
        {"name": "N8N Releases", "url": "https://github.com/n8n-io/n8n/releases.atom"},
    ]
}

YOUTUBE_CHANNELS = [
    {"name": "N8N Official", "channel_id": "UCFvDUHxI1S_dOPFerPLmDHw"},
    {"name": "Liam Ottley", "channel_id": "UCnawmTlkqrOXcB2tWrS1dYQ"},
    {"name": "AI Explained", "channel_id": "UCNJ1Ymd5yFuUPtn21xtRbbw"},
    {"name": "Two Minute Papers", "channel_id": "UCbfYPyITQ-7l4upoX8nvctg"},
]

if __name__ == "__main__":
    total = sum(len(sources) for sources in SOURCES.values())
    print(f"Total RSS sources: {total}")
    print(f"YouTube channels: {len(YOUTUBE_CHANNELS)}")
    
    for category, sources in SOURCES.items():
        print(f"\n{category}:")
        for source in sources:
            print(f"  - {source['name']}: {source['url']}")
