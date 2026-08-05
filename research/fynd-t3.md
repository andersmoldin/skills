# Att hålla ett editerat repo i synk med uppström

Utredning mot primärkällor: GitHubs egen dokumentationskälla (`github/docs` på GitHub), gits egna manualsidor lokalt (git 2.54.0) och `contrib/subtree/git-subtree.adoc` från git.git, samt Claude Codes plugindokumentation på `code.claude.com/docs`. Fakta om uppströmsrepot är hämtade live från GitHubs API.

## Utgångsläget (verifierat)

`mattpocock/skills`, MIT, default-branch `main`, ~205k stjärnor, senast pushat 2026-08-05. **Cirka 100 commits de senaste 60 dagarna** — alltså en aktiv uppström, inte ett arkiverat repo. Taggar finns (`v1.0.0` … `v1.2.2`), så "release" är ett meningsfullt begrepp, men huvudflödet ligger på `main`.

Strukturen är den som avgör allt nedan:

- `.claude-plugin/marketplace.json` i roten, med **`"source": "./"`** — hans pluginrot *är* repots rot.
- `.claude-plugin/plugin.json` i roten, med ett **explicit `skills`-fält som räknar upp alla 25 skill-kataloger** (`./skills/engineering/tdd` osv.).
- `skills/` med underkatalogerna `engineering`, `productivity`, `misc`, `in-progress`, `deprecated` — **101 filer** totalt under `skills/`.
- I roten ligger dessutom `AGENTS.md`, `CLAUDE.md`, `CONTEXT.md`, `README.md`, `package.json`, `package-lock.json`, `.changeset/`, `.github/`, `docs/`, `scripts/`, `.agents/`, `.out-of-scope/`.

Två konsekvenser att bära med sig:

1. Eftersom `plugin.json` listar varje skill-sökväg explicit blir **varje flytt eller omdöpning uppströms en ändring i `plugin.json`** — samma fil som du sannolikt också vill editera (namn, beskrivning, urval). Det är den enskilt mest konfliktbenägna filen i hela repot.
2. Eftersom hans pluginrot är repotsrot krockar hans rotfiler (`CLAUDE.md`, `package.json`, `README.md`) med dina om du lägger hans innehåll i din rot.

## Vad Claude Code faktiskt kräver (verifierat mot code.claude.com)

Detta ändrar problemet mer än man tror:

- **`.claude-plugin/marketplace.json` ska ligga i repots rot.** Ordagrant: "Create `.claude-plugin/marketplace.json` in your repository root."
- **`source` behöver inte peka på roten.** Tillåtna former: relativ sökväg (`"./plugins/formatter"`, måste börja med `./`, löses mot *marketplace-roten*, alltså katalogen som innehåller `.claude-plugin/`, och får inte gå utanför den med `../`), samt objekten `github` (`repo`, `ref?`, `sha?`), `url`, `git-subdir` (`url`, `path`, `ref?`, `sha?`) och `npm`.
- **`metadata.pluginRoot`** kan sättas som basprefix för relativa sökvägar.
- **`strict`**: `true` (default) = pluginets eget `plugin.json` är auktoritet och marketplace-posten kan *lägga till* komponenter ovanpå. `false` = marketplace-posten är hela definitionen, och om pluginet har ett `plugin.json` som deklarerar komponenter är det en konflikt och pluginet laddar inte.
- Vid `source: "./"` som delas av flera poster kan man lista specifika underkataloger i `skills`-fältet så att bara de laddas.
- Claude Code **klonar** marketplace-repot och kopierar sedan pluginkatalogen till `~/.claude/plugins/cache`. Bakgrundsuppdatering är `git pull` med fallback till omklon. **Submoduler nämns inte någonstans i dokumentationen** — varken kloning, uppdatering eller cache-kopiering säger något om `--recurse-submodules`.
- Symlänkar: bevaras inom pluginets egen katalog, **dereferereras** (innehållet kopieras in) om de pekar någon annanstans inom samma marketplace, och **hoppas över** om de pekar utanför marketplace-roten.

Den viktigaste följden: **du behöver inte vendorera hans filer för att ha ett fristående installerbart plugin.** En `marketplace.json` i din rot kan lista en post med `source: {source: "github", repo: "mattpocock/skills"}` bredvid en post med `source: "./mina-skills"`. Men den vägen ger dig noll möjlighet att *ändra* hans filer — och kravet här är uttryckligen att svara på svenska i hans SKILL.md. Så fort du vill editera hans innehåll måste innehållet finnas som filer du kontrollerar, och då är frågan bara *hur* de kom dit.

---

## Jämförelse

| | Konfliktyta och frekvens | Kostnad per uppström-release | Fil raderad/omdöpt uppströms | Fristående plugin i rot? | GitHub-avtryck |
|---|---|---|---|---|---|
| **Äkta fork + merge** | Konflikt bara i filer du faktiskt rört; git gör 3-vägs-merge med namnbytesdetektering. Frekvens ∝ hur många av hans 101 filer du editerat | Låg när du rört få filer: `git fetch && git merge upstream/main`, lös 0–N konflikter. `plugin.json` konfliktar nästan varje gång du ändrat skill-listan | Merge hanterar det korrekt: rename följs, delete-vs-modify blir en explicit konflikt du måste besluta om | Ja — filerna ligger där de ska, `.claude-plugin/` i roten redan från start | "forked from" visas under namnet; osynlig i sök som default; visibility låst till nätverket; egna issues men förlorade om du detachar |
| **Äkta fork + rebase** | Samma konflikter men de **återuppstår vid varje rebase** eftersom dina commits spelas om från grunden. `rerere` mildrar men måste aktiveras per klon | Låg första gången, sedan repetitiv. Kräver force-push, vilket bryter för alla som klonat | Som merge, men beslutet måste fattas om vid varje omspelning | Ja | Samma som ovan |
| **git subtree** | Uppström i en underkatalog. Konflikter uppstår bara inom prefixet, och bara i filer du rört — samma logik som merge, för det *är* en merge | `git subtree pull -P vendor/skills --squash <repo> main`. Något högre ceremoni, `--squash` rekommenderas för att inte dränka loggen | Merge-semantik gäller inom prefixet; namnbytesdetektering fungerar | Ja, men kräver **omstrukturering**: din `.claude-plugin/marketplace.json` i roten med `"source": "./vendor/skills"`. Hans `plugin.json` följer med underkatalogen och fungerar som pluginmanifest (`strict: true`) | Inget fork-avtryck alls. Vanligt repo, egna issues, syns i sök |
| **git submodule** | Ingen konfliktyta — **för att du inte kan editera hans filer alls**. Ändringar kräver commits i ett repo du äger, dvs. en fork som submodulmål, varpå forkproblemet är tillbaka | Nära noll: `git submodule update --remote` + commit av den nya pekaren | Trivialt uppströms, men eventuella egna ändringar finns inte där att kollidera | **Riskabelt.** Dokumentationen nämner inte submoduler någonstans; kloningen och bakgrunds-`git pull` beskrivs utan `--recurse-submodules`. Sannolik effekt: tom katalog hos användaren | Vanligt repo, men användaren behöver `--recurse-submodules` för att alls se innehållet vid manuell kloning |
| **Vendorering via sync-script** | Störst yta: skriptet ser inte skillnad på "uppström ändrade" och "jag ändrade". Rå kopiering skriver över dina ändringar tyst; skillnadsbaserad kopiering blir en handskriven merge | Beror helt på skriptets ambition. Naiv kopiering: sekunder, men dina svenska texter försvinner. Med bevarande av dina filer: manuell genomgång av alla ändrade filer | **Sämst.** Ingen namnbytesdetektering — en omdöpt fil ser ut som "raderad + ny", och en raderad fil du editerat blir antingen kvar för evigt eller tyst borta | Ja, helt fri layout | Vanligt repo, inget avtryck |
| **Patch/overlay** | Konflikter uppstår när patchens kontext inte längre matchar. En översatt SKILL.md är i praktiken en full omskrivning av filen, så patchen är hela filen — och rejectas vid minsta uppströmsändring i den | Kör om bygget; varje patch som inte applicerar måste regenereras för hand mot den nya filen | Patch mot raderad fil failar hårt vid bygget — vilket i sig är bra signal, men bygget stannar tills du agerar | Ja, om bygget commitas till repot. Om resultatet bara byggs i CI måste artefakten ändå landa i roten, för Claude Code läser filer ur klonen | Vanligt repo, inget avtryck |

---

## Äkta GitHub-fork

### Mekaniken

`git fetch upstream && git checkout main && git merge upstream/main`. GitHubs dokumentation beskriver exakt detta flöde och noterar att om din lokala gren inte har egna commits blir det en fast-forward; har den egna commits "you may need to resolve conflicts". "Sync fork" i webbgränssnittet gör samma sak: du får se commits från uppström och klickar **Update branch**. Ordagrant om konflikter: *"If the changes from the upstream repository cause conflicts, GitHub will prompt you to create a pull request to resolve the conflicts."* Knappen löser alltså inget själv — den skjuter över det på en PR. `gh repo sync -b BRANCH` är CLI-motsvarigheten, och: *"If the changes from the upstream repository cause conflicts, the GitHub CLI can't sync. To overwrite the destination branch, use the `--force` flag."* `--force` betyder här att dina ändringar skrivs över — det är alltså inte en konfliktlösning utan ett uppgivande.

Kort sagt: **så fort du har editerat hans filer är "Sync fork"-knappen och `gh repo sync` i praktiken oanvändbara**, och du är tillbaka på `git merge` i terminalen. Det är inte en defekt, det är designen.

### Konfliktfrekvens

Merge konfliktar bara där båda sidor ändrat samma fil (och för textfiler: samma rader). Har du översatt fem SKILL.md är det de fem filerna plus `plugin.json` som är exponerade — de övriga ~95 filerna flyter in gratis. Med ~100 commits/60 dagar uppströms blir en synk varannan vecka realistisk och konfliktmängden per synk liten men inte noll.

Två gitmekanismer värda att känna till, båda verifierade i manualsidorna:

- **`rerere`** (*"recording conflicted automerge results and corresponding hand resolve results on the initial manual merge, and applying previously recorded hand resolutions"*) — kräver `rerere.enabled` i konfigurationen, alltså per klon, och kan inte checkas in.
- **`merge=ours` via `.gitattributes`** — den klassiska "mina filer vinner alltid"-tricket. Viktig detalj: de **inbyggda** merge-drivrutinerna är enligt `gitattributes(5)` bara `text`, `binary` och `union`. `ours` är *inte* inbyggd; den måste definieras som en egen drivrutin, och *"the definition of a merge driver is done in the .git/config file, not in the gitattributes file"*. Alltså: går inte att distribuera i repot, varje klon måste konfigurera den. Och den gäller bara innehållsmerge — den räddar dig inte från delete/rename-konflikter.

### Rebase i stället för merge

Rebase håller historiken linjär och gör din delta läsbar som en patchserie ovanpå uppström. Priset är att dina commits skrivs om vid varje rebase, vilket kräver force-push till din publika gren. För ett repo som andra installerar som plugin är det direkt skadligt: Claude Code gör bakgrunds-`git pull` mot marketplace-klonen, och en force-pushad historik gör den pullen till en fast-forward-failure (dokumentationen beskriver att en misslyckad pull leder till att marketplace-repot raderas och klonas om — det *läker*, men det är onödig turbulens). Dessutom återuppstår samma konflikter vid varje rebase, till skillnad från merge där en löst konflikt är löst.

### Brytande ändring uppströms

Här är fork/merge starkast av alla alternativ. Git gör namnbytesdetektering, så en omdöpt fil du editerat följer med till det nya namnet och din ändring hamnar rätt. En fil du editerat som raderats uppströms ger en explicit *delete/modify*-konflikt — git vägrar gissa, och du måste ta beslutet. Det är det beteende du vill ha.

### Fristående installerbart plugin?

Tekniskt: ja, direkt. Filerna ligger där de ska, `.claude-plugin/marketplace.json` finns redan i roten och behöver bara byta `name` och `owner`. Ett `/plugin marketplace add ditt-namn/skills` fungerar på en fork precis som på vilket repo som helst.

### GitHub-specifika detaljer (verifierade)

- **"forked from" visas alltid.** Dokumentationen: *"When you view a forked repository on GitHub, the upstream repository is indicated below the name of the fork."* Det går inte att stänga av.
- **Egna issues — och egen numrering.** Påståendet i frågan att forks delar issue-numrering med uppström stämmer **inte**. Dokumentationen räknar upp vad varje fork kan ha eget av: *"Branches / Members and discussions / Issues and pull requests / Actions and projects / Tags, labels, and wikis."* Numreringen är per repo. Det som *delas* är gitobjekten: *"repository networks still share Git data. Commits pushed to any repository in a network can be accessible from other repositories in that network, including the upstream repository."* Alltså — allt du pushar till din fork är läsbart från uppström. (Att issues dessutom brukar vara *avstängda* som default i en ny fork är vanlig erfarenhet men **jag hittade inget dokumentationsstöd för det** — behandla som obekräftat.)
- **Synlighet är låst till nätverket.** *"You cannot change the visibility of a fork by itself."* Publikt uppström ⇒ publik fork, inget val.
- **Forks syns inte i sök som default.** *"By default, forks are not shown in search results."* Repo-sök kräver `fork:true`/`fork:only`, kodsök `is:fork`. För något som ska vara *upptäckbart* som publikt plugin är detta en reell kostnad.
- **Att bli fristående går — men det kostar.** Sedan en tid finns "Leave fork network" i Danger Zone. Villkoren är att forken är publik, under 1 GB och saknar egna child-forks. Varningen är rak: *"The new repository will not retain any of its issues, pull requests, wikis, stars, watchers, comments, child forks, or other metadata"* och *"Leaving the fork network is **permanent** and the new repository **cannot** be reconnected to the fork network."* Alternativt manuellt: bare-klon, radera repot, skapa nytt med samma namn, `push --mirror`. Notera vad detta betyder för synk: **när du lämnat nätverket finns ingen "Sync fork"-knapp längre**, men `git merge upstream/main` mot en manuellt tillagd remote fungerar exakt som förut. Fork-relationen på GitHub tillför i praktiken ingenting till själva synkmekaniken utöver knappen som ändå slutar fungera vid konflikt.

---

## git subtree

### Mekaniken

Från git.git:s egen dokumentation: *"Subtrees allow subprojects to be included within a subdirectory of the main project, optionally including the subproject's entire history"* och — den avgörande meningen mot submodule — *"subtrees do not need any special constructions (like `.gitmodules` files or gitlinks) be present in your repository, and do not force end-users of your repository to do anything special or to understand how subtrees work. A subtree is just a subdirectory."*

Uppsättning: `git subtree add -P vendor/skills --squash https://github.com/mattpocock/skills main`. Synk: `git subtree pull -P vendor/skills --squash https://github.com/mattpocock/skills main`. Dokumentationen är explicit att `pull` *"Exactly like 'merge', but parallels 'git pull'"* — det är alltså en riktig git-merge, med allt vad det innebär av 3-vägs-sammanslagning och namnbytesdetektering, bara förskjuten in i ett prefix.

`--squash` beskrivs som ett sätt att slippa loggskräp och att undvika problem *"when the same subproject is included multiple times in the same project, or is removed and then re-added"*. Fotnoten värd att notera: om du använt `--squash` vid tidigare merge av en annoterad tagg måste den taggen finnas lokalt vid nästa operation.

### Konfliktfrekvens och kostnad

Identisk med fork+merge, med skillnaden att konfliktytan är instängd i `vendor/skills/`. Dina egna filer utanför prefixet kan per konstruktion aldrig konflikta. Detta är ett verkligt värde: **separationen mellan "hans kod" och "min kod" är strukturell i stället för att bara vara en överenskommelse**.

Merkostnaden är att kommandot är längre och att `-P`-flaggan är obligatorisk för alla underkommandon — glömmer man den får man fel. En hjälpsam praxis är ett kort skript eller en Makefile-rad. Vill man senare bidra tillbaka finns `git subtree push`, som gör en `split` och pushar — men var uppmärksam på dokumentationens varning om `--annotate`: *"Whenever you split, you need to use the same annotation, or else you don't have a guarantee that the new re-created history will be identical to the old one. That will prevent merging from working correctly."*

### Brytande ändring uppströms

Samma som merge — bra. Namnbyten följs, delete/modify blir explicit konflikt.

### Fristående installerbart plugin?

Ja, men det kräver att du **skriver din egen `marketplace.json`** i roten i stället för att ärva hans. Konkret: `.claude-plugin/marketplace.json` i din rot, med en post `"source": "./vendor/skills"`. Hans `.claude-plugin/plugin.json` följer med underkatalogen och blir pluginmanifest för den posten under default-`strict: true`. Dina egna skills läggs som en andra post med t.ex. `"source": "./mina-skills"` — eller så pekar båda posterna in i vendorkatalogen med explicita `skills`-listor.

Två fällor att känna till, båda dokumenterade:

- Relativa sökvägar får **inte** använda `../` och löses mot marketplace-roten (katalogen som innehåller `.claude-plugin/`), inte mot `.claude-plugin/` självt.
- Om någon lägger till din marketplace via en **direkt URL till `marketplace.json`** i stället för via git, laddas bara den filen och relativa sökvägar bryts. Distribuera som git-repo, inte som fil-URL.

Ett tredje övervägande: om du vill *editera* hans filer på plats i `vendor/skills/` fungerar det utmärkt — det är dina commits i ditt repo, och `subtree pull` mergar över dem. Det är precis samma modell som forken, men utan fork-avtrycket och med tydligare gräns.

---

## git submodule

### Mekaniken

`git submodule add`, sedan `git submodule update --remote` för att flytta pekaren till uppströms senaste. Superprojektet lagrar bara ett commit-SHA (en gitlink); innehållet checkas ut på *detached HEAD* i submodulen (manualsidan: *"Checkout the commit recorded in the superproject on a detached HEAD in the submodule"*).

### Den avgörande begränsningen

**Du kan inte editera hans filer.** Filerna i submodulen tillhör hans repo. En ändring där måste committas och pushas till ett repo du har skrivrättighet till — alltså din fork — och då har du inte undvikit forken, du har lagt till ett extra lager ovanpå den. Det gör submodule till fel verktyg för själva uppgiften ("editera hans SKILL.md så den svarar på svenska"), oavsett dess övriga egenskaper.

Om man ändå tänker sig submodule + fork: konflikthanteringen sker i forken (samma som avsnitt 1), och submodulen tillför bara ceremonin att flytta pekaren.

### Vid brytande ändring uppströms

Enkelt i sig — ny SHA, klart. Men eftersom dina ändringar inte bor där finns heller inget att stämma av mot, så "enkelheten" är en följd av att problemet flyttats någon annanstans.

### Fristående installerbart plugin?

**Detta är den allvarliga invändningen.** Claude Code klonar marketplace-repot och kopierar sedan pluginkatalogen till `~/.claude/plugins/cache`. Bakgrundsuppdatering körs som `git pull` med omklon som fallback. **Ordet "submodule" förekommer inte i marketplace- eller pluginreferensdokumentationen** — inte i beskrivningen av kloning, inte i uppdateringsflödet, inte i cache-kopieringen. Ingenting antyder `--recurse-submodules`. En vanlig `git clone` lämnar submodulkatalogen tom, vilket i så fall betyder att pluginet installeras utan innehåll.

Detta är ett *dokumentationsmässigt frånvarobevis*, inte ett testat resultat. Det går att avgöra empiriskt på tio minuter (publicera ett testrepo med submodul och kör `/plugin marketplace add`), och den verifieringen bör göras innan alternativet avfärdas formellt. Men riskprofilen är tydlig: modellen bygger på en funktion som inte utlovas.

Notera i sammanhanget att symlänk-hanteringen *är* uttryckligen dokumenterad (bevaras inom pluginkatalogen, derefereras inom samma marketplace, hoppas över utanför). Att submoduler inte fått samma behandling är i sig talande.

---

## Vendorering via sync-script

### Mekaniken

Ett skript kopierar in uppströms filer i din trädstruktur. Ingen delad historik, ingen merge-bas.

### Varför konflikthanteringen blir sämre än den ser ut

Det centrala problemet är att **skriptet saknar merge-bas**. Git kan avgöra "ändrade *jag* denna fil eller ändrade *han* den?" eftersom den vet vad filen såg ut som när ni skildes åt. Ett kopieringsskript vet bara hur filen ser ut nu på båda sidor. Det ger tre otillfredsställande utfall att välja mellan:

1. **Kopiera allt rakt över.** Dina svenska översättningar försvinner tyst vid varje synk. Snabbt, och fel.
2. **Kopiera allt utom en undantagslista.** Dina översatta filer bevaras — men de **fryses**, och du missar alla hans förbättringar i exakt de filer du brydde dig tillräckligt mycket om för att editera. Det är den vanligaste tysta felmoden.
3. **Rapportera skillnader och låt en människa avgöra.** Fungerar, men då har du byggt en sämre version av `git merge` för hand.

Ett realistiskt mellanting är att låta skriptet vendorera in i en *orörd* spegelkatalog och committa den, så att `git diff` mellan två synkar blir läsbar. Men då har du i praktiken byggt subtree, bara med sämre verktyg.

### Brytande ändring uppströms

Sämst av alla alternativ. Utan namnbytesdetektering ser en omdöpt fil ut som "en fil försvann, en fil dök upp" — och om det var en fil du editerat blir din version antingen kvar som ett spöke under det gamla namnet, eller överskriven, beroende på hur skriptet är skrivet. Med hans `plugin.json` som räknar upp varje skill-sökväg explicit blir följdfelen synliga först vid installation.

### Fristående installerbart plugin?

Ja, och med störst frihet — layouten är helt din. Ingen strukturell begränsning alls.

### Kostnad

Låg löpande *körtid*, hög löpande *uppmärksamhet*. Skriptet blir en egen liten kodbas som måste underhållas mot uppströms strukturförändringar (`skills/engineering/` → något annat), och den underhållskostnaden är osynlig tills den plötsligt inte är det.

---

## Patch/overlay

### Mekaniken

Uppströms innehåll hålls bit-identiskt (som subtree, submodule eller en pinnad `github`-källa). Dina ändringar lever separat, antingen som patchfiler som appliceras vid bygget (`git apply` / quilt-modell) eller som overlay-filer som kopieras över efteråt.

### Konfliktfrekvens — och en avgörande nyans för just detta fall

Patchmodellen fungerar bäst när dina ändringar är **små och lokala** i stora filer. Kravet här är motsatsen: *"ändra en SKILL.md så den svarar på svenska"* är en fullständig omskrivning av filens innehåll. En patch som ersätter hela filen har ingen meningsfull kontext att matcha mot — den kommer att rejecta vid nästan varje uppströmsändring i filen, och regenereringen är då lika mycket arbete som en manuell merge.

**Overlay-varianten är däremot förvånansvärt stark just här.** Om din svenska SKILL.md helt enkelt är en fil som kopieras över hans vid bygget, finns ingen patchkontext som kan bli inaktuell. Kostnaden per uppström-release blir noll — men bara i den bokstavliga meningen att bygget inte går sönder. Semantiskt är det samma frysning som vendorering-alternativ 2: din svenska version driver ifrån hans engelska utan att någon säger till. Vill du fånga det behöver du en separat kontroll ("varna om hans version av en overlay-täckt fil har ändrats sedan senaste synk") — vilket i sin tur kräver att du sparar en referenspunkt, alltså i praktiken en merge-bas, alltså i praktiken git.

### Brytande ändring uppströms

Detta är patchmodellens bästa egenskap: **den failar högljutt**. En patch mot en raderad eller flyttad fil applicerar inte, och bygget stannar. Ingen tyst drift. Overlay-varianten failar tystare — en overlay-fil vars mål inte längre finns skapar bara en föräldralös fil, om inte bygget aktivt kontrollerar att målet existerade.

### Fristående installerbart plugin?

Ja, med ett krav: **resultatet måste finnas committat i repot**, eftersom Claude Code läser filer ur en klon av ditt repo, inte kör ditt bygge. Alltså behöver du antingen committa det byggda resultatet (och då bär du både källa och artefakt i samma repo, med risk för att de glider isär) eller köra bygget i CI som committar tillbaka till en publiceringsgren som marketplacen pekar på via `ref`. Båda fungerar; båda är mer maskineri än de andra alternativen.

---

## En sjätte möjlighet som föll ut av utredningen

Värd att notera eftersom den inte fanns i listan: **`marketplace.json` kan lista en post vars `source` är hans repo direkt** (`{"source": "github", "repo": "mattpocock/skills", "ref": "v1.2.2"}` eller `sha` för exakt pinning) **bredvid en post med dina egna skills på relativ sökväg.** Ditt repo är då en katalog över två plugins: hans, orörda och alltid färska, och dina, helt egna.

Det löser synkproblemet fullständigt — det finns inget att synka — men **det löser inte översättningskravet**, eftersom hans filer aldrig passerar genom dina händer. `strict: false` låter marketplace-posten bestämma *vilka* av hans filer som exponeras som skills, alltså kurering och urval, men inte *innehållet* i dem.

Kombinationen är dock möjlig och kanske underskattad: hans oredigerade skills via `github`-källa för det mesta, plus dina egna svenska skills som separata filer i din rot för det fåtal där språket faktiskt spelar roll. Då krymper vendoreringsytan från 101 filer till de få du verkligen skrev om — och synkproblemet krymper i samma proportion. Notera dock att två marketplace-poster som båda levererar en skill med samma namn kräver eftertanke om vilken som vinner, och att en pinnad `ref`/`sha` behöver höjas manuellt för att hans förbättringar ska nå dig alls.

---

## Slutsats

Avvägningarna, hopsamlade:

**Konfliktkvalitet är inte samma sak som konfliktmängd.** Fork+merge och subtree ger *fler* synliga konflikter än vendorering och overlay — men det är för att de är de enda modellerna som faktiskt *upptäcker* att både du och uppström har ändrat samma sak. De andra modellerna har färre konflikter för att de tyst väljer en sida. Med ~100 commits/60 dagar uppströms är tyst drift den dyra felmoden, inte högljudda konflikter.

**Namnbytesdetektering är den tekniska skiljelinjen.** Allt som är en riktig git-merge (fork+merge, fork+rebase, subtree) hanterar omdöpta och raderade filer korrekt. Allt annat (sync-script, patch, overlay) gör det inte, och måste kompensera med manuell uppmärksamhet. Hans `plugin.json` med 25 explicit uppräknade sökvägar gör detta konkret snarare än hypotetiskt.

**Fork-relationen på GitHub ger nästan ingenting utöver knappen.** "Sync fork" och `gh repo sync` slutar fungera exakt när du behöver dem — vid konflikt — och `gh repo sync --force` löser konflikten genom att kasta dina ändringar. Det som återstår är `git merge upstream/main`, och det kommandot fungerar lika bra från ett repo som aldrig varit en fork. Emot forken talar dessutom: permanent "forked from"-märkning, osynlighet i GitHub-sök som default, låst synlighet, och att vägen ut ("Leave fork network") är permanent och kostar issues, PRs, stars och watchers.

**Subtree är fork+merge:s mekanik utan GitHub-kostnaderna**, mot priset av längre kommandon och att du måste skriva din egen `marketplace.json` med `"source": "./vendor/skills"`.

**Submodule svarar inte mot uppgiften** (du kan inte editera hans filer) och bär dessutom en odokumenterad risk i själva pluginlevererandet.

**Vendorering och overlay har lägst löpande kommandokostnad och högst löpande uppmärksamhetskostnad.** De optimerar för att synken ska gå fort, i ett läge där det som är dyrt är att upptäcka vad synken egentligen innebar.

**Storleken på vendoreringsytan är i sig en designparameter.** Om bara ett fåtal skills faktiskt behöver skrivas om på svenska, kan hans övriga skills konsumeras orörda via en `github`-källa i din egen `marketplace.json` — och då blir valet mellan modellerna ovan ett beslut om betydligt färre filer, med proportionerligt mindre insats oavsett vilken modell som väljs.

Kravet att `.claude-plugin/marketplace.json` ligger i repots rot är uppfyllt av samtliga alternativ utom submodule (osäkert) och patch/overlay (kräver att byggresultatet committas). Det är alltså inte kravet som avgör valet.
