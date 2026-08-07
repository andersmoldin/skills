# skills

Mitt superset av Matt Pococks skills — hans uppsättning plus mina egna, på svenska.

## Status: beslutad, ännu inte byggd

Repot innehåller i nuläget bara besluten. Uppsättningen — `.claude-plugin/`, den vendorerade
kopian av hans skills och mina egna — är inte byggd än.

**[`SPEC.md`](SPEC.md) är byggunderlaget.** Den beskriver vald synkmodell, repostruktur, namnrymd,
uppdateringsrutin, licens och migrering, och ska räcka för att bygga uppsättningen utan att fatta
fler beslut. Besluten bakom den redovisas i ärendena [#5](../../issues/5)–[#10](../../issues/10).

När uppsättningen är byggd installeras den så här:

```bash
claude plugin marketplace add andersmoldin/skills
claude plugin install moldin-skills@moldin --scope user
```

## Attribution

Grunden i det här repot är [Matt Pococks skills](https://github.com/mattpocock/skills) (MIT).
Hans arbete kommer att ligga orört i `vendor/matt/`; mina ändringar är översättningar och
justeringar ovanpå det.

**Det här är inte Matts officiella distribution.** Vill du ha hans uppsättning som han avsett den,
installera `mattpocock-skills` från Anthropics officiella marketplace, eller följ hans README.

## Licens

MIT — se [`SPEC.md` §7](SPEC.md) för hur licens och attribution ska se ut i det färdiga repot.
