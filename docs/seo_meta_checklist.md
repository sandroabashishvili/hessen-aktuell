# SEO / Meta Checklist

სტატუსი: `active`
განახლდა: `2026-06-22`

ეს დოკი აფიქსირებს მინიმალურ SEO/meta წესებს `Hessen Aktuell`-ისთვის. მიზანი არ არის ზედმეტი SEO fantasy; მიზანია, რომ public static pages ტექნიკურად სუფთა, ინდექსირებადი და თანმიმდევრული იყოს.

## Required Head Fields

ყველა public HTML გვერდს უნდა ჰქონდეს:

- `<title>`
- `<meta name="description">`
- `<link rel="canonical">`
- `og:type`
- `og:site_name`
- `og:title`
- `og:description`
- `og:url`
- `twitter:card`
- `twitter:title`
- `twitter:description`
- favicon links
- shared CSS link

Generated pages ამას იღებენ shared helper-იდან:

- `shared/py/news_pipeline/html.py`
- function: `head_meta(...)`

Static `about/index.html` იგივე წესს ხელით მიყვება, რადგან About page ჯერ builder-ზე არ გადაგვყავს.

## Canonical Rules

ამ ეტაპზე canonical path არის root-relative:

- `/`
- `/cities/`
- `/cities/kassel/`
- `/topics/police/`
- `/archive/2026-06-22/`

როცა public domain გადაწყდება, sitemap base URL შეიცვლება `HESSEN_AKTUELL_BASE_URL`-ით. Canonical-ების absolute URL-ზე გადაყვანა მოგვიანებით შეიძლება, მაგრამ route consistency უკვე დაცულია.

## Sitemap Rules

Pipeline ყოველთვის წერს:

- `sitemap.xml`
- `robots.txt`

local default:

```bash
python3 -m shared.py.news_pipeline
```

public build:

```bash
HESSEN_AKTUELL_BASE_URL="https://example.com" python3 -m shared.py.news_pipeline
```

GitHub/hosting publish-მდე sitemap-ში `localhost` არ უნდა დარჩეს.

## Diagnostics

SEO/meta coverage მოწმდება:

```bash
python3 -m shared.py.diagnostics
```

Diagnostics ამოწმებს:

- source links
- source freshness
- internal links
- sitemap/robots coverage
- SEO head fields
- content balance

სრული JSON საჭიროებისას:

```bash
python3 -m shared.py.diagnostics --json
```

## Content Rules

- title მოკლე და route-specific უნდა იყოს
- description უნდა აღწერდეს გვერდს, არა ზოგად marketing ტექსტს
- story cards source URL-ზე გადადის და source attribution ჩანს
- full external article text არ იკოპირება
- generated local visuals გამოიყენება იქ, სადაც source image rights ჯერ არ არის გადაწყვეტილი

## Next SEO Steps

შემდეგი ეტაპები:

1. public domain/hosting URL-ის გადაწყვეტა
2. canonical absolute URL policy
3. Open Graph image policy
4. JSON-LD structured data მხოლოდ მაშინ, როცა content model სტაბილურია
5. archive retention policy, რომ sitemap უსასრულოდ არ გაიბეროს
