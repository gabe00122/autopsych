# Draft Fermi family roster: human review view

Status: **structurally valid draft; scientifically unreviewed; not preregistered**.

The machine-readable authority is `fermi_family_roster.json`. This view is for
concept review only. The 250 reserved IDs are nonnumeric slots, not candidate
items. No family below has passed AI construction, blind challenge,
deterministic calculation, Wolfram Alpha, source verification, or human review.

| Domain | ID | Proposed family | Provisional class | Main construct risk |
|---|---|---|---|---|
| Physical | PHY-01 | Annual rooftop solar electricity | A | Roof usability, shading, and AC/DC scope |
| Physical | PHY-02 | Annual wind-farm electricity | A | Site-specific capacity factor |
| Physical | PHY-03 | Annual captured stormwater volume | B | Capture efficiency may be system-specific or arbitrary |
| Physical | PHY-04 | Water mass contained in fresh snow | B | Snow density changes rapidly |
| Physical | PHY-05 | Annual commercial-building site energy | A | Activity and climate strata may interact |
| Geographical-demographic | GEO-01 | Annual live births | A | Crude birth rate depends strongly on age structure |
| Geographical-demographic | GEO-02 | Occupied households and housing demand | A | Households and housing units are distinct estimands |
| Geographical-demographic | GEO-03 | Public K-12 enrollment | A | Grade coverage and private/homeschool treatment |
| Geographical-demographic | GEO-04 | Annual commute trips | A | Hybrid work makes frequency time-sensitive |
| Geographical-demographic | GEO-05 | Annual municipal solid waste generation | A | Generated and discarded waste are often conflated |
| Technological | TEC-01 | Annual data-center electricity | A | Nameplate IT power is not average IT load |
| Technological | TEC-02 | Annual electric-vehicle charging demand | A | Vehicle-side and grid-side energy differ |
| Technological | TEC-03 | Annual streetlight electricity | B | Fixture spacing and control profiles vary |
| Technological | TEC-04 | Annual seawater reverse-osmosis electricity | A | Process-only and whole-site electricity are easily conflated |
| Technological | TEC-05 | Battery-pack mass for usable storage | B | Cell and pack specific energy differ |
| Economic | ECO-01 | Annual food-at-home expenditure | A | Consumer units are not households; price-year drift |
| Economic | ECO-02 | Annual food-services sales | A | Tourism and commuter leakage can dominate |
| Economic | ECO-03 | Annual industry payroll | A | Wages and total compensation differ |
| Economic | ECO-04 | Annual general sales-tax revenue | A | Effective tax base is jurisdiction-specific |
| Economic | ECO-05 | Annual residential-electricity expenditure | A | Customer and household counts differ |
| Biological | BIO-01 | Annual dairy-milk production | A | Herd definition and production system |
| Biological | BIO-02 | Annual table-egg production | A | Table versus hatching eggs; inventory timing |
| Biological | BIO-03 | Annual urban-tree carbon sequestration | B | Species, size, condition, and gross/net scope |
| Biological | BIO-04 | Annual companion-animal dry-food demand | B | Animal-size distribution and wet-food substitution |
| Biological | BIO-05 | Annual domestic wastewater nitrogen load | B | Industrial load and collection boundaries |

## Candid review priorities

1. **Freeze the TEC-04 system boundary before sourcing.** Intake, pretreatment,
   high-pressure pumping, energy recovery, and post-treatment must be included
   or excluded consistently. A plant-level electricity back-check cannot be
   compared with a process-only estimate.
2. **Freeze the estimands before sourcing.** Several families have common but
   consequential category errors: site versus source energy, households versus
   housing units, generated versus discarded waste, and gross versus net carbon.
3. **Do not mistake official data for construct validity.** An authoritative
   table can still measure a different population, year, geography, or boundary.
4. **Keep time-varying economic quantities versioned.** Every monetary family
   needs a price year and a rule for nominal versus real dollars.
5. **Reject families whose uncertainty is driven mainly by arbitrary system
   design.** Parameterization should vary supplied inputs, not conceal unresolved
   choices inside bridge quantities.

## Human decision requested before packet construction

For each family, record `retain for packet construction`, `redesign`, or
`replace`. Structural validation is not a reason to retain a weak construct.
