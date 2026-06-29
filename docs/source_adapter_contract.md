# Source Adapter Contract

სტატუსი: `active MVP`
განახლდა: `2026-06-20`

ეს დოკი აღწერს როგორ უნდა შემოვიდეს რეალური source data `Hessen Aktuell` pipeline-ში.

## მიზანი

Adapter იღებს მხოლოდ მინიმალურ, უსაფრთხო ველებს:
- title
- original URL
- publish date
- source name
- source family
- city
- topic/category

Adapter არ აკოპირებს სრულ სტატიას.

## Required Output

ყველა adapter აბრუნებს `NewsItem` ჩანაწერებს შემდეგი პრინციპით:
- `title` მოდის source-იდან
- `source_url` არის original article/detail URL
- `published_date` ნორმალიზებულია ISO ფორმატში
- `summary` არის მოკლე own summary
- `summary_status` აჩვენებს მეთოდს
- `media_type` default არის `placeholder`
- `image_download_allowed` მოდის `source_registry.json`-იდან

## Fail-Safe Rule

თუ source fetch ან parse ვერ შესრულდა:
- pipeline არ უნდა ჩავარდეს
- source გადადის `source_watch_fallback` ჩანაწერზე
- homepage/archive მაინც გენერირდება

## Current Adapters

### stadt-kassel-aktuelles

Method: `official HTML parser`

Reads from:
- `https://www.kassel.de/aktuelles/index.php`

Section:
- `Pressemitteilungen`

Fields:
- title
- href/original URL
- datetime/date
- source category

Current media:
- local visual placeholder
- source image download disabled

### landkreis-kassel-presse

Method: `official HTML parser`

Reads from:
- `https://www.landkreiskassel.de/pressemitteilungen/index.php`

Section:
- `Aktuelles aus dem Landkreis Kassel`

Fields:
- title
- href/original URL
- datetime/date
- source category

Filtering:
- accepts only `Pressemitteilung` teaser entries
- ignores media/download teaser entries

Current media:
- local visual placeholder
- source image download disabled

### polizei-nordhessen-presse

Method: `official HTML parser`

Reads from:
- `https://www.polizei.hessen.de/meldungen?tid1%5B3343%5D=3343`

Section:
- filtered `Meldungen` list for `Polizeipräsidium Nordhessen`

Fields:
- title
- href/original URL
- visible date
- source dateline is ignored for stable source naming

Filtering:
- source URL uses the official Nordhessen filter ID `3343`
- adapter reads only teaser-list entries

Current media:
- local visual placeholder
- source image download disabled

## Next Adapter Candidates

1. `hessen.de-presse`
2. `rmv-meldungen`
3. additional official city sources for Wiesbaden/Darmstadt

Next adapter should follow the same fail-safe shape before adding image or video handling.
