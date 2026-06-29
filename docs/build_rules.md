# Build Rules

სტატუსი: `აქტიური ცნობარი`
განახლდა: `2026-06-22`

## დოკების წერის წესები

- direction უნდა იყოს მკაფიო და ვიწრო
- ჯერ truth ვწერთ, მერე სურვილებს
- source policy მკაფიოდ უნდა განვასხვავოთ category ideas-ისგან
- `MVP`, `next`, `later` ერთმანეთში არ უნდა აირიოს
- legal-sensitive საკითხებში უნდა ვიყოთ conservative
- დოკი არ უნდა გვპირდებოდეს იმას, რასაც კოდი ჯერ არ აკეთებს

## კოდის წერის წესები

- static-first mindset სანამ სხვა რამე არ მოგვინდა
- page map წინასწარ უნდა იყოს ცნობილი
- source adapter logic და presentation logic ერთმანეთში არ უნდა აირიოს
- SEO/meta layer თავიდანვე უნდა ჩაითვალოს
- SEO/meta checklist აღწერილია:
  - [seo_meta_checklist.md](/home/sandro/portfolio_projects/hessen_aktuell/docs/seo_meta_checklist.md)
- archive flow homepage flow-სგან ცალკე პასუხისმგებლობად უნდა იყოს ნაფიქრი
- source attribution required field უნდა იყოს, არა optional nice-to-have
- generated homepage/archive/city pages ერთ news stream-ს უნდა ეყრდნობოდეს, რომ ცალკე static scaffold არ დარჩეს
- public generated HTML-ს ხელით არ ვასწორებთ; structure/design/content flow იცვლება builders/config/shared layer-ში
- template vs generated boundary აღწერილია:
  - [template_generated_architecture.md](/home/sandro/portfolio_projects/hessen_aktuell/docs/template_generated_architecture.md)

## diagnostics წესები

- ამ პროექტში link/source შემოწმებას ვეძახით `diagnostics`
- source registry URL-ები, შიდა HTML links, sitemap coverage და content balance ერთი ბრძანებით უნდა მოწმდებოდეს: `python3 -m shared.py.diagnostics`
- diagnostics report ინახება `shared/data/diagnostics/`
- sitemap/robots build pipeline-ის ნაწილია; diagnostics ამოწმებს, რომ sitemap coverage არ დაირღვეს
- SmartSignalHub-ის მძიმე tool structure პირდაპირ არ გადმოგვაქვს; აქ ვიღებთ მხოლოდ იმ იდეას, რაც პატარა static news project-ს სჭირდება

## sitemap / publish წესები

- `python3 -m shared.py.news_pipeline` ყოველთვის წერს `sitemap.xml` და `robots.txt`
- default local base URL არის `http://localhost:8090`
- public build-ზე base URL უნდა მივცეთ environment variable-ით:
  - `HESSEN_AKTUELL_BASE_URL="https://example.com" python3 -m shared.py.news_pipeline`
- GitHub/hosting-ზე ატვირთვამდე sitemap-ში `localhost` არ უნდა დარჩეს

## content ingestion წესები

- whitelist-based sources
- source family recorded
- raw title stored
- original URL stored
- date normalized
- category assigned
- no blind full-text copy
- source adapter უნდა fail-safe იყოს: თუ fetch/parse ვერ იმუშავა, source-watch fallback იწერება
- generated archive date რეგიონული პროექტისთვის `Europe/Berlin` დღით ითვლება
- adapter summary უნდა იყოს მოკლე own summary, არა source full-text copy
- story card description არ უნდა იყოს boilerplate; თუ source teaser/preview არ არის, paragraph საერთოდ არ იბეჭდება

## UI წესები

- news portal უნდა იყოს ცოცხალი, არა მკვდარი blog layout
- homepage hierarchy მკაფიო უნდა იყოს
- category rails უნდა იგრძნობოდეს
- archive navigation უნდა იყოს მარტივი
- article card pattern თავიდანვე ერთიანი უნდა იყოს

## რაზე ვაქცევთ ყურადღებას

დოკების დროს:
- legality
- source transparency
- information architecture
- realistic publishing volume

კოდის დროს:
- source boundaries
- archive correctness
- SEO consistency
- update automation readiness
- page performance

## რაც ჯერ არ უნდა ვაკეთოთ

- full CMS fantasy
- user accounts
- comments
- admin dashboard
- რთული search stack
- მრავალენოვანი სისტემა პირველივე ეტაპზე
