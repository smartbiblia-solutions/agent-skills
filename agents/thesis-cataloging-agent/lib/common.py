from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
KNOWLEDGE_DIR = ROOT / "knowledge"
MEMORY_DIR = ROOT / "memory"
DATASET_DIR = ROOT / "dataset"
SCHEMA_DIR = ROOT / "schemas"

DEGREE_TYPES = {
    "Thèse d'État",
    "Thèse de doctorat",
    "Thèse de 3e cycle",
    "Thèse d'université",
    "Thèse de docteur-ingénieur",
    "Thèse d'exercice",
    "Habilitation à diriger des recherches",
    "Mémoire de DEA",
    "Mémoire de DES",
    "Mémoire de DESS",
    "Mémoire de DU",
    "Mémoire de DIU",
    "Mémoire de DUT",
    "Mémoire de maîtrise",
    "Mémoire de master professionnel 1re année",
    "Mémoire de master professionnel 2e année",
    "Mémoire de master recherche 1re année",
    "Mémoire de master recherche 2e année",
}

DISCIPLINE_MAP = {
    "000": "Informatique, information, généralités",
    "004": "Informatique",
    "020": "Bibliothéconomie et sciences de l'information",
    "060": "Organisations générales et muséologie",
    "070": "Médias d'information, journalisme, édition",
    "090": "Manuscrits et livres rares",
    "100": "Philosophie, psychologie",
    "150": "Psychologie",
    "300": "Sciences sociales, sociologie, anthropologie",
    "320": "Science politique",
    "330": "Economie",
    "340": "Droit",
    "370": "Education et enseignement",
    "400": "Langues et linguistique",
    "440": "Langues romanes. Français",
    "500": "Sciences de la nature et mathématiques",
    "510": "Mathématiques",
    "530": "Physique",
    "540": "Chimie, minéralogie, cristallographie",
    "550": "Sciences de la terre",
    "570": "Sciences de la vie, biologie, biochimie",
    "600": "Technologie (Sciences appliquées)",
    "610": "Médecine et santé",
    "620": "Sciences de l'ingénieur",
    "630": "Agronomie, agriculture et médecine vétérinaire",
    "650": "Gestion et organisation de l'entreprise",
    "700": "Arts",
    "780": "Musique",
    "800": "Littérature, rhétorique et critique",
    "900": "Histoire, géographie",
}

LANGUAGE_MAP = {
    "français": "fre",
    "francais": "fre",
    "french": "fre",
    "anglais": "eng",
    "english": "eng",
    "allemand": "ger",
    "german": "ger",
    "espagnol": "spa",
    "spanish": "spa",
    "italien": "ita",
    "latin": "lat",
}

NAME_SPLIT_RE = re.compile(r"\s*[;,]\s*|\s+et\s+", re.IGNORECASE)
YEAR_RE = re.compile(r"\b(19|20)\d{2}\b")


@dataclass
class ValidationIssue:
    path: str
    message: str
    level: str = "error"


def read_text(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8")


def write_json_stdout(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def load_json(path: str | Path) -> Any:
    return json.loads(read_text(path))


def save_json(path: str | Path, payload: Any) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def list_knowledge_files() -> list[str]:
    if not KNOWLEDGE_DIR.exists():
        return []
    return sorted(str(p.relative_to(ROOT)) for p in KNOWLEDGE_DIR.rglob("*.md"))


def load_knowledge_summary() -> dict[str, Any]:
    files = []
    for path in KNOWLEDGE_DIR.rglob("*.md"):
        files.append({
            "path": str(path.relative_to(ROOT)),
            "title": path.stem,
            "size": len(path.read_text(encoding="utf-8")),
        })
    return {"count": len(files), "files": sorted(files, key=lambda x: x["path"])}


def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def split_names(raw: str) -> list[str]:
    raw = normalize_whitespace(raw)
    if not raw:
        return []
    parts = [normalize_whitespace(p) for p in NAME_SPLIT_RE.split(raw) if normalize_whitespace(p)]
    return parts


def infer_document_type(text: str) -> str:
    lower = text.lower()
    if "mémoire" in lower or "memoire" in lower or "habilitation" in lower:
        return "dissertation"
    return "thesis"


def infer_degree_type(text: str) -> str:
    lower = text.lower()
    if "habilitation à diriger des recherches" in lower:
        return "Habilitation à diriger des recherches"
    if "thèse de doctorat" in lower or "these de doctorat" in lower or "doctorat" in lower:
        return "Thèse de doctorat"
    if "thèse d'exercice" in lower or "these d'exercice" in lower:
        return "Thèse d'exercice"
    if "mémoire de master" in lower or "memoire de master" in lower:
        return "Mémoire de master recherche 2e année"
    return "Thèse de doctorat"


def infer_language(text: str) -> str:
    lower = text.lower()
    for key, code in LANGUAGE_MAP.items():
        if key in lower:
            return code
    return "fre"


def infer_discipline(text: str) -> str:
    lower = text.lower()
    heuristics = [
        ("informatique", "004"),
        ("computer", "004"),
        ("bibliothé", "020"),
        ("bibliothe", "020"),
        ("droit", "340"),
        ("économie", "330"),
        ("economie", "330"),
        ("politique", "320"),
        ("lingu", "400"),
        ("math", "510"),
        ("physique", "530"),
        ("chim", "540"),
        ("géologie", "550"),
        ("geologie", "550"),
        ("biolog", "570"),
        ("médec", "610"),
        ("medec", "610"),
        ("ingénieur", "620"),
        ("ingenieur", "620"),
        ("agronom", "630"),
        ("gestion", "650"),
        ("histoire", "900"),
        ("géographie", "900"),
        ("geographie", "900"),
    ]
    for needle, code in heuristics:
        if needle in lower:
            return f"{code} {DISCIPLINE_MAP[code]}"
    return "004 Informatique"


def find_year(text: str) -> str:
    match = YEAR_RE.search(text)
    return match.group(0) if match else ""


def parse_cover_text(text: str) -> dict[str, Any]:
    lines = [normalize_whitespace(line) for line in text.splitlines() if normalize_whitespace(line)]
    title = ""
    subtitle = ""
    author = ""
    advisor: list[str] = []
    jury_president: list[str] = []
    reviewers: list[str] = []
    committee_members: list[str] = []
    granting_institution = ""
    doctoral_school: list[str] = []
    partner_institutions: list[str] = []
    co_tutelle_institutions: list[str] = []
    abstract = ""

    title_candidate_pending = False
    for idx, line in enumerate(lines):
        lower = line.lower()
        if "thèse de doctorat" in lower or "these de doctorat" in lower or lower.startswith("thèse") or lower.startswith("these"):
            title_candidate_pending = True
            continue
        if title_candidate_pending and not title and len(line) > 12 and not any(k in lower for k in ["université", "universite", "école doctorale", "ecole doctorale", "par ", "présentée", "presentee"]):
            title = line
            if idx + 1 < len(lines):
                next_lower = lines[idx + 1].lower()
                if len(lines[idx + 1]) > 10 and not any(k in next_lower for k in ["par ", "président", "president", "rapporteur", "membres du jury", "jury", "année", "annee", "langue", "résumé", "resume"]):
                    subtitle = lines[idx + 1]
            title_candidate_pending = False
        if lower.startswith("par "):
            author = normalize_whitespace(line[4:])
        elif "auteur" in lower and ":" in line and not author:
            author = normalize_whitespace(line.split(":", 1)[1])
        if ("directeur" in lower or "directrice" in lower or "sous la direction" in lower) and ":" in line:
            advisor.extend(split_names(line.split(":", 1)[1]))
        if "président du jury" in lower and ":" in line:
            jury_president.extend(split_names(line.split(":", 1)[1]))
        if ("rapporteur" in lower or "reviewer" in lower) and ":" in line:
            reviewers.extend(split_names(line.split(":", 1)[1]))
        if ("membres du jury" in lower or "jury" in lower) and ":" in line:
            committee_members.extend(split_names(line.split(":", 1)[1]))
        if ("université" in lower or "universite" in lower) and not granting_institution:
            granting_institution = line
        if "école doctorale" in lower or "ecole doctorale" in lower:
            doctoral_school.append(line.split(":", 1)[1].strip() if ":" in line else line)
        if "co-tutelle" in lower or "cotutelle" in lower:
            co_tutelle_institutions.extend(split_names(line.split(":", 1)[1] if ":" in line else line))
        if "partenaire" in lower and ":" in line:
            partner_institutions.extend(split_names(line.split(":", 1)[1]))
        if lower.startswith("résumé") or lower.startswith("resume"):
            abstract = line.split(":", 1)[1].strip() if ":" in line else ""

    if not title and lines:
        title = lines[0]
    return {
        "document-type": infer_document_type(text),
        "title": title,
        "subtitle": subtitle,
        "author": author,
        "advisor": unique_list(advisor),
        "jury_president": unique_list(jury_president),
        "reviewers": unique_list(reviewers),
        "committee_members": unique_list(committee_members),
        "defense_year": find_year(text),
        "language": infer_language(text),
        "abstract_language": [infer_language(text)],
        "degree_type": infer_degree_type(text),
        "discipline": infer_discipline(text),
        "granting_institution": granting_institution,
        "co_tutelle_institutions": unique_list(co_tutelle_institutions),
        "doctoral_school": unique_list(doctoral_school),
        "partner_institutions": unique_list(partner_institutions),
        "abstract": abstract,
    }


def unique_list(values: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for value in values:
        value = normalize_whitespace(value)
        if value and value not in seen:
            seen.add(value)
            out.append(value)
    return out


def validate_metadata(payload: dict[str, Any]) -> tuple[list[ValidationIssue], list[str]]:
    issues: list[ValidationIssue] = []
    warnings: list[str] = []
    required = [
        "document-type", "title", "subtitle", "author", "advisor", "jury_president",
        "reviewers", "committee_members", "defense_year", "language", "abstract_language",
        "degree_type", "discipline", "granting_institution", "co_tutelle_institutions",
        "doctoral_school", "partner_institutions", "abstract"
    ]
    for key in required:
        if key not in payload:
            issues.append(ValidationIssue(key, "champ obligatoire manquant"))
    if payload.get("document-type") not in {"thesis", "dissertation"}:
        issues.append(ValidationIssue("document-type", "doit être 'thesis' ou 'dissertation'"))
    if payload.get("degree_type") and payload.get("degree_type") not in DEGREE_TYPES:
        warnings.append("degree_type hors liste fermée attendue")
    if payload.get("discipline"):
        if not any(payload["discipline"].startswith(code + " ") or payload["discipline"] == code for code in DISCIPLINE_MAP):
            warnings.append("discipline hors vocabulaire contrôlé connu")
    if payload.get("language") and len(str(payload["language"])) != 3:
        warnings.append("language devrait idéalement être un code sur 3 lettres")
    if not payload.get("title"):
        issues.append(ValidationIssue("title", "titre vide"))
    if not payload.get("author"):
        issues.append(ValidationIssue("author", "auteur vide"))
    year = str(payload.get("defense_year", ""))
    if year and not YEAR_RE.fullmatch(year):
        warnings.append("defense_year ne ressemble pas à une année à 4 chiffres")
    return issues, warnings


def person_to_access_point(name: str) -> str:
    name = normalize_whitespace(name)
    parts = name.split()
    if len(parts) >= 2:
        return f"{parts[-1]}, {' '.join(parts[:-1])}"
    return name


def build_unimarc_xml(metadata: dict[str, Any], persons: list[dict[str, Any]] | None = None) -> str:
    record = ET.Element("record")
    leader = ET.SubElement(record, "leader")
    leader.text = "00000nam a2200000 u 4500"

    def add_df(tag: str, ind1: str = " ", ind2: str = " ", subfields: list[tuple[str, str]] | None = None):
        field = ET.SubElement(record, "datafield", tag=tag, ind1=ind1, ind2=ind2)
        for code, value in (subfields or []):
            sf = ET.SubElement(field, "subfield", code=code)
            sf.text = value
        return field

    add_df("101", subfields=[("a", metadata.get("language", "fre"))])
    title_subfields = [("a", metadata.get("title", ""))]
    if metadata.get("subtitle"):
        title_subfields.append(("e", metadata["subtitle"]))
    add_df("200", ind1="1", subfields=title_subfields)
    if metadata.get("degree_type"):
        add_df("328", subfields=[("a", metadata["degree_type"])])
    if metadata.get("abstract"):
        add_df("330", subfields=[("a", metadata["abstract"])])
    if metadata.get("granting_institution"):
        add_df("712", subfields=[("a", metadata["granting_institution"])])
    if metadata.get("defense_year"):
        add_df("210", subfields=[("d", metadata["defense_year"])])
    if metadata.get("discipline"):
        add_df("686", subfields=[("a", metadata["discipline"])])

    role_to_tag = {
        "author": "700",
        "advisor": "701",
        "jury_president": "702",
        "reviewer": "702",
        "committee_member": "702",
    }
    if persons:
        for person in persons:
            tag = role_to_tag.get(person.get("role", "committee_member"), "702")
            subfields = [("a", person.get("normalized_form") or person_to_access_point(person.get("name", "")))]
            if person.get("ppn"):
                subfields.append(("3", person["ppn"]))
            add_df(tag, subfields=subfields)
    else:
        if metadata.get("author"):
            add_df("700", subfields=[("a", person_to_access_point(metadata["author"]))])
        for advisor in metadata.get("advisor", []):
            add_df("701", subfields=[("a", person_to_access_point(advisor))])
        for name in metadata.get("jury_president", []):
            add_df("702", subfields=[("a", person_to_access_point(name))])
        for name in metadata.get("reviewers", []):
            add_df("702", subfields=[("a", person_to_access_point(name))])
        for name in metadata.get("committee_members", []):
            add_df("702", subfields=[("a", person_to_access_point(name))])

    return ET.tostring(record, encoding="unicode")


def validate_unimarc_xml(xml_text: str) -> tuple[list[str], list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    checked_fields: list[str] = []
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as exc:
        return [f"XML invalide: {exc}"], [], []
    tags = [el.attrib.get("tag", "") for el in root.findall("datafield")]
    checked_fields = sorted(set(t for t in tags if t))
    for mandatory in ["101", "200", "700"]:
        if mandatory not in tags:
            errors.append(f"zone {mandatory} manquante")
    if "328" not in tags:
        warnings.append("zone 328 absente")
    for field in root.findall("datafield"):
        tag = field.attrib.get("tag", "")
        if tag in {"700", "701", "702"}:
            subcodes = [sf.attrib.get("code") for sf in field.findall("subfield")]
            if "a" not in subcodes:
                errors.append(f"zone {tag} sans sous-champ $a")
    return errors, warnings, checked_fields
