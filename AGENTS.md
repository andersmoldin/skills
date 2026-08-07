# Project agent memory

This file is the project's committed home for project-intrinsic agent knowledge: build, test, release, architecture, and sharp-edge notes that should travel with the code.

## Vad det här repot är

Ett Claude Code plugin-marketplace som ska innehålla Matt Pococks skills (vendorerade och delvis
översatta) plus egna. **Ännu inte byggt** — [`SPEC.md`](SPEC.md) är byggunderlaget och den
auktoritativa källan till repostruktur, namn, uppdateringsrutin och migrering. Läs den före arbete
som rör uppsättningen. Besluten bakom den ligger i ärendena #5–#10.

## Språk

Allt publikt i det här repot skrivs **på svenska**: ärenden, resolutioner, commit-meddelanden,
PR-titlar och PR-texter, dokumentation. Stående preferens från repoägaren (#1).

Undantag: namn i `marketplace.json`/`plugin.json` och skill-katalognamn måste vara kebab-case
(`a-z0-9-`), så åäö är uteslutet **där** — men inte i dokumentfilnamn eller prosa.

## Sharp edges

- Verifiera påståenden om Claude Codes plugin-mekanik mot primärkälla (code.claude.com, den
  installerade pluginens filer, `claude plugin --help`) i stället för mot minnet. `SPEC.md` §10
  listar vad som är verifierat empiriskt, vad som bara är verifierat mot dokumentation, och två
  korrigeringar av tidigare fastställda uppgifter.
- Testa aldrig plugin-installation mot den globala uppsättningen. Sätt `CLAUDE_CONFIG_DIR` till en
  engångskatalog — det isolerar marketplaces, cache och installerade plugins fullständigt.
- Rör inte den installerade `mattpocock-skills` utan uttryckligt uppdrag.

## Maintaining this file

Keep this file for knowledge useful to almost every future agent session in this project.
Do not repeat what the codebase already shows; point to the authoritative file or command instead.
Prefer rewriting or pruning existing entries over appending new ones.
When updating this file, preserve this bar for all agents and keep entries concise.
