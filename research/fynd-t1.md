# Vad är källa och vad är genererat i `mattpocock/skills`?

Metod: repot klonades (shallow) från GitHub och lästes på disk (`/tmp/mps`, HEAD `8b36d4f`, version 1.2.2). Alla påståenden nedan bygger på faktisk filläsning.

**Kort svar: nästan ingenting i repot är genererat.** Det finns inget byggsteg som producerar skills, docs eller manifest. Det enda automatiskt skrivna är `version`-fältet i `.claude-plugin/plugin.json`, plus `CHANGELOG.md` och versionsbumpen som changesets gör vid release.

## 1. `.agents/` vs `skills/` — vilket genereras från vilket?

**Ingetdera.** De är två olika sorters innehåll, ingen genereras från den andra.

- `.agents/` är *maintainer-dokumentation för detta repo* — inte skills. Innehåll: `.agents/install-block.md`, `.agents/invocation.md`, `.agents/writing-docs.md` och `.agents/adr/0001-…md`, `.agents/adr/0002-ship-as-a-claude-code-plugin.md`. `install-block.md` inleds: "One install story, one wording. `README.md`, `.changeset/*`, and every page under `docs/` must say **this** and nothing else. Change it here first, then propagate." Alltså: manuell propagering, inget skript.
- `skills/` är själva produkten: `skills/<bucket>/<skill>/SKILL.md` plus stödfiler och `agents/openai.yaml`. Buckets enligt `CLAUDE.md`: `engineering/`, `productivity/` (promoted), samt `misc/`, `in-progress/`, `deprecated/`.

Notera att namnet `.agents/` här *inte* har med `~/.agents/skills` att göra — den sökvägen dyker upp separat i `scripts/link-skills.sh` som ett installationsmål för Codex-liknande harnesses.

Vad som *ser* generat ut men är handskrivet:

- `skills/*/*/agents/openai.yaml` — Codex-metadata bredvid varje `SKILL.md`. `CHANGELOG.md` 1.2.0 säger uttryckligen: "Add Codex metadata alongside each skill's Claude Code frontmatter so the set works in both harnesses **without generated copies**." De underhålls för hand och måste hållas i synk manuellt (`.agents/invocation.md`: "Keep the two in sync: a skill is user-invoked in both harnesses or neither.").
- `docs/<bucket>/<skill>.md` — människo-riktade sidor som publiceras på `https://aihero.dev/skills-<skill-name>`. De speglar `skills/engineering/` och `skills/productivity/` men är **skrivna för hand** enligt mallen i `.agents/writing-docs.md`: "The page is not the skill and not a copy of `SKILL.md`… Act whenever a promoted skill is added, renamed, or has its behaviour changed: create or re-sync its docs page." Re-sync är en instruktion till en agent, inte ett skript.
- `AGENTS.md` är en **symlink till `CLAUDE.md`** (`git ls-files -s` visar mode `120000`, `readlink AGENTS.md` → `CLAUDE.md`). Det är den enda "spegling" i repot som är mekanisk.

## 2. `scripts/` och `package.json`

`package.json` scripts-sektion, i sin helhet:

```json
"scripts": {
  "changeset": "changeset",
  "version": "changeset version && node scripts/sync-plugin-version.mjs",
  "check-plugin-version": "node scripts/sync-plugin-version.mjs --check"
}
```

Det finns inget `build`, inget `generate`. `private: true`, inget npm-publish.

- `scripts/sync-plugin-version.mjs` — **det enda skriptet som skriver in i repot.** Kopierar `package.json`s `version` till `.claude-plugin/plugin.json` och byter bara ut versionsraden ("Rewrite only the version line, to keep the key order and the formatting"). `--check` skriver inget och exitar 1 vid drift.
- `scripts/link-skills.sh` — dev-verktyg som symlänkar varje skill-mapp med `SKILL.md` (exklusive `deprecated/`) in i `~/.claude/skills` och `~/.agents/skills`. Skriptets egen header: "This is a dev-only script, intended for use by maintainers of this repo. It is not a supported installer. Modifications to it — or requests for modifications — will not be approved." Det skriver alltså **utanför** repot, inte in i det (och har en explicit vakt mot att skriva tillbaka in i repots `skills/`-träd).
- `scripts/list-skills.sh` — `find . -name SKILL.md | sort`. Ren utskrift, inga sidoeffekter.

`.github/workflows/release.yml` är enda workflow: på push till `main` kör `changesets/action@v1` med `version: npm run version` och `publish: npx changeset tag`. Det är där `CHANGELOG.md`, `package.json`-versionen och `plugin.json`-versionen skrivs — via en release-PR ("chore: version skills"). Jag hittade **ingen** CI som kör `check-plugin-version` eller `claude plugin validate`.

## 3. `.claude-plugin/plugin.json` vs `marketplace.json`

- `plugin.json` styr **vilka skills som faktiskt ingår i Claude Code-pluginet**, via en handskriven `skills`-array med 25 sökvägar (`"./skills/engineering/ask-matt"` … `"./skills/productivity/writing-for-agents"`). Plus namn, version, beskrivning, författare, keywords. `CLAUDE.md`: "Every skill in `engineering/` or `productivity/` (the **promoted** buckets) must have … an entry in `.claude-plugin/plugin.json`'s `skills` array (the Claude Code plugin ships exactly the promoted set). Skills in `misc/`, `in-progress/`, and `deprecated/` must not appear in either." Listan underhålls manuellt; bara `version` rörs av skript.
- `marketplace.json` gör repot till sin **egen enpluggs-marketplace** (`plugins: [{ name: "mattpocock-skills", source: "./" }]`). Enligt `.agents/install-block.md` är detta uttryckligen *inte* den dokumenterade installationsvägen: "The official listing supersedes it. It is kept as a fallback for installing the repo directly — an unreleased commit, **or a fork** — and is **not** documented to users."

Den sista meningen är direkt relevant för fork-frågan (se Slutsats).

## 4. `.out-of-scope/` och `.changeset/`

- `.out-of-scope/` = **dokumenterade nej.** Tre filer (`mainstream-issue-trackers-only.md`, `question-limits.md`, `setup-skill-verify-mode.md`), var och en med rubrikerna "Why this is out of scope" och "Prior requests" som pekar på issue-nummer (#99, #44, #106). Det är en triage-artefakt för att slippa återuppta samma feature request. Jämför `skills/engineering/triage/OUT-OF-SCOPE.md` som är samma mönster inbakat i triage-skillen.
- `.changeset/` = versionshantering med [changesets](https://github.com/changesets/changesets). `.changeset/config.json` har `privatePackages: { version: true, tag: true }`, `baseBranch: "main"` och changelog-genererare `@changesets/changelog-github`. Varje PR lägger en changeset-markdownfil; release-workflowet konsumerar dem till `CHANGELOG.md` + versionsbump. **`CHANGELOG.md` är alltså genererad.** (Vid läsningen låg inga öppna changeset-filer kvar — bara `README.md` och `config.json`.)

## 5. `CONTEXT.md`, `CLAUDE.md`, `AGENTS.md` — underhållsreglerna

`AGENTS.md` === `CLAUDE.md` (symlink). Den filen är repots underhållskontrakt och är i praktiken en checklista för vad som måste hållas i synk **för hand** när man rör en skill:

1. Bucket-placering avgör allt: promoted (`engineering/`, `productivity/`) vs icke-promoted.
2. En promoted skill kräver: rad i topp-`README.md` (med länk till dess `SKILL.md`), rad i bucketens `README.md`, entry i `plugin.json`s `skills`-array, och en docs-sida `docs/<bucket>/<namn>.md`.
3. Icke-promoted skills får *inte* finnas i `README.md` eller `plugin.json` och får ingen docs-sida.
4. Varje `SKILL.md` är antingen user-invoked (`disable-model-invocation: true` + `policy.allow_implicit_invocation: false` i `agents/openai.yaml`) eller model-invoked — se `.agents/invocation.md`.
5. `ask-matt` är routern: "whenever you add, rename, remove, or change how a user-reachable skill fits the flows, re-read `ask-matt`'s `SKILL.md` and update it… a new skill it never mentions, or a stale one it still routes to, is a router that lies."
6. Installkommandon kopieras ordagrant från `.agents/install-block.md`; kör `claude plugin validate . --strict` efter ändring i manifesten.
7. `scripts/link-skills.sh` körs om efter add/remove/rename.

`CONTEXT.md` är däremot **inte** om repots underhåll utan repots *domänmodell* — den delade vokabulären: **Issue tracker**, **Issue**, **Decision ticket**, **Triage role**, plus "Relationships" och "Flagged ambiguities" (t.ex. att "backlog" avskaffats som term). Den följer formatet i `skills/engineering/domain-modeling/CONTEXT-FORMAT.md` — repot dogfoodar sina egna skills.

Alltså: hela "byggsystemet" är prosa-instruktioner till en agent, inte kod. Det är en medveten design (`README.md`: "These skills are designed to be small, easy to adapt, and composable… Hack around with them. Make them your own.").

## 6. Dokumenterad väg för egna/anpassade skills?

**Nej — inte för att bidra egna skills till repot, och ingen CONTRIBUTING.md finns.** Vad som finns:

- `README.md` beskriver två installationsvägar med olika filosofi, ordagrant: "**The Claude Code plugin** installs the whole set as a managed, read-only bundle that updates when I ship — you subscribe rather than fork. **skills.sh** copies editable skill files into your project, so you can hack on them and make them your own. Pick one — installing both leaves you with every skill twice."
- Alltså: den dokumenterade vägen till *anpassning* är `npx skills@latest add mattpocock/skills` (skills.sh), som "writes the skills into your repo as ordinary files you own and can edit. Nothing updates behind your back; pull my latest changes when you want them with `npx skills update`." Det är kopior i ditt eget repo — inte en fork av hans.
- `skills/productivity/writing-for-agents/` (+ `SKILL-MECHANICS.md`) är den skill som lär en agent skriva nya skills. Det är närmaste sak till en "så skriver du en egen skill"-guide.
- `docs/` är slutanvändardokumentation per skill, inte bidragsdokumentation.
- `.out-of-scope/` visar vad som *inte* tas emot; `scripts/link-skills.sh` säger uttryckligen att ändringsförslag till just det skriptet inte godkänns.

Osäkert/ej fastställt: om det finns issue-mallar eller bidragsregler i `.github/` utöver workflowet — `.github/` innehöll bara `workflows/release.yml` i den klonade träden.

## Slutsats

Om du forkar repot, editerar `skills/engineering/wayfinder/SKILL.md` och lägger till en egen skill:

**Du editerar (allt är källa, inget bygge rör dem):**

- `skills/engineering/wayfinder/SKILL.md` — direkt. Inget genererar den, inget skriver över den. Samma för alla `SKILL.md` och deras stödfiler.
- För en egen skill: skapa `skills/<bucket>/<namn>/SKILL.md` (+ valfritt `agents/openai.yaml` om du kör Codex), lägg till sökvägen i `.claude-plugin/plugin.json`s `skills`-array om den ska ingå i pluginet, samt rader i `README.md` och `skills/<bucket>/README.md` och en sida i `docs/` om du vill följa husreglerna. Allt det är handarbete — `CLAUDE.md` beskriver det som en checklista, inte som ett skript.

**Risk för överskrivning — mycket liten, och den kommer inte från ett bygge:**

- Endast `version`-fältet i `.claude-plugin/plugin.json` skrivs maskinellt (`scripts/sync-plugin-version.mjs`, via `npm run version`). Dina `skills`-entries rörs inte — skriptet byter bokstavligen bara ut versionsträngen med en regex.
- `CHANGELOG.md` och `package.json`s `version` ägs av changesets/release-workflowet.
- `AGENTS.md` är en symlink — editerar du den editerar du `CLAUDE.md`.
- Kör du `scripts/link-skills.sh` skriver det symlänkar i `~/.claude/skills` och `~/.agents/skills` — utanför repot, men det **skriver över** befintliga poster där med samma namn (`rm -rf` på icke-symlänkar). Det är den enda destruktiva operationen i repot.

**Den verkliga risken i en fork är merge-konflikter, inte generering.** Upstream editerar exakt samma `SKILL.md`-filer som du, så varje `git pull` från mattpocock/skills kolliderar med dina ändringar rad för rad. Repots eget svar på det är att man **inte ska forka för att anpassa**: `README.md` säger "you subscribe rather than fork" om pluginvägen och pekar hackers till `npx skills@latest add mattpocock/skills`, som kopierar in filerna i ditt eget projekt där du äger dem. Fork-vägen är enligt `.agents/install-block.md` bara tänkt som fallback för installation ("an unreleased commit, or a fork") via `marketplace.json` — `/plugin marketplace add <din-fork>` följt av `/plugin install mattpocock-skills@mattpocock` — och den vägen är uttryckligen odokumenterad för användare.

Praktiskt: forka om du vill *drifta pluginet själv* (då är `marketplace.json` + `plugin.json` dina knappar); kopiera in via skills.sh om du bara vill hacka på en handfull skills och slippa merge-smärtan.
