# Current Status

სტატუსი: `source adapter MVP`
განახლდა: `2026-06-26`

## სად ვართ ახლა

`Hessen Aktuell` direction ფაზიდან working prototype ფაზაში გადავიდა.

ამ ეტაპზე დაფიქსირებულია:
- მიმართულება: `Hessen`
- source policy საჭიროა conservative ფორმით
- portal volume მიზანი მაღალია
- categories და build rules დალაგებულია
- page map დალაგებულია
- folder scaffold უკვე არსებობს
- homepage-ის პირველი static prototype უკვე დგას
- შიდა გვერდებიც static structure-ზეა გადაყვანილი
- shared nav ახლა ყველა გვერდზე ერთნაირია
- `Cities` და `Topics` landing pages დაემატა
- page-family folders დაემატა
- shared layer უკვე ცალკეა გამოტანილი
- source-aware MVP news pipeline დაემატა
- homepage და daily archive უკვე შეიძლება გენერირდეს whitelist source entries-იდან
- `Stadt Kassel Aktuelles` HTML adapter უკვე იღებს მინიმალურ რეალურ fields-ს Pressemitteilungen სექციიდან
- `Landkreis Kassel Pressemitteilungen` HTML adapter უკვე იღებს მინიმალურ რეალურ fields-ს search result teaser list-იდან
- `Polizei Nordhessen` HTML adapter უკვე იღებს filtered official Meldungen list-ს Nordhessen-ისთვის
- city pages უკვე generated news stream-ს იყენებს და აღარ არის ცარიელი scaffold
- `cities/index.html` უკვე pipeline-ით გენერირდება, როგორც `topics/index.html`
- Frankfurt, Wiesbaden და Darmstadt უკვე რეალურ source items-ს აჩვენებს, არა მხოლოდ fallback card-ს
- Frankfurt უკვე სამი source group-ით ივსება: `Polizei Frankfurt Presse`, `VGF Frankfurt News` და `Mainova Frankfurt Presse`
- diagnostics output ახლა terminal-ში მოკლე ადამიანურ summary-ს აჩვენებს და JSON report-საც ინახავს
- source freshness age ახლა `notice`-ად ითვლება და არა failure/warning-ად, თუ parser items-ს სწორად აბრუნებს
- homepage layout tightened: lead/latest news now share one left column, and the right dashboard now focuses only on city/topic navigation
- homepage city/topic navigation counts now use accumulated unique items from `shared/data/news`, not only the current daily source pull
- public page copy cleanup completed: archive/about/home/city/topic pages now avoid developer-facing MVP, pipeline, source-monitor, and generated-flow wording
- static About page finalized and intentionally kept static
- sitemap/robots generation added to the news pipeline
- public UI copy German pass completed across generated home/city/topic/archive pages and static About page
- archive index cards now include generated local image banners
- archive retention added: daily JSON files and generated daily archive folders keep the latest 10 archive days
- `/service/` page added with trusted service links for official warnings, administration, police, health, transport, work, family, education, and integration
- homepage service teaser added in the former empty right-side panel

## რა გავაკეთეთ უკვე

- idea folder აღარ არის უბრალოდ placeholder
- project direction ჩაიწერა:
  - [project_brief.md](/home/sandro/portfolio_projects/hessen_aktuell/docs/project_brief.md)
- source/legal-safe operating rules ჩაიწერა:
  - [source_policy.md](/home/sandro/portfolio_projects/hessen_aktuell/docs/source_policy.md)
- source adapter contract ჩაიწერა:
  - [source_adapter_contract.md](/home/sandro/portfolio_projects/hessen_aktuell/docs/source_adapter_contract.md)
- category/taxonomy draft ჩაიწერა:
  - [editorial_taxonomy.md](/home/sandro/portfolio_projects/hessen_aktuell/docs/editorial_taxonomy.md)
- page structure draft ჩაიწერა:
  - [page_map.md](/home/sandro/portfolio_projects/hessen_aktuell/docs/page_map.md)
- doc/code rules ჩაიწერა:
  - [build_rules.md](/home/sandro/portfolio_projects/hessen_aktuell/docs/build_rules.md)
- template vs generated architecture ჩაიწერა:
  - [template_generated_architecture.md](/home/sandro/portfolio_projects/hessen_aktuell/docs/template_generated_architecture.md)
- SEO/meta checklist ჩაიწერა:
  - [seo_meta_checklist.md](/home/sandro/portfolio_projects/hessen_aktuell/docs/seo_meta_checklist.md)
- physical scaffold შეიქმნა:
  - [index.html](/home/sandro/portfolio_projects/hessen_aktuell/index.html)
  - [cities](/home/sandro/portfolio_projects/hessen_aktuell/cities)
  - [topics](/home/sandro/portfolio_projects/hessen_aktuell/topics)
  - [archive](/home/sandro/portfolio_projects/hessen_aktuell/archive)
  - [about](/home/sandro/portfolio_projects/hessen_aktuell/about)
  - [shared](/home/sandro/portfolio_projects/hessen_aktuell/shared)
- homepage static prototype დაიდგა:
  - [index.html](/home/sandro/portfolio_projects/hessen_aktuell/index.html)
  - [styles.css](/home/sandro/portfolio_projects/hessen_aktuell/shared/css/styles.css)
- index routes დაემატა:
  - [cities/index.html](/home/sandro/portfolio_projects/hessen_aktuell/cities/index.html)
  - [topics/index.html](/home/sandro/portfolio_projects/hessen_aktuell/topics/index.html)
- navigation alignment გაკეთდა:
  - top nav ყველა გვერდზე ერთნაირია
  - `Cities` და `Topics` dropdown-ით იხსნება
- static vs dynamic boundary გამკაცრდა:
  - stable blocks დარჩა
  - დროებითი fake headlines მოვხსენით
- source-aware generation დაემატა:
  - [shared/py/news_pipeline](/home/sandro/portfolio_projects/hessen_aktuell/shared/py/news_pipeline)
  - [shared/data/news](/home/sandro/portfolio_projects/hessen_aktuell/shared/data/news)
  - [shared/data/source_registry.json](/home/sandro/portfolio_projects/hessen_aktuell/shared/data/source_registry.json)
  - [archive/2026-06-19](/home/sandro/portfolio_projects/hessen_aktuell/archive/2026-06-19)
  - command: `python3 -m shared.py.news_pipeline`
- first real adapter დაემატა:
  - source: `stadt-kassel-aktuelles`
  - method: official HTML parser
  - reads: title, original URL, date, category
  - summary: generated short own summary
  - images: local visual placeholder
- second real adapter დაემატა:
  - source: `landkreis-kassel-presse`
  - method: official RSS parser with HTML fallback
  - reads: title, original URL, date, category
  - skips media/download teaser entries
  - RSS media/download entries are filtered out
  - summary: generated short own summary
  - images: local visual placeholder
- third real adapter დაემატა:
  - source: `polizei-nordhessen-presse`
  - method: official HTML parser
  - reads: title, original URL, date
  - source URL uses official Nordhessen filter `tid1[3343]`
  - summary: generated short own summary
  - images: local visual placeholder
- Frankfurt real adapter დაემატა:
  - source: `polizei-frankfurt-presse`
  - method: RSS parser
  - reads: title, original URL, date, description
  - source URL: verified `Polizei Frankfurt Presse`
- Frankfurt transport/news adapter დაემატა:
  - source: `vgf-frankfurt-news`
  - method: official HTML parser
  - reads: title, original URL, date, description
  - source URL: verified `VGF Frankfurt News`
- Frankfurt energy/economy adapter დაემატა:
  - source: `mainova-frankfurt-presse`
  - method: official HTML parser
  - reads: title, original URL, date, description
  - replaces Fraport traffic/statistics items with more useful Frankfurt infrastructure/economy items
  - source URL: verified `Mainova Frankfurt Presse`
- Hessen-wide economy/transport adapter დაემატა:
  - source: `hessen-economy-transport-presse`
  - method: official Hessen Drupal HTML parser
  - reads: title, original URL, date, dateline, description
  - replaces the old manual `RMV` fallback source
  - source URL: verified `wirtschaft.hessen.de/presse`
- Hessen-wide government adapter დაემატა:
  - source: `hessen-government-presse`
  - method: official Hessen Drupal HTML parser
  - reads: title, original URL, date, dateline, description
  - replaces the old manual `Hessen Tourismus` fallback source
  - source URL: verified `hessen.de/presse`
- Wiesbaden real adapter დაემატა:
  - source: `stadt-wiesbaden-presse`
  - method: RSS parser
  - reads: title, original URL, date, description
  - source URL: verified `Landeshauptstadt Wiesbaden Pressemitteilungen`
- Wiesbaden police/safety adapter დაემატა:
  - source: `polizei-wiesbaden-presse`
  - method: Presseportal city RSS parser
  - reads: title, original URL, date, description
- Darmstadt real adapter დაემატა:
  - source: `stadt-darmstadt-presse`
  - method: official HTML parser
  - reads: title, original URL, date, description
- Darmstadt police/safety adapter დაემატა:
  - source: `polizei-darmstadt-presse`
  - method: Presseportal city RSS parser
  - reads: title, original URL, date, description
- Kassel city page generation დაემატა:
  - source: generated item stream
  - output: `cities/kassel/index.html`
- multi-city generation დაემატა:
  - `CityPageBuilder` ახლა ყველა registry city-სთვის აშენებს generated page-ს
  - `cities/index.html` ავტომატურად შენდება current city counts-ით, latest topic-ით და route-card image strip-ებით
  - `cities/frankfurt/`, `cities/darmstadt/`, `cities/wiesbaden/` scaffold აღარ არის ცალკე ხელით შესანახი template
  - Frankfurt municipal press page returned a Cloudflare challenge to headless fetch, so Frankfurt fallback now uses a verified `Polizei Frankfurt Presse` source
  - Frankfurt transport/public-service coverage now uses `VGF Frankfurt News`
  - Frankfurt energy/economy coverage now uses `Mainova Frankfurt Presse`
  - Wiesbaden and Darmstadt source fallback URLs were corrected after 404 checks
  - Wiesbaden and Darmstadt now each have municipal + police source groups
- media policy MVP დაემატა:
  - card visual slot
  - local visual placeholders
  - source image download default-off
  - YouTube embed permission field
  - source images are still disabled until image rights and attribution handling is implemented
  - AI-generated topic visual pool დაემატა:
    - `Police`, `Transport`, `Politics`, `Events`, `Economy`, `Safety`
    - files: `shared/assets/news/topics/*-01.png` through `*-04.png`
    - each topic currently has 4 generated local image variants
    - story cards now render generated local images instead of CSS-only placeholders
    - story feeds now rotate topic images sequentially inside each generated page, so repeated Police/Politics/etc. posts use `01`, `02`, `03`, `04` in order instead of frequently repeating one hash-selected image
    - route cards still use deterministic city/topic visual mapping where needed
    - duplicate-looking assets were replaced for `police-04`, `politics-03`, `politics-04`, and `safety-02`
- Home feed cleanup დაემატა:
  - homepage აღარ იღებს პირველივე registry source items-ს ბრმად
  - Home-ზე city-balanced selection გამოიყენება, რომ Kassel/Frankfurt/Wiesbaden/Darmstadt ერთად გამოჩნდეს
  - Home right-side city/topic counts use stored daily JSON history with `item_id` dedupe, so repeated stories across daily builds are counted once
  - story cards now show `published_date`
  - RSS date fallback fixed, so Presseportal items no longer store empty dates
  - news item IDs are now stable by `source_id + source URL slug`, so fallback date changes do not make the same source story look like a new item
- Topic pages generated stream-ზე გადავიდა:
  - `topics/index.html` ახლა current item counts-ს აჩვენებს
  - `topics/politics/`, `topics/transport/`, `topics/police/`, `topics/economy/`, `topics/events/`, `topics/safety/` ავტომატურად შენდება
  - topic pages use the same story card, date, generated image, and source attribution layer as city/archive pages
  - `cities/index.html` და `topics/index.html` ორივე იყენებს generated topic image layer-ს landing cards-ზეც
  - `cities/index.html` now uses fixed city visual mapping, so Kassel/Frankfurt/Darmstadt/Wiesbaden keep distinct route-card images
- Old archive scaffold removed:
  - old example day/month archive scaffold removed
  - current generated daily archives remain
- Article scaffold removed:
  - article detail pages are not part of the current public MVP
  - story cards link out to original sources instead
- Old standalone `home/` scaffold removed:
  - homepage is served by root [index.html](/home/sandro/portfolio_projects/hessen_aktuell/index.html)
- visual consistency pass დაემატა:
  - generated pages now include shared `favicon.svg`
  - generated headers now include a small `HA` brand mark
  - story card text spacing and visual placeholder sizing are controlled in shared CSS
  - homepage lead/latest news panels now use one shared left-column width
  - homepage right rail now uses a compact navigation dashboard for Cities and Topics only
  - homepage right rail count source is accumulated unique history from `shared/data/news`
  - story cards now show only reader-facing meta: date and source name
  - archive index now lists available daily archive pages with counts instead of technical route/pipeline notes
  - `/service/` is generated by the news pipeline
  - shared navigation now includes `Service`
  - homepage right-side service panel links into the full service page
- diagnostics layer დაემატა:
  - command: `python3 -m shared.py.diagnostics`
  - checks source registry URLs
  - checks source adapter freshness: parsed item count, latest parsed date, manual/fallback sources
  - checks generated/static internal HTML links
  - checks sitemap/robots coverage
  - checks SEO/meta head fields
  - checks content balance: city/topic/source distribution, top city, top source
  - terminal output now includes readable summary before the JSON block
  - writes report to `shared/data/diagnostics/`
  - latest verified source links: `12 source URLs ok / 0 broken`
  - latest verified internal links: `1135 ok / 0 broken`
  - latest sitemap check: `24 URLs / 0 missing / robots ok`
  - latest SEO/meta check: `168 ok / 0 missing`
  - latest generated news count: `55`
  - latest content balance: `OK`, top city `Frankfurt=15`, top source `Landkreis Kassel Pressemitteilungen=5`
  - latest freshness audit: `12 ok / 3 notice / 0 warning / 0 empty`
  - freshness notices are not broken-source warnings; these sources return valid items but their latest public item is older than build day:
    - `polizei-nordhessen-presse`: latest `2026-06-15` (`8d`)
    - `mainova-frankfurt-presse`: latest `2026-06-16` (`7d`)
    - `hessen-economy-transport-presse`: latest `2026-06-19` (`4d`)
  - latest overall diagnostics status: `ok`
- structure pass დაიწყო:
  - [shared/css/styles.css](/home/sandro/portfolio_projects/hessen_aktuell/shared/css/styles.css)
  - [shared/js/main.js](/home/sandro/portfolio_projects/hessen_aktuell/shared/js/main.js)
  - [shared/data/site_map.json](/home/sandro/portfolio_projects/hessen_aktuell/shared/data/site_map.json)

## რას ველოდებით

პირველი პრაქტიკული შედეგი მიღებულია:
- shared layout rules გამკაცრდა
- page-family consistency დალაგდა
- Frankfurt, Wiesbaden და Darmstadt real source adapters დაემატა
- Frankfurt item count is built from 3 source groups without Fraport traffic-statistics archive items
- Hessen-wide government and economy/transport source adapters დაემატა
- source link diagnostics დაემატა
- cities/topics landing pages now show generated image strips
  - topic image pool increased from 3 to 4 generated variants per topic
  - latest generated image usage audit: `24/24` topic images appear across generated pages
  - story feed image selection now rotates per topic within the page, reducing repeated adjacent visuals
- content balance diagnostics დაემატა
- template vs generated architecture doc დაემატა
- homepage functional compact blocks დაემატა
- sitemap/robots generation and diagnostics დაემატა
- About page static final pass გაკეთდა
- SEO/meta checklist and diagnostics დაემატა

## რა არის შემდეგი 5 ნაბიჯი

1. source diagnostics report-ის HTML page, თუ terminal/JSON აღარ იქნება საკმარისი
2. optional source replacement, თუ რომელიმე official source დიდხანს აღარ განახლდება
3. public hosting URL decision, so sitemap can be generated with final base URL
4. Open Graph image policy, როცა real/public visual strategy გადაწყდება
5. topic/city image variants further expansion, თუ გვერდიგვერდ გამეორება ისევ თვალში მოხვდება

## ახლო პრიორიტეტი

ყველაზე სწორი შემდეგი ნაბიჯი არის:
- source diagnostics report-ის HTML page, თუ terminal/JSON აღარ იქნება საკმარისი

page structure უკვე დაფიქსირდა.
ფოლდერის scaffold მზადაა.
prototype უკვე დგას და source-watch MVP pipeline მუშაობს.
ყველა 12 configured source-ს ახლა real adapter აქვს.
Frankfurt აღარ არის police-only.
diagnostics report უკვე ამოწმებს source registry-ს, freshness-ს, content balance-ს და შიდა HTML links-ს.
freshness notice-ები შემოწმებულია: parser-ები სწორ official list-ს კითხულობენ; ამ ეტაპზე ეს არ არის blocking issue.
topic visual pool უკვე 4 generated ვარიანტამდე გაიზარდა თითო თემაზე.
