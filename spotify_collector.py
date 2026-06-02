"""
artists.py (구 spotify_collector.py)
=====================================
분석 대상 아티스트 라인업 정의.
Spotify API 및 시뮬레이션 코드는 제거됨.
"""

# ─── 아티스트 라인업 ────────────────────────────────────────────────────────────
ARTISTS_BY_DECADE = {
    "90s": [
        "Nirvana", "Radiohead", "Oasis", "Green Day", "Mariah Carey",
        "Pearl Jam", "Red Hot Chili Peppers", "TLC", "Boyz II Men", "Madonna",
        "Snoop Dogg", "2Pac", "The Notorious B.I.G.", "Celine Dion", "Whitney Houston",
        "R.E.M.", "U2", "Foo Fighters", "No Doubt", "Weezer",
        "Alanis Morissette", "Beck", "The Smashing Pumpkins", "Janet Jackson", "Spice Girls"
    ],
    "00s": [
        "Coldplay", "Linkin Park", "Maroon 5", "Beyoncé", "Eminem",
        "Jay-Z", "Kanye West", "Rihanna", "Britney Spears", "Justin Timberlake",
        "Usher", "Outkast", "The Killers", "The Strokes", "Arctic Monkeys",
        "Muse", "John Mayer", "Alicia Keys", "P!nk", "Kelly Clarkson",
        "Black Eyed Peas", "Fall Out Boy", "My Chemical Romance", "Avril Lavigne", "Lady Gaga"
    ],
    "10s": [
        "Taylor Swift", "Bruno Mars", "Adele", "Ed Sheeran", "One Direction",
        "Drake", "Justin Bieber", "Ariana Grande", "Post Malone", "The Weeknd",
        "Kendrick Lamar", "J. Cole", "Katy Perry", "Imagine Dragons", "Twenty One Pilots",
        "Halsey", "Billie Eilish", "Shawn Mendes", "Dua Lipa", "Sam Smith",
        "Frank Ocean", "Lana Del Rey", "Lorde", "Cardi B", "Travis Scott"
    ],
    "20s": [
        "Olivia Rodrigo", "Doja Cat", "Lil Nas X", "Bad Bunny", "Megan Thee Stallion",
        "Jack Harlow", "The Kid LAROI", "SZA", "Morgan Wallen", "Luke Combs",
        "Tate McRae", "Sabrina Carpenter", "PinkPantheress", "Ice Spice", "Central Cee",
        "Peso Pluma", "Benson Boone", "Noah Kahan", "Zach Bryan", "Chappell Roan",
        "Tyla", "Victoria Monét", "Reneé Rapp", "Laufey", "NewJeans"
    ],
}

SONGS_PER_ARTIST = 20  # 아티스트당 수집 곡 수
