# Source Policy

სტატუსი: `აქტიური draft`
განახლდა: `2026-04-04`

## მთავარი პრინციპი

ამ პროექტში source strategy თავიდანვე უნდა იყოს conservative.

ანუ:
- საჯარო წყაროების გამოყენება შეიძლება
- მაგრამ external publisher content-ის უსაფუძვლო კოპირება არ შეიძლება
- სადაც uncertainty-ია, იქ უნდა ვიმუშაოთ `headline + summary + link-out` პრინციპით

ეს დოკი არის operational policy,
არა ოფიციალური იურიდიული დასკვნა.

## პრიორიტეტული source families

პირველი არჩევანი:
- official city / regional press pages
- official public-service updates
- official emergency / police press pages
- official tourism / civic information pages

Hessen მიმართულებისთვის საწყისი candidate source families:
- Stadt Kassel `Aktuelles`
  - https://www.kassel.de/aktuelles/index.php
- Landkreis Kassel `Pressemitteilungen`
  - https://www.landkreiskassel.de/pressemitteilungen/index.php
  - გვერდზე მითითებულია RSS feed availability
- Polizei Nordhessen press/public information
  - https://www.polizei.hessen.de/polizeipraesidien/polizeipraesidium-nordhessen/presse-und-oeffentlichkeitsarbeit

## რისი განთავსება გვინდა

უსაფრთხო operational მიმართულება:
- own headline style
- მოკლე own summary
- source attribution
- original link
- publication date
- category + tags

## რისი თავიდან აცილება გვინდა

- სრული სტატიის უხეში კოპირება commercial publishers-იდან
- paywalled/publication text-ის mirror-ად გადაქცევა
- source attribution-ის გარეშე განთავსება
- გაურკვეველი licensing-ის მქონე სურათების თავისუფალი ატვირთვა

## minimum attribution rule

თუ ჩანაწერი external source-ზეა დაფუძნებული, მინიმუმ უნდა ჩანდეს:
- source name
- source URL
- original publish date თუ ხელმისაწვდომია
- ჩვენი summary და არა სრული კოპირებული ტექსტი

## image policy draft

MVP-სთვის:
- source images არ უნდა ჩაითვალოს ავტომატურად უსაფრთხოდ
- default mode არის local visual / placeholder
- YouTube embed შეიძლება official/public channel-ებიდან, როცა embed დაშვებულია
- source image გამოიყენება მხოლოდ მაშინ, როცა registry-ში `image_download_allowed=true`
- clearly reusable/official asset შეიძლება დაემატოს allowlist-ით
- generated/local topic images are allowed as safe default visuals
- generated visuals must not contain source logos, readable publisher marks, identifiable people, or misleading event-specific details

## automation rule

როცა pipeline მოგვიტანს news item-ს, სისტემამ უნდა იცოდეს:
- source family
- source URL
- raw title
- raw date
- summary status
- image rights status

თუ rights status უცნობია:
- item შეიძლება გამოჩნდეს text-only რეჟიმში

## რაც უნდა გადავამოწმოთ კოდის დაწერისას

- source whitelist არსებობს თუ არა
- თითო connector/source-ს attribution field აქვს თუ არა
- full-text copying ხომ არ ხდება
- image download default-on ხომ არ არის დაუფიქრებლად
- archive გვერდზე source link ჩანს თუ არა
- media policy ველები ინახება თუ არა:
  - `media_type`
  - `media_source`
  - `media_rights_status`
  - `image_download_allowed`
  - `youtube_embed_allowed`
