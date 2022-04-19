# Music Complexity Analysis

## How to Run

### Scraping data from Ultimate Guitar
`GatherSongPages.ipynb` uses Selenium to tab through Ultimate Guitar (filtering results by decade) and saves the raw `.html` output.

`ParseHTML.ipynb` uses BeautifulSoup to scrape this output, generating `.json` files for each song with structural and chord progression information.

### Structural Complexity
`SongStructure.ipynb` and `ChordProgression.ipynb` calculate the structure and chord progression statistics seen on the web page.

`VariationFromPattern.ipynb` looks at how songs vary from standard patterns. For structure,  "verse-chorus-verse-chorus-bridge-chorus" is a common structure that many songs use. For chord progression, the I-V-vi-IV chord progression is famously used in a lot of pop music.

### Genre
`GetGenreLastFM.ipynb` uses BeautifulSoup to scrape Genre information for each song from Last.FM. Then, `GetGenreCounts.ipynb` cleans the data up a bit and saves count information for each decade.

`MarkovChainsForGenres.ipynb` uses the Markov Chain code from `SongStructyre.ipynb` to develop similar transition matrices, only this time splitting data by genre, not decade.

### Lyrics
Lyrical analysis hasn't been included on the web page yet, but it's coming soon!

`GetLyricLists.ipynb` scrapes lyrics from each song's `.html` page (which is saved in the `GatherSongPages.ipynb` notebook above).

`SentimentAnalysisForLyrics.ipynb` uses NLTK's Sentiment Intensity Analyzer to get sentiment scores for each song's lyrics.

`LyricsForWordcloud.ipynb` cleans the lyrics and prints them out to one file per decade. This is for a word cloud visualization that's coming soon to the web page.
