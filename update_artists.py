import re

FILE_PATH = "spotify_collector.py"

NEW_DICT = """ARTISTS_BY_DECADE = {
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
}"""

def update_artists():
    with open(FILE_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # Replace dict
    pattern_dict = r'ARTISTS_BY_DECADE = \{.*?\}'
    content = re.sub(pattern_dict, NEW_DICT, content, flags=re.DOTALL)
    
    # Replace limits
    content = content.replace("SONGS_PER_ARTIST = 25", "SONGS_PER_ARTIST = 20")
    content = content.replace("def get_artist_top_tracks(sp: spotipy.Spotify, artist_name: str, n: int = 25)", "def get_artist_top_tracks(sp: spotipy.Spotify, artist_name: str, n: int = 20)")
    
    # In case there are hardcoded limits for testing etc.
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        f.write(content)

    print("✅ spotify_collector.py 설정 업데이트 완료: 아티스트 100명, 20곡씩 세팅됨")

if __name__ == "__main__":
    update_artists()
