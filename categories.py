"""
categories.py

Lookup tables for the "Politikbereich" (policy area) codes used in the
d1e1/d1e2/d1e3, d2e1/d2e2/d2e3 and d3e1/d3e2/d3e3 fields (a vote can be
tagged with up to three policy areas, each a 3-level hierarchy).

Transcribed from data/data.pdf (the Swissvotes codebook), section
"Politikbereich" -- itself licensed CC BY 4.0, see LICENSE-DATA.

Code format, as it appears in data/swissvotes.ch.csv:
    "x"    -> top-level code    (e.g. "1"),    resolved via LEVEL1
    "x.y"  -> second-level code (e.g. "1.2"),  resolved via LEVEL2
    "x.yz" -> third-level code  (e.g. "1.21"), resolved via LEVEL3
              (the dot before the 3rd digit is dropped in the source data,
              i.e. "1.21" stands for "1.2.1")
"." (or any other unrecognized code) means "not assigned" and is left as-is.
"""

LEVEL1 = {
    "1": "Staatsordnung",
    "2": "Aussenpolitik",
    "3": "Sicherheitspolitik",
    "4": "Wirtschaft",
    "5": "Landwirtschaft",
    "6": "Öffentliche Finanzen",
    "7": "Energie",
    "8": "Verkehr und Infrastruktur",
    "9": "Umwelt und Lebensraum",
    "10": "Sozial- und Gesellschaftspolitik",
    "11": "Bildung und Forschung",
    "12": "Kultur, Religion, Medien",
}

LEVEL2 = {
    "1.1": "Nationale Identität",
    "1.2": "Politisches System",
    "1.3": "Institutionen",
    "1.4": "Volksrechte",
    "1.5": "Föderalismus",
    "1.6": "Rechtsordnung",
    "2.1": "Aussenpolitische Grundhaltung",
    "2.2": "Europapolitik",
    "2.3": "Internationale Organisationen",
    "2.4": "Entwicklungszusammenarbeit",
    "2.5": "Staatsverträge mit einzelnen Staaten",
    "2.6": "Aussenwirtschaftspolitik",
    "2.7": "Diplomatie",
    "2.8": "Auslandschweizer:innen",
    "3.1": "Öffentliche Sicherheit",
    "3.2": "Armee",
    "3.3": "Landesversorgung",
    "4.1": "Wirtschaftspolitik",
    "4.2": "Arbeit und Beschäftigung",
    "4.3": "Finanzwesen",
    "4.4": "Freizeit und Tourismus",
    "5.1": "Agrarpolitik",
    "5.2": "Tierische Produktion",
    "5.3": "Pflanzliche Produktion",
    "5.4": "Forstwirtschaft",
    "5.5": "Fischerei, Jagd, Haustiere",
    "6.1": "Steuerwesen",
    "6.2": "Finanzordnung",
    "6.3": "Öffentliche Ausgaben",
    "6.4": "Spar- und Sanierungsmassnahmen",
    "7.1": "Energiepolitik",
    "7.2": "Kernenergie",
    "7.3": "Wasserkraft",
    "7.4": "Alternativenergien",
    "7.5": "Erdöl, Gas",
    "8.1": "Verkehrspolitik",
    "8.2": "Strassenverkehr",
    "8.3": "Schienenverkehr",
    "8.4": "Luftverkehr",
    "8.5": "Schifffahrt",
    "8.6": "Post",
    "8.7": "Telekommunikation",
    "9.1": "Boden",
    "9.2": "Wohnen",
    "9.3": "Umwelt",
    "10.1": "Gesundheit",
    "10.2": "Sozialversicherungen",
    "10.3": "Gesellschaftsfragen",
    "11.1": "Bildungspolitik",
    "11.2": "Schulen",
    "11.3": "Hochschulen",
    "11.4": "Forschung",
    "11.5": "Berufsbildung",
    "12.1": "Kulturpolitik",
    "12.2": "Sprachpolitik",
    "12.3": "Religion, Kirchen",
    "12.4": "Sport",
    "12.5": "Medien und Kommunikation",
}

LEVEL3 = {
    "1.21": "Bundesverfassung",
    "1.22": "Verfassungsgebungsverfahren",
    "1.23": "Gesetzgebungsverfahren",
    "1.24": "Wahlsystem",
    "1.31": "Regierung, Verwaltung",
    "1.32": "Parlament",
    "1.33": "Gerichte",
    "1.34": "Nationalbank",
    "1.41": "Initiative",
    "1.42": "Referendum",
    "1.43": "Stimmrecht",
    "1.51": "Territorialfragen",
    "1.52": "Beziehungen zwischen Bund und Kantonen",
    "1.53": "Aufgabenteilung",
    "1.61": "Internationales Recht",
    "1.62": "Grundrechte",
    "1.63": "Bürgerrecht",
    "1.64": "Privatrecht",
    "1.65": "Strafrecht",
    "1.66": "Datenschutz",
    "2.11": "Neutralität",
    "2.12": "Unabhängigkeit",
    "2.13": "Gute Dienste",
    "2.21": "EFTA",
    "2.22": "EU",
    "2.23": "EWR",
    "2.24": "Andere europäische Organisationen",
    "2.31": "UNO",
    "2.32": "Andere internationale Organisationen",
    "2.61": "Exportförderung",
    "2.62": "Zollwesen",
    "3.11": "Bevölkerungsschutz",
    "3.12": "Staatsschutz",
    "3.13": "Polizei",
    "3.21": "Armee (allgemein)",
    "3.22": "Militärorganisation",
    "3.23": "Rüstung",
    "3.24": "Militäranlagen",
    "3.25": "Dienstverweigerung, Zivildienst",
    "3.26": "Armeeabschaffung",
    "3.27": "Militärische Ausbildung",
    "3.28": "Internationale Einsätze",
    "4.11": "Konjunkturpolitik",
    "4.12": "Wettbewerbspolitik",
    "4.13": "Strukturpolitik",
    "4.14": "Preispolitik",
    "4.15": "Konsumentenschutz",
    "4.16": "Gesellschaftsrecht",
    "4.21": "Arbeitsbedingungen",
    "4.22": "Arbeitszeit",
    "4.23": "Sozialpartnerschaft",
    "4.24": "Beschäftigungspolitik",
    "4.31": "Geld- und Währungspolitik",
    "4.32": "Banken, Börsen, Versicherungen",
    "4.41": "Fremdenverkehr",
    "4.42": "Hotellerie und Gastgewerbe",
    "4.43": "Geldspiele",
    "6.11": "Steuerpolitik",
    "6.12": "Steuersystem",
    "6.13": "Direkte Steuern",
    "6.14": "Indirekte Steuern",
    "8.11": "Agglomerationsverkehr",
    "8.12": "Transitverkehr",
    "8.21": "Strassenbau",
    "8.22": "Schwerverkehr",
    "8.31": "Güterverkehr",
    "8.32": "Personenverkehr",
    "9.11": "Raumplanung",
    "9.12": "Bodenrecht",
    "9.21": "Mietwesen",
    "9.22": "Wohnungsbau, Wohneigentum",
    "9.31": "Umweltpolitik",
    "9.32": "Lärmschutz",
    "9.33": "Luftreinhaltung",
    "9.34": "Gewässerschutz",
    "9.35": "Bodenschutz",
    "9.36": "Abfälle",
    "9.37": "Natur- und Heimatschutz",
    "9.38": "Tierschutz",
    "10.11": "Gesundheitspolitik",
    "10.12": "Medizinforschung und -technik",
    "10.13": "Medikamente",
    "10.14": "Suchtmittel",
    "10.15": "Fortpflanzungsmedizin",
    "10.21": "Alters- und Hinterbliebenenversicherung",
    "10.22": "Invalidenversicherung",
    "10.23": "Berufliche Vorsorge",
    "10.24": "Kranken- und Unfallversicherung",
    "10.25": "Mutterschaftsversicherung",
    "10.26": "Arbeitslosenversicherung",
    "10.27": "Erwerbsersatzordnung",
    "10.28": "Fürsorge",
    "10.31": "Migrations- und Integrationspolitik",
    "10.32": "Asylpolitik",
    "10.33": "Frauen und Gleichstellungspolitik",
    "10.34": "Familienpolitik",
    "10.35": "Kinder- und Jugendpolitik",
    "10.36": "Alterspolitik",
    "10.37": "Menschen mit Behinderungen",
    "10.38": "LGBTQIA+",
    "11.41": "Gentechnologie",
    "11.42": "Tierversuche",
    "12.51": "Medienpolitik",
    "12.52": "Presse",
    "12.53": "Radio, Fernsehen, Elektronische Medien",
    "12.54": "Medienfreiheit",
}


def resolve_category_code(code: str, level: int) -> str:
    """
    Resolve a single Politikbereich code at the given level (1, 2 or 3) to
    its German label. Unrecognized codes (e.g. "." for "not assigned") are
    returned unchanged.
    """
    table = (LEVEL1, LEVEL2, LEVEL3)[level - 1]
    return table.get(code, code)


def extract_categories(vote: dict) -> list:
    """
    Build the "categories" list for a vote document out of its raw
    d1e1/d1e2/d1e3, d2e1/d2e2/d2e3, d3e1/d3e2/d3e3 fields: up to three
    entries (one per policy area a vote is tagged with), each a
    [level1, level2, level3] array of resolved text, most-general-first --
    only as deep as the vote is actually assigned. A group with no level1
    assigned (missing, "" or ".") is omitted entirely; if level1 is
    assigned but a deeper level isn't, the array simply stops there.
    """
    result = []
    for n in (1, 2, 3):
        entry = []
        for level in (1, 2, 3):
            code = vote.get(f"d{n}e{level}")
            if not code or code == ".":
                break
            entry.append(resolve_category_code(code, level))
        if entry:
            result.append(entry)
    return result
