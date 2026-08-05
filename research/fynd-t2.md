# Egna Plugin-Marketplaces i Claude Code — Utreda Mot Dokumentation

**Forskningsdatum:** 2026-08-05  
**Källa:** https://code.claude.com/docs/en/ (plugin-marketplaces.md, plugins.md, plugins-reference.md, discover-plugins.md)

---

## 1. Syntax för att lägga till eget marketplace från GitHub-repo

**VERIFIERAT I DOCS:**

### Från session (interaktiv)
```
/plugin marketplace add owner/repo
/plugin marketplace add owner/repo@branch-or-tag
```

### Från terminal (non-interaktiv)
```bash
claude plugin marketplace add owner/repo
claude plugin marketplace add owner/repo@ref  # pin till branch/tag
```

### Från andra git-hosts
```
/plugin marketplace add https://gitlab.com/company/plugins.git
/plugin marketplace add git@gitlab.com:company/plugins.git
```

### Från lokal path
```
/plugin marketplace add ./my-marketplace
```

**Viktigt:** URL utan scheme (t.ex. `gitlab.example.com/team/plugins.git`) avvisas som ogiltig från v2.1.196. Måste ha `https://` eller `git@`.

---

## 2. Repo-struktur och obligatoriska fält

**VERIFIERAT I DOCS:**

### Placeringskrav

```
marketplace-repo/
├── .claude-plugin/
│   └── marketplace.json          # MÅSTE ligga här
└── plugins/
    └── min-plugin/
        ├── .claude-plugin/
        │   └── plugin.json       # MÅSTE ligga här
        ├── skills/
        │   └── skill-name/
        │       └── SKILL.md
        └── ... (agents, hooks, etc.)
```

**marketplace.json-placeringen:** `.claude-plugin/marketplace.json` i marketplace-roten (den mapp som innehåller `.claude-plugin/`)

**plugin.json-placeringen:** `.claude-plugin/plugin.json` i varje plugins rot

### Obligatoriska fält i marketplace.json

```json
{
  "name": "my-marketplace",           // OBLIGATORISK. Kebab-case, unik per användare
  "owner": {                          // OBLIGATORISK
    "name": "Din Namn"                // OBLIGATORISK
  },
  "plugins": [                        // OBLIGATORISK (minst ett entry)
    {
      "name": "plugin-name",          // OBLIGATORISK
      "source": "./plugins/plugin-name" // OBLIGATORISK
    }
  ]
}
```

Valfria marketplace-fält: `description`, `version`, `metadata.pluginRoot`, `allowCrossMarketplaceDependenciesOn`, `renames`

### Obligatoriska fält i plugin.json

Enligt docs: **`name` är enda obligatoriska fältet om manifest inkluderas.**

```json
{
  "name": "min-plugin",               // OBLIGATORISK
  "description": "Beskrivning",       // Rekommenderat
  "version": "1.0.0",                 // Valfritt (se versionering nedan)
  "author": {
    "name": "Ditt Namn"
  }
}
```

---

## 3. Auto-uppdateringar och versionering

**VERIFIERAT I DOCS:**

### Hämtas uppdateringar automatiskt?

**Ja, för Anthropics officiella marketplace.** För anpassade marketplaces:
- **Default:** Auto-update är **inaktiverat** för tredjepartsmarketplaces
- **Aktivering:** Kan aktiveras manuellt via `/plugin` > Marketplaces, eller via `"autoUpdate": true` i `extraKnownMarketplaces` i managed settings

### Kommando för manuell uppdatering
```
/plugin marketplace update <marketplace-name>
claude plugin marketplace update <marketplace-name>  # Terminal
```

### Versionering — prioritetsordning

Claude Code löser version från denna ordning:

1. **`version` i plugin.json** (högsta prioritet)
2. **`version` i marketplace-entry**
3. **Git commit SHA** (fallback om inget av ovanstående är satt)

**Viktigt:** Om `version` är satt i både plugin.json och marketplace-entry använder Claude Code plugin.json-värdet utan varning.

**Rekommendation från docs:** För aktivt utvecklade plugins — utelämna `version` helt för att använda commit SHA. Då är varje commit en ny version automatiskt.

---

## 4. Namnkollisioner mellan marketplaces

**VERIFIERAT I DOCS:**

### Marketplace-namn
- **Måste vara unika per användare:** "Each user can register only one marketplace per name: adding a second marketplace with the same name replaces the first."
- Om du lägger till två marketplaces med samma namn — den senare ERSÄTTER den första

### Plugin-namn inom en marketplace
- Måste vara unika **inom samma marketplace**
- Kan inte ha samma namn om de är i **samma marketplace.json**

### Mellan marketplaces — samma skill-namn (t.ex. två "wayfinder")
**Docs säger:** Skills är **namespaced** per plugin:
```
/plugin-name:skill-name
/mattpocock-skills:wayfinder
/other-marketplace:wayfinder
```

**Slutsats:** Två marketplaces **kan** båda tillhandahålla en skill med samma namn (t.ex. `wayfinder`). Inga kollisioner. Anledningen: namnrymd är `plugin-name`, inte marketplace-namn.

**Prefixet `mattpocock-skills:`** är inte en officiell namnrymd — det är bara plugin-namnet. Det är ett exempel på hur någon publicerat sina plugins (alla under ett plugin-namn som tillhandahåller flera skills).

### Cross-marketplace dependencies
Docs nämner `allowCrossMarketplaceDependenciesOn` för att en marketplace får förlita sig på plugins från andra marketplaces. Collisioner hanteras genom denna whitelist.

---

## 5. Non-ASCII-tecken (å, ä, ö) i skill-namn

**VERIFIERAT I DOCS:**

### Officiell kravspecifikation

Plugin-namn (i plugin.json `name`): **Kebab-case, no spaces**

Docs säger ordagrant:
> Plugin name "x" is not kebab-case: the plugin name contains uppercase letters, spaces, or special characters. **Rename to lowercase letters, digits, and hyphens only**

**Slutsats:** Endast `a-z`, `0-9`, och `-` är tillåtna. Icke-ASCII-tecken (å, ä, ö) är **INTE tillåtna**.

### I katalognamn under `skills/`

Skill-namn härleds från mapp-namn: `skills/min-skill/SKILL.md` → skill-namn blir `min-skill`

Docs tillåter frontmatter-fält `name` i SKILL.md för att ändra namn. Samma regel gäller: kebab-case.

### I slash-kommandon

Skill-kommandot: `/plugin-name:skill-name`

Samma krav: `skill-name` måste vara kebab-case (så ingen å, ä, ö).

### Varning från validator

`claude plugin validate` rapporterar varning:
> Plugin name "x" is not kebab-case

Men **innan v2.1.221** rapporterades detta inte. Från v2.1.221+ är det ett varning (icke-blockerande).

---

## 6. Global vs per-projekt installation

**VERIFIERAT I DOCS:**

### User scope (GLOBAL)
- **Settings-fil:** `~/.claude/settings.json`
- **Cache:** `~/.claude/plugins/cache/`
- **Marketplace-state:** `~/.claude/plugins/known_marketplaces.json`
- **Synk:** Automatiskt på användarens maskin; måste installeras manuellt på andra maskiner
- **Tillgång:** Alla projekt på datorn
- **Kommando:** `/plugin install plugin-name --scope user` (standard)

### Project scope
- **Settings-fil:** `.claude/settings.json` (i repo)
- **Delas via:** Git — alla som cloner repot ser samma plugins
- **Installation:** Användaren måste godkänna workspace-trust innan plugins laddar
- **Kommando:** `/plugin install plugin-name --scope project`

### Local scope
- **Settings-fil:** `.claude/settings.local.json` (gitignorerad)
- **Användare:** Bara dig själv i det här projektet
- **Delas:** Nej
- **Kommando:** `/plugin install plugin-name --scope local`

### Vad synkas mellan maskiner

| Vad | User | Project | Local |
|-----|------|---------|-------|
| Installer-metadata | `~/.claude/settings.json` | `.claude/settings.json` (version control) | `.claude/settings.local.json` (NOT synced) |
| Plugin-cache | `~/.claude/plugins/cache/` | Shared, copied per machine | Shared, copied per machine |
| Marketplace-registry | `~/.claude/plugins/known_marketplaces.json` | N/A | N/A |

**Slutsats:** Plugin-filerna själva lagras i `~/.claude/plugins/cache/` per maskin. Om någon i repot installerar ett plugin med project-scope, blir det listad i `.claude/settings.json` men **måste repullad från marketplace på varje ny maskin**. Ingen fil synkas — bara "detta plugin är installerat"-informationen.

---

## 7. Installation direkt från git-repo utan marketplace

**VERIFIERAT I DOCS:**

### Svar: JA, men endast för testing

**För development/testing:**
```bash
claude --plugin-dir ./min-plugin
```

Detta laddar pluginen för den sessionen. `--plugin-dir` är inte permanent.

**För URL-baserad testing:**
```bash
claude --plugin-url https://example.com/my-plugin.zip
```

### För permanent installation

Du **måste** skapa en marketplace. Alternativ:

1. **Skapa en marketplace-repo** med `.claude-plugin/marketplace.json` och publicera på GitHub
2. **Använd skills-dir** — en plugin under `~/.claude/skills/plugin-name/` med `.claude-plugin/plugin.json` laddar automatiskt som `plugin-name@skills-dir`

Det finns **inget sätt att installera direkt från ett git-repo utan en marketplace eller --plugin-dir**.

---

## Slutsats

För någon som vill **publicera ett eget superset av annans skills:**

1. **Skapa en marketplace-repo:** en GitHub-repo (eller GitLab/privat git) med en `.claude-plugin/marketplace.json`
2. **Namngivning:** Använd ett unikt marketplace-namn (kebab-case, a-z0-9-) — detta måste inte matcha andre marketplaces-namn, men om två person installerar två marketplaces med samma namn ersätter den senare den första
3. **Plugin-namn:** Varje plugin i din marketplace måste ha ett unikt namn (kebab-case) för att undvika interna kollisioner
4. **Skill-namngivning:** Skills blir namespaced automatiskt: `/ditt-plugin-namn:skill-name`. Om någon annan publicerar samma skill-namn under ett annat plugin-namn — ingen konflikt, för namnrymden är pluginet
5. **Versioning:** Välj en strategi — explicit version eller commit SHA. Commits SHA är enklare för aktivt utvecklade plugins
6. **Icke-ASCII:** Använd enbart a-z, 0-9, och hyphen i alla namn. Svenska tecken (å, ä, ö) är INTE tillåtna
7. **Synk mellan maskiner:** Endast installationsinformationen synkas via `.claude/settings.json`. Plugin-filerna måste repullad från din marketplace på varje ny maskin

**Nyckel-fördel:** Din marketplace kan vara privat (GitHub private repo) och fungerar med organization-auth. Eller offentlig. Eller lokal (`./path/to/marketplace`).

---

## Källhänvisningar

- https://code.claude.com/docs/en/plugin-marketplaces.md — Create and distribute a plugin marketplace
- https://code.claude.com/docs/en/plugins.md — Create plugins
- https://code.claude.com/docs/en/plugins-reference.md — Plugins reference (schema, CLI commands)
- https://code.claude.com/docs/en/discover-plugins.md — Discover and install prebuilt plugins

**Notering:** All information är från officiell Claude Code-dokumentation hämtad 2026-08-05. Ingen information är gissad från min träningdata.
