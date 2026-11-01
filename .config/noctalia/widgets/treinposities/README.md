# Treinposities.nl Waybar Widget & Trip Planner

Een geavanceerde Waybar module die real-time data van **treinposities.nl** gebruikt voor actuele vertrektijden, materieel- en positietracking, en een complete interactieve reisplanner.

---

## 🚆 Functionaliteiten

1. **Actuele Vertrektijden (Live Station Departures)**:
   - Toont actuele vertrektijd, geplande tijd, vertragingen (`+2`, `+10`), en gewijzigde sporen (`!Sp.7`).
   - Herkent uitval (`[Rijdt niet]` / doorgestreept).
   - Real-time materieelinformatie en treinpositie: toont treinstelnummers (bijv. `VIRM-4 9567`, `SNG 2333`), treinsnelheid & afstand (bijv. `65km/u - 1.4km`) of `Aan perron`.
   - Kleurgecodeerde status: groen (op tijd), oranje (vertraging), rood (kritieke vertraging / uitval).

2. **Reisplanner (Trip Planner / Woon-werk)**:
   - Plant treinreizen tussen vertrek- en bestemmingsstation via treinposities.nl.
   - Toont reistijd, aantal overstappen, en alle deeltrajecten met vertreksporen, aankomstsporen en vertragingen.
   - Toont ingezet materieel per deeltraject.
   - Snelle wisselknop om richting om te draaien (heenreis ⬄ terugreis).

3. **Interactief Menu (Rofi Integratie)**:
   - **Links-klik**: Hoofdmenu met vertrektijden bekijken, station wisselen (fuzzy search over 410+ stations), reis plannen, modus wisselen of favorieten kiezen.
   - **Rechts-klik**: Direct de Reisplanner openen.
   - **Midden-klik**: Modus wisselen tussen *Station Vertrektijden* en *Reisplanner*.
   - **Scroll Omhoog**: Volgend favoriet station selecteren.
   - **Scroll Omlaag**: Reisrichting omdraaien (bijv. Utrecht ➔ Amsterdam naar Amsterdam ➔ Utrecht).

4. **Klembord & Browser integratie**:
   - Reisadvies of treingegevens kopiëren naar klembord (`wl-copy`).
   - Direct openen op treinposities.nl in de browser via één klik.

---

## ⚙️ Configuratie

Het configuratiebestand staat in:
`~/.config/waybar/scripts/treinposities/config.json`

```json
{
  "mode": "station",
  "current_station": "Utrecht Centraal",
  "trip_from": "Utrecht Centraal",
  "trip_to": "Amsterdam Centraal",
  "favorites": [
    "Utrecht Centraal",
    "Amsterdam Centraal",
    "Rotterdam Centraal",
    "Den Haag Centraal",
    "Schiphol Airport",
    "Eindhoven Centraal",
    "Arnhem Centraal"
  ],
  "max_tooltip_departures": 10,
  "max_tooltip_trips": 4,
  "show_material": true,
  "cache_ttl_seconds": 25,
  "waybar_signal": 8
}
```

### Instellingen:
- `mode`: `"station"` (toont volgende vertrekkende trein) of `"trip"` (toont volgende geplande reis).
- `current_station`: Huidig gekozen station voor vertrektijden (naam, afkorting of slug).
- `trip_from`: Standaard vertrekstation voor de reisplanner.
- `trip_to`: Standaard bestemmingsstation voor de reisplanner.
- `favorites`: Lijst met favoriete stations om snel doorheen te scrollen.
- `max_tooltip_departures`: Aantal vertrekkende treinen in de tooltip tabel.
- `show_material`: Toon treinstelnummers en snelheden/perronstatus.
- `cache_ttl_seconds`: Lokale cache TTL (voorkomt onnodige requests).
- `waybar_signal`: RTMIN signaalnummer (`pkill -RTMIN+8 waybar`) voor directe updates.

---

## ⌨️ CLI Commando's

Je kunt het script ook handmatig aanroepen vanuit een terminal of sneltoets:

```bash
# Output JSON voor Waybar
~/.config/waybar/scripts/treinposities/treinposities.py waybar

# Open het interactieve Rofi hoofdmenu
~/.config/waybar/scripts/treinposities/treinposities.py menu

# Open direct de Reisplanner in Rofi
~/.config/waybar/scripts/treinposities/treinposities.py plan

# Kies een ander station
~/.config/waybar/scripts/treinposities/treinposities.py station

# Wissel tussen Station- en Reisplanner modus
~/.config/waybar/scripts/treinposities/treinposities.py toggle-mode

# Draai de reisrichting van de reisplanner om
~/.config/waybar/scripts/treinposities/treinposities.py swap-trip

# Schakel naar het volgende favoriete station
~/.config/waybar/scripts/treinposities/treinposities.py next-favorite

# Cache wissen en widget direct verversen
~/.config/waybar/scripts/treinposities/treinposities.py refresh
```
