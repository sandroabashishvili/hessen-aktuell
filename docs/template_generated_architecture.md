# Template vs Generated Architecture

სტატუსი: `active`
განახლდა: `2026-06-22`

ეს დოკი აფიქსირებს `Hessen Aktuell`-ის მთავარ წესს: public HTML გვერდები უნდა აშენდეს pipeline/builders-ით. ხელით არ უნდა ვასწოროთ generated output, რადგან შემდეგი build იმ ცვლილებას მაინც გადაწერს.

## მთავარი წესი

ხელით ვცვლით:
- source registry-ს
- adapters-ს
- builders-ს
- shared HTML helpers-ს
- shared CSS/JS/assets-ს
- docs-ს

ხელით არ ვცვლით:
- root generated homepage-ს
- generated city pages-ს
- generated topic pages-ს
- generated archive pages-ს
- generated daily JSON-ს
- generated diagnostics reports-ს
- generated `sitemap.xml` / `robots.txt` files-ს

## Generated Public Pages

ეს გვერდები `python3 -m shared.py.news_pipeline` ბრძანებით შენდება:

- `/index.html`
- `/archive/index.html`
- `/archive/YYYY-MM-DD/index.html`
- `/cities/index.html`
- `/cities/kassel/index.html`
- `/cities/frankfurt/index.html`
- `/cities/wiesbaden/index.html`
- `/cities/darmstadt/index.html`
- `/topics/index.html`
- `/topics/politics/index.html`
- `/topics/transport/index.html`
- `/topics/police/index.html`
- `/topics/economy/index.html`
- `/topics/events/index.html`
- `/topics/safety/index.html`
- `/sitemap.xml`
- `/robots.txt`

## Static Pages

ამ ეტაპზე static public page არის:

- `/about/index.html`

ეს გვერდი ჯერ არ გვექარება. თუ მოგვიანებით ხშირად შეიცვლება ან source transparency/dashboard logic დასჭირდება, გადავა `AboutPageBuilder`-ზე.

## Builders

Public HTML-ს აშენებს ეს layer:

- `shared/py/news_pipeline/index_builder.py` -> Home
- `shared/py/news_pipeline/archive_builder.py` -> Archive index + daily archive
- `shared/py/news_pipeline/city_builder.py` -> Cities index + city pages
- `shared/py/news_pipeline/topic_builder.py` -> Topics index + topic pages
- `shared/py/news_pipeline/html.py` -> shared nav, favicon, brand mark, story cards, image helpers

## Data Flow

Pipeline flow:

1. `source_registry.json` აღწერს whitelist official sources-ს.
2. `sources.py` კითხულობს registry-ს.
3. `collector.py` ყველა source-ს აგროვებს.
4. `adapters.py` source-specific parser-ებს იყენებს.
5. `orchestrator.py` წერს daily JSON-ს და builders-ს უშვებს.
6. builders წერენ public HTML-ს.
7. `sitemap_builder.py` წერს `sitemap.xml` და `robots.txt`.
8. `python3 -m shared.py.diagnostics` ამოწმებს source links-ს, freshness-ს, internal links-ს, sitemap coverage-ს და content balance-ს.

## Change Rules

თუ ტექსტი/HTML structure არ მოგწონს generated გვერდზე:
- არ ვასწორებთ პირდაპირ `index.html` output-ს.
- ვპოულობთ შესაბამის builder-ს.
- ვასწორებთ render function-ს ან shared helper-ს.
- თავიდან ვუშვებთ `python3 -m shared.py.news_pipeline`.
- ბოლოს ვუშვებთ `python3 -m shared.py.diagnostics`.

თუ public hosting URL შეიცვალა:
- local build-ზე default არის `http://localhost:8090`.
- publish build-ზე ვიყენებთ `HESSEN_AKTUELL_BASE_URL`.
- მაგალითად: `HESSEN_AKTUELL_BASE_URL="https://example.com" python3 -m shared.py.news_pipeline`.

თუ წყარო არასწორად იკითხება:
- ვამოწმებთ `source_registry.json` URL-ს.
- ვამოწმებთ შესაბამის adapter-ს.
- ვამოწმებთ diagnostics report-ს.
- საჭიროების შემთხვევაში ვცვლით endpoint/parser-ს.

თუ დიზაინის საერთო ელემენტი არასწორია:
- ვასწორებთ `shared/css/` ან `shared/py/news_pipeline/html.py`-ში.
- არ ვაკოპირებთ CSS-ს ცალკეულ generated pages-ში.

## Current Boundary

Generated output არის deployable/public result.
Source of truth არის builders/config/shared layer.

ამით მომავალში აღარ უნდა აგვერიოს, რომელი ფაილი არის სამუშაო კოდი და რომელი არის build result.
