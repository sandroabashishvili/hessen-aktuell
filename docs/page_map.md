# Page Map

სტატუსი: `active MVP`
განახლდა: `2026-06-20`

ეს დოკი აღწერს `Hessen Aktuell`-ის მიმდინარე public page structure-ს.

## Top Navigation

ბრაუზერში top nav-ში ჩანს:
1. `Home`
2. `Cities`
3. `Topics`
4. `Archive`
5. `About`

`Article` navigation-იდან ამოღებულია. ცალკე article pages ჯერ არ არის public layer, რადგან source rewrite/copyright policy ბოლომდე არ არის გადაწყვეტილი.

## Page Types

მიმდინარე page types:
1. `Home`
2. `Cities index`
3. `City page`
4. `Topics index`
5. `Topic page`
6. `Archive page`
7. `About`

## 1. Home

URL:
- `/`

აჩვენებს:
- city-balanced lead/latest feed
- source-aware cards
- generated topic visuals
- city/topic/archive shortcuts

## 2. Cities Index

URL:
- `/cities/`

აჩვენებს:
- Kassel
- Frankfurt
- Darmstadt
- Wiesbaden

## 3. City Pages

URLs:
- `/cities/kassel/`
- `/cities/frankfurt/`
- `/cities/darmstadt/`
- `/cities/wiesbaden/`

აჩვენებს:
- city lead item
- city story stream
- source attribution
- date
- generated local image
- original source link

## 4. Topics Index

URL:
- `/topics/`

აჩვენებს:
- Politics
- Transport
- Police
- Economy
- Events
- Safety
- current item count per topic

## 5. Topic Pages

URLs:
- `/topics/politics/`
- `/topics/transport/`
- `/topics/police/`
- `/topics/economy/`
- `/topics/events/`
- `/topics/safety/`

აჩვენებს:
- topic lead item
- topic story stream
- city mix
- source attribution
- date
- generated local image
- original source link

## 6. Archive

URLs:
- `/archive/`
- `/archive/YYYY-MM-DD/`

აჩვენებს:
- latest daily archive entry point
- day-level source-aware story stream
- city/topic summary

ძველი scaffold archive routes ამოღებულია.

## 7. About

URL:
- `/about/`

აჩვენებს:
- project purpose
- source handling direction
- publishing boundaries

## Internal Flow

სწორი flow:
- Home -> Cities
- Home -> Topics
- Home -> City
- Home -> Topic
- Home -> Archive
- Cities -> City
- Topics -> Topic
- City -> Archive
- Topic -> Archive
- ყველა მთავარ გვერდზე -> About
