# Sample Summarization Outputs

Pre-generated sample outputs comparing model engines, lengths, and readability scores.

## sample_article.txt

**Original Article:** 499 words, Readability: 46.5 (Difficult), Reading Level: Grade 12.2

### DistilBART (DISTILBART) · Short (~94.2% reduction)

> Cities around the world are rediscovering the rooftop as a place to grow food. Rooftop plantings also insulate the buildings beneath them. Most experts land somewhere in the middle.

- **Words:** 499 → 29 words
- **Readability (Flesch):** 46.5 → 59.9 (Fairly difficult)
- **Grade Level:** Grade 12.2 → Grade 7.3
- **Engine:** `sshleifer/distilbart-cnn-12-6 (Extractive fallback)`

### DistilBART (DISTILBART) · Medium (~80.4% reduction)

> Cities around the world are rediscovering the rooftop as a place to grow food. In dense neighborhoods where ground-level land is expensive or simply unavailable, flat roofs offer thousands of square meters of unused space that receives full sunlight for most of the day. Rooftop plantings also insulate the buildings beneath them. Urban planners are beginning to write rooftop agriculture into building codes. Several cities now offer tax relief or faster permits to developers who include green roofs in new construction, and a handful require them on large commercial buildings. Most experts land somewhere in the middle.

- **Words:** 499 → 98 words
- **Readability (Flesch):** 46.5 → 52.1 (Fairly difficult)
- **Grade Level:** Grade 12.2 → Grade 10.0
- **Engine:** `sshleifer/distilbart-cnn-12-6 (Extractive fallback)`

### T5 Small (T5-SMALL) · Short (~94.2% reduction)

> Cities around the world are rediscovering the rooftop as a place to grow food. Rooftop plantings also insulate the buildings beneath them. Most experts land somewhere in the middle.

- **Words:** 499 → 29 words
- **Readability (Flesch):** 46.5 → 59.9 (Fairly difficult)
- **Grade Level:** Grade 12.2 → Grade 7.3
- **Engine:** `t5-small (Extractive fallback)`

### T5 Small (T5-SMALL) · Medium (~80.4% reduction)

> Cities around the world are rediscovering the rooftop as a place to grow food. In dense neighborhoods where ground-level land is expensive or simply unavailable, flat roofs offer thousands of square meters of unused space that receives full sunlight for most of the day. Rooftop plantings also insulate the buildings beneath them. Urban planners are beginning to write rooftop agriculture into building codes. Several cities now offer tax relief or faster permits to developers who include green roofs in new construction, and a handful require them on large commercial buildings. Most experts land somewhere in the middle.

- **Words:** 499 → 98 words
- **Readability (Flesch):** 46.5 → 52.1 (Fairly difficult)
- **Grade Level:** Grade 12.2 → Grade 10.0
- **Engine:** `t5-small (Extractive fallback)`
