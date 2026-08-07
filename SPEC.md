# Spec: `andersmoldin/skills`

Mitt superset av Matt Pococks skills — hans uppsättning (delvis editerad av mig) plus mina egna,
distribuerat som ett publikt installerbart Claude Code-plugin på flera maskiner.

**Status:** beslutad, obyggd. Det här dokumentet är byggunderlaget. Det ska räcka för att jag, en
agent eller vem som helst ska kunna bygga uppsättningen **utan att fatta fler beslut**.

**Ursprung:** besluten fattades av en agent på uttryckligt uppdrag, natten till 2026-08-08, och
redovisas i ärendena [#5](../../issues/5)–[#10](../../issues/10). De är förslag som kaptenen kan
riva upp; tills dess gäller de.

**Språk:** allt publikt i det här repot skrivs på svenska. Undantag: namn i manifest måste vara
kebab-case (`a-z0-9-`), så åäö är uteslutet där.

---

## 1. Besluten i korthet

| Fråga | Beslut |
|---|---|
| Synkmodell (#5) | `git subtree` av `mattpocock/skills` till `vendor/matt/`, med **egen** `marketplace.json` och **egen** `plugin.json` i roten |
| Marketplace-namn (#6) | `moldin` |
| Plugin-namn (#6) | `moldin-skills` → skills heter `moldin-skills:wayfinder` osv. |
| Hans skill-namn (#6) | behålls oförändrade; bara prefixet byts |
| Separation (#7) | strukturell: allt under `vendor/matt/` är hans, allt annat är mitt |
| Uppdateringsrutin (#8) | `git subtree pull` vid hans releaser, ~månadsvis, manuell konfliktlösning |
| Licens (#9) | MIT; Matts copyright-rad står kvar, min läggs till |
| Migrering (#10) | avinstallera hans plugin först, installera mitt, per maskin; auto-update på |

---

## 2. Vald synkmodell (#5)

### Modellen

```
andersmoldin/skills
├── .claude-plugin/
│   ├── marketplace.json   ← min, en enda plugin-post: {"name": "moldin-skills", "source": "./"}
│   └── plugin.json        ← MIN, räknar upp alla skill-sökvägar (hans OCH mina)
├── vendor/matt/           ← git subtree av mattpocock/skills, hela hans repo
├── mina-skills/           ← mina egna skills
├── LICENSE                ← MIT, båda copyright-raderna
├── README.md
├── MINA-ANDRINGAR.md
└── SPEC.md
```

Ett plugin, en namnrymd. Pluginroten är repots rot, så min `plugin.json` i roten är
pluginmanifestet — och den pekar in i `vendor/matt/` för hans skills och i `mina-skills/` för mina.

### Varför just den här

**Det avgörande draget är att hans `plugin.json` degraderas från konfliktyta till changelog.**

`plugin.json` räknar upp alla 25 skill-sökvägar explicit och pekades i #4 ut som repots mest
konfliktbenägna fil: varje gång han lägger till, döper om eller flyttar en skill ändras den, och
varje gång jag lägger till en egen skill ändras den också. I en äkta fork är det *samma fil* — och
då konfliktar den i praktiken vid varje synk.

I den här modellen är min `plugin.json` en helt egen fil som uppström aldrig rör. Hans hamnar på
`vendor/matt/.claude-plugin/plugin.json`, där den ligger orörd och **ignoreras av Claude Code**
(den är inte pluginrot). Den mergas därför alltid rent — och blir i stället precis det jag behöver:
en läsbar diff som talar om exakt vilka skills han lagt till, döpt om eller tagit bort sedan sist.
Den farligaste filen blir den mest användbara.

**Konfliktytan blir exakt så stor som jag själv gör den.** Git mergar bara filer där båda sidor
ändrat. Har jag översatt tre SKILL.md är det de tre filerna som är exponerade; de övriga ~98 flyter
in gratis. Det gör kostnaden proportionell mot hur mycket jag faktiskt editerar, inte mot hur
mycket han skriver.

**Namnbytesdetektering behålls.** `git subtree pull` *är* en riktig git-merge (bara förskjuten in i
ett prefix), så en omdöpt fil jag editerat följer med till sitt nya namn, och en raderad fil jag
editerat ger en explicit *delete/modify*-konflikt som git vägrar gissa sig förbi. Det är den
egenskapen som skiljer merge-baserade modeller från kopieringsbaserade, och den är viktigare än den
låter: uppström rör sig snabbt (se §10), och den dyra felmoden är **tyst drift**, inte högljudda
konflikter.

**Strukturell separation på köpet.** Gränsen mellan hans och mitt är en katalog, inte en
överenskommelse. Det besvarar #7 nästan gratis, och det gör att mina egna skills per konstruktion
aldrig kan konflikta.

**Hans repo-rot hamnar inte i min rot.** I en fork blir hans `README.md`, `CLAUDE.md`,
`package.json` och `.github/workflows/` *mina* rotfiler. Här hamnar de under `vendor/matt/`, där de
är inerta — GitHub kör bara workflows som ligger i rotens `.github/workflows/`, så hans
release-pipeline startar aldrig i mitt repo.

### Avvägningarna jag accepterade

- **Jag måste själv underhålla `plugin.json`.** När Matt lägger till en skill dyker den *inte* upp
  automatiskt hos mig — jag måste addera sökvägen. Det är medvetet: priset för att slippa
  konflikter i den filen är att urvalet blir ett aktivt val varje gång. Rutinen i §7 gör steget
  omöjligt att glömma, men det är ett manuellt steg.
- **Längre kommandon.** `git subtree pull -P vendor/matt --squash …` är klumpigare än
  `git merge upstream/main`, och `-P` är obligatoriskt i alla underkommandon. Mildras av ett skript
  (§7), inte av modellen.
- **Konflikter försvinner inte.** Editerar jag en SKILL.md han också ändrar får jag en konflikt.
  Det är designen, inte en defekt — alternativen "löser" det genom att tyst välja en sida.
- **Repot bär hela hans repo, inte bara `skills/`.** `git subtree` kan inte filtrera. `docs/`,
  `.changeset/`, `scripts/`, `CHANGELOG.md` (44 kB) följer med. Det kostar diskutrymme och lite
  brus i sökningar, men **noll kontextfönster** — bara filer som är uppräknade i min `plugin.json`
  laddas som skills.
- **Ingen fork-relation på GitHub.** Jag syns inte i hans forkgraf och får ingen "Sync fork"-knapp.
  Knappen är ändå oanvändbar så fort man editerat (#4: den promptar en PR vid konflikt, och
  `gh repo sync --force` löser konflikten genom att kasta mina ändringar). Att inte vara en fork ger
  i gengäld synlighet i GitHub-sök, vilket en fork inte har som default.

### Alternativen jag valde bort

**Äkta GitHub-fork + merge.** Mekaniskt nästan lika bra — samma merge, samma
namnbytesdetektering. Bortvald på tre punkter: (1) hans `plugin.json` förblir *min* `plugin.json`
och konfliktar därmed vid varje synk där någon av oss rört skill-listan, vilket är nästan varje
synk; (2) hans rotfiler blir mina rotfiler, inklusive `.github/workflows/`; (3) forken är dold i
GitHub-sök som default, synligheten är låst till nätverket, och vägen ut ("Leave fork network") är
permanent och kostar issues, PR:er, stars och watchers. Punkt (1) är den tyngsta: den gör den
dyraste filen dyrast i onödan.

**Submodule.** Numera *tekniskt gångbart* — se §10, jag testade det och det fungerar, tvärtemot vad
frånvaron i dokumentationen antydde. Bortvald ändå, av en skäl som testet inte påverkar: **filerna
i en submodul tillhör hans repo och kan inte editeras av mig.** Att editera dem kräver en fork som
submodulmål, och då är forkproblemet tillbaka plus ett extra lager. Modellen svarar inte mot
uppgiften. Dessutom vilar den på odokumenterat beteende (§10) som kan regrediera utan förvarning.

**Ren vendorering via sync-script.** Bortvald för att skriptet saknar merge-bas: det kan inte skilja
"han ändrade" från "jag ändrade". Utfallen är att mina översättningar skrivs över tyst, eller
fryses tyst, eller att jag bygger en sämre `git merge` för hand. Ingen namnbytesdetektering.

**Patch/overlay.** Bortvald för att kravet är helt fel form för patchar: "skriv om en SKILL.md på
svenska" är en fullständig omskrivning, så patchen *är* hela filen och rejectar vid minsta
uppströmsändring. Overlay-varianten failar i stället tyst — samma frysning som ovan.

**Kombinerad modell (hans repo utpekat direkt + liten editerad yta).** Den mest lockande, och den
jag prövade hårdast — #5 bad uttryckligen om det. Den skulle se ut så här: en post med
`{"source": "github", "repo": "mattpocock/skills", "ref": "v1.2.3"}` bredvid en post
`{"source": "./mina-skills"}`. Synkproblemet upphör helt: det finns inget att synka.

**Den föll på att den inte kan uppfylla "ersätta, inte komplettera".**

- Två marketplace-poster är två plugins, alltså **två namnrymder**. Hans `matt-skills:wayfinder` och
  min `mina-skills:wayfinder` existerar båda, samtidigt. Det är exakt "every skill twice" som Matt
  varnar för, bara flyttat in i mitt eget repo.
- Den uppenbara utvägen är `strict: false`, som låter marketplace-posten bestämma vilka av hans
  filer som exponeras — då kunde jag räkna upp bara de skills jag *inte* ersatt. Men
  dokumentationen är entydig: med `strict: false` är marketplace-posten hela definitionen, och
  *"if the plugin also has a `plugin.json` that declares components, that's a conflict and the
  plugin fails to load"*. `mattpocock/skills` **har** en `plugin.json` som deklarerar 25 skills.
  Kombinationen `strict: false` + hans repo som källa laddar alltså inte. (Verifierat mot
  dokumentationen, **inte** empiriskt — se §10.)
- Kvar blir `strict: true`, där hans `plugin.json` styr och alla 25 skills laddas. Jag kan lägga
  till bredvid, men aldrig dra ifrån eller ändra. Alltså: komplettera, inte ersätta.

Slutsatsen är värd att skriva ut, för den är kartans knut: **`source` mot hans repo löser synken
fullständigt och editerbarheten inte alls, och de två kraven kan inte delas upp per skill** — för
det som förhindrar delningen är namnrymden, inte filerna. Vendorering behövs för att *editera*,
precis som #4 fastställde; det nya här är att den inte går att krympa till en delmängd.

---

## 3. Repostruktur

```
.claude-plugin/marketplace.json    en post: moldin-skills, source "./"
.claude-plugin/plugin.json         pluginmanifestet: alla skill-sökvägar, hans och mina
vendor/matt/                       git subtree av mattpocock/skills (hela repot)
mina-skills/<skill-namn>/SKILL.md  mina egna skills
LICENSE                            MIT, två copyright-rader
README.md                          vad det är, attribution, installation
MINA-ANDRINGAR.md                  index över vad jag ändrat i vendor/matt
SPEC.md                            det här dokumentet
```

### `.claude-plugin/marketplace.json`

```json
{
  "name": "moldin",
  "owner": { "name": "Anders Moldin", "url": "https://github.com/andersmoldin" },
  "description": "Anders Moldins skills: Matt Pococks uppsattning, delvis pa svenska, plus egna.",
  "plugins": [
    {
      "name": "moldin-skills",
      "source": "./",
      "description": "Matt Pococks skills (delvis editerade, delvis pa svenska) plus mina egna.",
      "category": "engineering"
    }
  ]
}
```

### `.claude-plugin/plugin.json`

```json
{
  "name": "moldin-skills",
  "description": "Matt Pococks skills, delvis pa svenska, plus mina egna.",
  "author": { "name": "Anders Moldin" },
  "repository": "https://github.com/andersmoldin/skills",
  "license": "MIT",
  "skills": [
    "./vendor/matt/skills/engineering/wayfinder",
    "./vendor/matt/skills/engineering/tdd",
    "…övriga vendorerade skills jag vill ha…",
    "./mina-skills/vanta-va"
  ]
}
```

**Sätt inget `version`-fält.** Claude Code löser version i ordningen `plugin.json` →
marketplace-post → **git-commit-SHA för pluginets källa**, och dokumentationen säger uttryckligen
att `version` kan utelämnas för relativa sökvägar i en git-hostad marketplace. Utelämnat betyder
att varje push blir en ny version automatiskt. Sätter jag ett `version` och glömmer bumpa det
ser klienterna samma version och **hämtar aldrig mina ändringar** — en tyst felmod som inte är värd
risken.

Att en `plugin.json` i roten får peka in i `vendor/` är **verifierat empiriskt**, se §10.

---

## 4. Namnrymd (#6)

| Sak | Namn | Varför |
|---|---|---|
| Marketplace | `moldin` | Måste vara unikt per användare. Kort, mitt, kolliderar inte med `claude-plugins-official`. |
| Plugin | `moldin-skills` | Blir prefix på **varje** skill-anrop, så det ska vara kort och omisskännligt icke-Matt. |
| Hans skills | oförändrade (`wayfinder`, `grill-me`, `tdd`, …) | Muskelminnet överlever bytet; bara prefixet ändras. |
| Mina skills | svensk kebab-case utan diakriter (`vanta-va`) | Åäö är uteslutet i manifestnamn. |

Installation blir `/plugin install moldin-skills@moldin`, och skills anropas
`moldin-skills:wayfinder`.

**Hans skill-namn behålls.** Skills är namnrymdade på **plugin-namnet**, så det finns ingen teknisk
kollisionsrisk — och att döpa om dem skulle kosta muskelminne utan att köpa något. Det enda som
ändras är prefixet: `mattpocock-skills:wayfinder` → `moldin-skills:wayfinder`.

Undantag: en skill som jag skriver om så mycket att den **beter sig annorlunda** ska byta namn, så
att namnet inte ljuger. Skriver jag om `wait-what` till en svensk omformuleringsskill blir den
`vanta-va` i `mina-skills/`, inte en editerad `wait-what` i `vendor/matt/`. Regeln:
*översättning behåller namnet, omdesign byter namn.*

**Hur jag ser vilken variant som körs.** Tre nivåer, i stigande styrka:

1. **Prefixet.** Efter migreringen är `moldin-skills:` den enda namnrymd som finns. Fyrar en skill
   är den min — per konstruktion, eftersom hans plugin är avinstallerat (#10).
2. **Inventariet.** `claude plugin list` och `claude plugin details moldin-skills` visar exakt vilka
   skills som är laddade och varifrån.
3. **Beteendet.** Den starkaste kontrollen är den enklaste: en editerad `wayfinder` som ska svara på
   svenska *svarar på svenska*. Lägg alltid in något observerbart i en editerad skill, så blir
   verifieringen ett beteende och inte en filjämförelse.

**Parallellinstallation under övergången: nej.** Namnrymden tillåter det rent tekniskt — båda
pluginen kan installeras samtidigt utan kollision. Men då laddas 25 skills två gånger, deras
beskrivningar konkurrerar om modellens uppmärksamhet vid varje val, och de betalar always-on-kontext
dubbelt. Det är precis Matts varning. **Och det behövs inte:** jämförelsen mellan min och hans
version är en git-fråga, inte en installationsfråga. `vendor/matt/` *är* hans innehåll, orört, i mitt
repo — `git diff` svarar bättre och gratis:

```bash
git diff $(git merge-base HEAD @{u}) -- vendor/matt/skills/engineering/wayfinder
```

Rollback finns om något ändå går fel (#10) — det är billigare än att leva med dubletter.

---

## 5. Så skiljs mina ändringar från Matts (#7)

Fyra mekanismer, i fallande auktoritet. **Git är sanningen; dokumenten är index som ska gå att
regenerera.** En handunderhållen lista som är enda källa blir fel inom ett halvår.

**1. Strukturell gräns.** Allt under `vendor/matt/` är hans. Allt annat är mitt. Den frågan behöver
aldrig ställas igen.

**2. Committhygien.** Mina ändringar *inuti* `vendor/matt/` ligger alltid i egna commits, aldrig
blandade med en subtree-pull. Prefix i commit-meddelandet:

- `vendor:` — enbart `git subtree pull`, aldrig något annat i samma commit
- `svensk:` — min ändring i en vendorerad fil
- `egen:` — mina egna skills, utanför `vendor/`

**3. Genererat index.** Det här kommandot listar varje vendorerad fil jag rört, och är den
auktoritativa källan till "vad har jag egentligen ändrat":

```bash
git log --oneline --name-only --no-merges --pretty=format:'%h %s' \
  --grep='^svensk:' -- vendor/matt/ | sort -u
```

**4. `MINA-ANDRINGAR.md`.** En kort prosatabell — fil, vad jag gjorde, varför — som fångar *avsikten*,
vilket git inte kan. Uppdateras i samma commit som ändringen. Blir den osams med kommandot i punkt 3
är det kommandot som har rätt. (Filnamn utan diakriter av ren portabilitetsvana; kravet på kebab-case
gäller bara manifestnamn, inte dokumentfilnamn.)

**Regeln för när jag editerar kontra kopierar:**

| Situation | Gör så | Konsekvens |
|---|---|---|
| Liten justering (ton, ett stycke, "svara på svenska") | Editera på plats i `vendor/matt/` | Får hans förbättringar; högljudd konflikt om vi krockar. **Önskvärt.** |
| Fullständig omskrivning | Ny skill i `mina-skills/`, och **ta bort hans sökväg ur `plugin.json`** | Ingen konflikt, ingen dubblett — men jag missar hans förbättringar, medvetet |

Det andra fallet är den enda tysta felmoden som finns kvar i modellen. Därför: varje sådan
ersättning ska ha en rad i `MINA-ANDRINGAR.md` som säger *vilken* skill den ersätter, så att
uppdateringsrutinens steg 4 (§6) kan kontrollera om hans original ändrats sedan dess.

---

## 6. Uppdateringsrutin (#8)

### Hur jag upptäcker att han shippat

Han taggar releaser (`v1.0.0` … `v1.2.3`) och underhåller `CHANGELOG.md`. **Watch → Custom →
Releases** på `mattpocock/skills` ger mejl per release och är den primära signalen. Sekundärt:
hans nyhetsbrev. Notera att taggarna kommer betydligt glesare än commitsen (§10), vilket är bra —
tagg är rätt synkenhet, inte commit.

### Kadens

**Vid hans releaser, alltså i praktiken ungefär månadsvis.** Inte per commit: uppström gör ~325
commits/60 dagar (§10), och att jaga dem vore meningslöst arbete. Inte heller kvartalsvis —
divergensen växer superlinjärt med tiden eftersom sannolikheten att han rört *just* mina filer
ökar.

### Stegen

```bash
# 1. Hämta hans senaste release in i vendorkatalogen
git subtree pull -P vendor/matt --squash https://github.com/mattpocock/skills v1.2.4

# 2. Lös eventuella konflikter — bara i filer jag själv editerat
#    (hans /resolving-merge-conflicts-skill är gjord för precis det här)

# 3. Läs vad som hänt med hans skill-lista: den enda diff som måste läsas varje gång
git diff HEAD~1 -- vendor/matt/.claude-plugin/plugin.json

# 4. Uppdatera MIN plugin.json utifrån steg 3:
#    tillagda skills -> lägg till sökvägen om jag vill ha dem
#    omdöpta        -> ändra sökvägen
#    borttagna      -> ta bort sökvägen (annars går pluginet sönder)
#    Kontrollera samtidigt varje "ersatt" skill i MINA-ANDRINGAR.md

# 5. Validera innan något publiceras
claude plugin validate .

# 6. Testa lokalt utan att röra den installerade uppsättningen
claude --plugin-dir . -p "/moldin-skills:wayfinder hej"

# 7. Publicera
git commit && git push
```

**Steg 3 och 4 är rutinens kärna.** Allt annat är mekanik. Hoppar jag över dem går pluginet sönder
tyst nästa gång han döper om en katalog — en sökväg i min `plugin.json` som inte finns.

### Vem löser konflikterna

Jag, eller en agent på mitt uppdrag. De uppstår bara i filer jag själv har editerat, så de kräver
alltid ett *innehållsbeslut* ("ska hans nya stycke också vara på svenska?") som ingen automat kan
fatta åt mig.

### Vad som kan automatiseras — och vad som inte får det

| Steg | Automatiserbart? |
|---|---|
| Upptäcka release | **Ja.** Watch på releases, eller ett schemalagt jobb som jämför senaste tagg. |
| `subtree pull` + öppna PR | **Ja**, som utkast. Ett GitHub Actions-jobb kan köra pullen och öppna en PR som failar synligt vid konflikt. |
| Lösa konflikter | **Nej.** Innehållsbeslut. |
| Uppdatera `plugin.json` | **Nej.** Urvalsbeslut — det är hela poängen med att den är min. |
| Validera (`claude plugin validate .`) | **Ja**, som CI-grind på varje PR. |
| Merga | **Nej.** |

Rekommendation: börja manuellt. Automatisera först notifiering och validering. Den automatiska
subtree-PR:en är trevlig men inte värd att bygga innan rutinen körts några gånger för hand — och en
automatik som *mergar* ska aldrig byggas, för då är tyst drift tillbaka.

---

## 7. Licens och attribution (#9)

**Licens: MIT.** Samma som uppström. Att byta till något mer restriktivt går inte för hans del
(MIT tillåter vidaredistribution men jag kan inte licensiera om hans arbete under strängare villkor
för andra), och något mer tillåtande finns knappt. Samma licens är dessutom det ärligaste.

**Matts copyright-rad står kvar.** MIT kräver ordagrant att *"the above copyright notice and this
permission notice shall be included in all copies or substantial portions of the Software"*. Här är
det extra viktigt eftersom detta är en **vendorering, inte en fork** — LICENSE ärvs inte automatiskt,
den måste läggas dit avsiktligt. Två saker gäller:

1. `vendor/matt/LICENSE` följer med subtree-pullen och ska **aldrig** redigeras eller raderas. Den
   täcker hans del.
2. Rotens `LICENSE` ska bära båda raderna:

```
MIT License

Copyright (c) 2026 Matt Pocock          (skills under vendor/matt/, ursprungligen fran
                                         https://github.com/mattpocock/skills)
Copyright (c) 2026 Anders Moldin        (egna skills, oversattningar och andringar)

[MIT-texten i sin helhet]
```

**Attribution i README** — omisskännlig, högt upp, inte i en fotnot:

> Grunden i det här repot är [Matt Pococks skills](https://github.com/mattpocock/skills) (MIT).
> Hans arbete ligger orört i `vendor/matt/`; mina ändringar är översättningar och justeringar
> ovanpå det, och listas i [`MINA-ANDRINGAR.md`](MINA-ANDRINGAR.md).
> **Det här är inte Matts officiella distribution.** Vill du ha hans uppsättning som han avsett den,
> installera `mattpocock-skills` från Anthropics officiella marketplace eller följ hans README.

**NOTICE-avsnitt: behövs inte som separat fil.** MIT kräver inget NOTICE (det är ett Apache-2.0-krav),
och en fil till som kan bli inaktuell är en skuld. `MINA-ANDRINGAR.md` fyller redan funktionen
"vad är ändrat" och har en rutin som håller den aktuell (§5). Att lägga till en `NOTICE` som
duplicerar den vore sämre, inte bättre.

**Utöver licensens bokstav.** Det finns förväntningar här som MIT inte reglerar, och de är värda att
möta:

- **Konkurrera inte om hans namn.** Inget i marketplace-, plugin- eller repo-namnet ska innehålla
  "matt" eller "pocock". Därför `moldin-skills`, inte `mattpocock-skills-sv`. Någon som söker efter
  hans uppsättning ska hitta hans.
- **Skicka inte in det här till någon publik katalog** (Anthropics community-marketplace,
  skills.sh) — det är hans arbete med mina översättningar, inte en produkt jag har rätt att
  marknadsföra som min. Repot är publikt för att jag ska nå det från flera maskiner, inte för att
  konkurrera.
- **Behåll hans namn inuti filerna.** Editera inte bort författarrader ur vendorerade SKILL.md.
- **Länka tillbaka** till hans repo och nyhetsbrev från README.

Notera samtidigt att han i sin README beskriver pluginet som *"a managed, read-only bundle … you
subscribe rather than fork"* och att det inte finns någon `CONTRIBUTING.md`. Han inbjuder alltså inte
till forkar. Han *tillåter* dem — MIT — och hans egen `marketplace.json` är i källan beskriven som en
fallback *"for a fork"*. Det är grönt ljus nog, men det är ett skäl att hålla profilen låg snarare än
att marknadsföra bygget.

---

## 8. Migrering (#10)

### Förutsättningar som styr ordningen

- `mattpocock-skills` kommer från `claude-plugins-official`, som också levererar många andra
  plugins. **Ta aldrig bort den marketplacen** — dokumentationen är tydlig: *"Removing a marketplace
  will uninstall any plugins you installed from it."* Avinstallera bara pluginet.
- **Ingenting synkas mellan maskiner.** `~/.claude/plugins/cache/` är per dator. Varje maskin måste
  köra samma steg.
- Plugins laddas vid sessionsstart; ändringar kräver `/reload-plugins` eller omstart.

### Maskin 1

```bash
# 0. Avsluta eller checkpointa pågående arbete som lutar sig mot hans skills.
#    /mattpocock-skills:handoff är gjord för det. Efter steg 1 finns de inte.

# 1. Avinstallera hans plugin (marketplacen lämnas orörd)
claude plugin uninstall mattpocock-skills@claude-plugins-official

# 2. Lägg till min marketplace
claude plugin marketplace add andersmoldin/skills

# 3. Installera mitt plugin, globalt (user scope = alla projekt)
claude plugin install moldin-skills@moldin --scope user

# 4. Aktivera i en öppen session
/reload-plugins        # vid varning: /reload-plugins --force

# 5. Slå på auto-update: /plugin -> Marketplaces -> moldin -> Enable auto-update
```

**Varför avinstallera först.** Det ger ett kort fönster utan skills, men det köper något viktigare:
under verifieringen (steg 6) finns bara *en* uppsättning, så frågan "är det min eller hans wayfinder
som svarade?" kan inte uppstå. Den omvända ordningen — installera först — ger dubbletter under
verifieringen, vilket är precis den tvetydighet jag försöker undvika. Rollback är billig:

```bash
claude plugin install mattpocock-skills@claude-plugins-official
```

### Maskin 2 och 3

Exakt samma steg 1–5. Inget hoppas över, inget synkas. Två saker skiljer:

- **Steg 0 är viktigare**, för de maskinerna har sessioner du inte tittar på just nu.
- **Versionsdrift är normalt.** Maskinerna hämtar var för sig; en som varit avstängd ligger efter
  tills auto-update kört eller `/plugin marketplace update moldin` körts manuellt. Det är
  ofarligt — skills är textfiler utan delat tillstånd. Ligger en maskin efter: kör steg 5 nedan.

Om en maskin ligger efter, eller efter varje publicerad ändring om auto-update är av:

```bash
claude plugin marketplace update moldin
claude plugin update moldin-skills@moldin
```

### Auto-update: på

Tredjepartsmarketplaces har auto-update **av** som standard. Slå på den för `moldin`.

Skälet är kravet på flera maskiner: auto-update är det enda som håller tre datorer i takt utan
manuellt arbete på var och en, och utan den blir "vilken maskin har vilken version" en fråga jag
måste bära i huvudet. Risken — att en dålig push sprider sig automatiskt — är liten här, eftersom
jag är den enda som pushar och `git revert` + push återställer alla maskiner lika automatiskt.

Två detaljer värda att känna till: uppdateringen sker i bakgrunden efter sessionsstart med upp till
tio minuters slumpmässig fördröjning, så den **påverkar aldrig en session som redan kör**; och
bakgrundspullens problem med git-credentials gäller bara *privata* repon — mitt är publikt, så det
berör mig inte.

### Verifiering

```bash
claude plugin list                      # moldin-skills@moldin, inget mattpocock-skills
claude plugin details moldin-skills     # inventariet: rätt antal skills, rätt namn
```

Och den som faktiskt bevisar något: **kör en editerad skill och se att den beter sig som min.**
`/moldin-skills:wayfinder` ska svara på svenska. Inventarielistor visar att rätt filer är på plats;
bara beteendet visar att rätt fil *laddades*.

---

## 9. Att göra i ordning (bygglista)

1. `git subtree add -P vendor/matt --squash https://github.com/mattpocock/skills v1.2.3`
2. Skriv `.claude-plugin/marketplace.json` och `.claude-plugin/plugin.json` (§3)
3. Skriv rotens `LICENSE` med båda copyright-raderna (§7)
4. Uppdatera `README.md` med attribution och installationsinstruktion (§7)
5. Skapa `MINA-ANDRINGAR.md` (tom tabell med rubriker)
6. `claude plugin validate .`
7. `claude --plugin-dir . -p "…"` för rökprov
8. Pusha, och kör migreringen på maskin 1 (§8)
9. Först därefter: börja översätta skills

---

## 10. Faktabilaga: vad som är verifierat och vad som inte är det

Allt nedan kontrollerades 2026-08-07/08 mot primärkälla. Där något inte gick att verifiera står det.

### Empiriskt test: gör plugininstallationen `--recurse-submodules`?

**Ja.** Detta motsäger den slutsats som låg närmast till hands i #4, och motsägelsen är avsiktlig
och belagd.

Miljö: Claude Code **2.1.224**, git 2.54.0, macOS 26.6 arm64. Allt kördes mot en
engångs-`CLAUDE_CONFIG_DIR`, aldrig mot den globala uppsättningen.

Uppsättning: ett engångsrepo (privat, sedan tömt på innehåll) med
`.claude-plugin/marketplace.json` i roten, en enda plugin-post med `"source": "./vendor/skills"`,
där `vendor/skills` var en **git-submodul** som pekade på `https://github.com/mattpocock/skills`.

| Steg | Kommando | Resultat |
|---|---|---|
| Kontroll | `git clone` (utan flaggor) av samma repo | `vendor/skills/` **tom** — 0 filer |
| Add | `claude plugin marketplace add andersmoldin/fm-submodul-test` | `vendor/skills/` **fylld — 151 filer** |
| Install | `claude plugin install submodul-test@…` | Lyckades. 35 `SKILL.md` i cachen; version `1.2.3` lästes ur submodulens `plugin.json`; `gitCommitSha` blev submodulens commit |
| Update | flyttade submodulpekaren till `v1.2.0`, pushade, `claude plugin marketplace update` | Innehållet **följde med**: `1.2.3` → `1.2.0` |

Alltså: både klon-, installations- och uppdateringsvägen tar med submoduler. Stödbevis: den
installerade binären innehåller ett kluster av klonargument — `clone`, `--depth`,
`--recurse-submodules`, `--shallow-submodules`, `--branch`, `--no-checkout` — direkt intill
telemetrinamnet `plugin_clone` och plugin-SHA-validering.

**Men beteendet är odokumenterat.** Ordet "submodule" förekommer ingenstans i
marketplace-dokumentationen. Det är alltså en *observerad implementationsdetalj i 2.1.224*, inte ett
löfte, och kan regrediera utan att någon annonserar det. Det räcker för att inte avfärda submoduler
som tekniskt omöjliga — men inte för att bygga på dem. Bortvalet i §2 vilar därför på
editerbarheten, inte på det här testet.

Engångsrepot `andersmoldin/fm-submodul-test` kunde **inte raderas** av agenten: token saknar
`delete_repo`-scope. Det är privat och tomt på värde. Radera det:
`gh repo delete andersmoldin/fm-submodul-test --yes`.

### Verifierat empiriskt

- **En `plugin.json` i roten får peka in i en underkatalog.** Byggde ett plugin med
  `skills: ["./vendor/matt/…/wayfinder", "./mina-skills/vanta-va"]`, körde
  `claude plugin validate` (passerade) och installerade det lokalt:
  `claude plugin details` visade båda skills under **en** namnrymd. Det är hela §3:s bärande
  antagande.
- **Lokala sökvägar klonas inte.** En marketplace tillagd som `./path` registreras som
  `"source": "directory"` och pekar rakt på originalkatalogen. Bra att veta vid lokal utveckling —
  ändringar slår igenom direkt, utan `marketplace update`.
- **Skills namnrymdas på plugin-namnet.** Direkt observerbart i den här sessionen: hans skills
  exponeras som `mattpocock-skills:tdd`, `mattpocock-skills:grilling`, …

### Verifierat mot dokumentationen (code.claude.com)

- `.claude-plugin/marketplace.json` ska ligga i repots rot; relativa `source`-sökvägar löses mot
  marketplace-roten och får inte använda `../`.
- Plugin-källor: relativ sökväg, `github` (`repo`, `ref?`, `sha?`), `url`, `git-subdir`, `npm`,
  `archive`. Sätts både `ref` och `sha` vinner `sha`.
- Versionsordning: `plugin.json` → marketplace-post → git-commit-SHA. `version` kan utelämnas för
  git-baserade källor. Ett satt men obumpat `version` gör att klienterna aldrig uppdaterar.
- `strict: false` + ett plugin som har egen `plugin.json` med komponenter ⇒ konflikt, pluginet
  laddar inte. **Detta är inte testat empiriskt** — det är grunden för att den kombinerade modellen
  valdes bort i §2, så om det beslutet ska rivas upp är det här som ska testas först.
- Auto-update: **på** som standard för Anthropics officiella marketplaces, **av** för
  tredjeparts- och lokala. Bakgrundsuppdatering sker efter sessionsstart med upp till tio minuters
  slumpfördröjning.
- `renames`-fältet i `marketplace.json` migrerar användare vid namnbyte (kräver ≥ 2.1.193). Relevant
  om `moldin-skills` någonsin döps om — då ska `renames` användas, inte ett rent namnbyte.
- Att ta bort en marketplace avinstallerar alla plugins från den.
- Ett plugins `name` är dess stabila identifierare; `displayName` ändrar etiketten utan att bryta
  installationer.

### Verifierat mot `mattpocock/skills` (klon av `main`, commit `84fdeff`)

- MIT, `Copyright (c) 2026 Matt Pocock`.
- Senaste tagg **v1.2.3**; `plugin.json` på `main` står på `1.2.3`.
- `plugin.json` räknar upp **25** skill-kataloger explicit. **101** filer under `skills/`.
- README ordagrant: *"installs the whole set as a managed, read-only bundle that updates when I ship
  — you subscribe rather than fork"* … *"Pick one — installing both leaves you with every skill
  twice."*

### Korrigeringar av kartan och researchen

Två fastställda uppgifter stämmer inte längre. Båda är belagda:

1. **Uppström rör sig ~3× snabbare än #4 angav.** #4 skrev "~100 commits på 60 dagar". Faktiskt
   utfall mätt på `origin/main`: **325 commits** senaste 60 dagarna (238 exklusive merge-commits),
   och **132 distinkta filer** under `skills/` berörda under perioden — fler än de 101 som finns nu,
   eftersom filer också döpts om och raderats. Det stärker slutsatsen i §2, det ändrar den inte:
   desto viktigare att konfliktytan är liten och att den som finns är högljudd.
2. **Den installerade `mattpocock-skills` står på 1.2.3, inte 1.2.0** som kartan angav
   (`installed_plugins.json`, `lastUpdated` 2026-08-07). Förklaringen är att `claude-plugins-official`
   är en officiell marketplace, och de har auto-update på som standard. Kartans observation att den
   kurerade kopian låg efter hans `main` gäller alltså inte längre — 1.2.3 är i kapp med senaste
   taggen.

### Fallgropar att bära vidare

- **`vendor/matt/scripts/link-skills.sh` skriver över poster i `~/.claude/skills`.** Kör den aldrig.
  Den följer med subtree-pullen och ser ofarlig ut.
- Hans `.github/workflows/` hamnar under `vendor/matt/` och kör därför inte. Flytta dem aldrig till
  roten.
- `AGENTS.md` i hans repo är en symlink till `CLAUDE.md`. Den ligger inom pluginroten och bevaras;
  den är inte en skill och påverkar ingenting.
