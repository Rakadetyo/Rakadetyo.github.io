#!/usr/bin/env python3
"""
build.py - Static site generator for Rakadetyo's portfolio.

Reads JSON data from data/ and HTML templates from templates/,
then assembles the final index.html.

Usage:
    python build.py

To update your CV, edit the JSON files in data/ and re-run this script.
"""

import json
import os
import sys

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT, "data")
TMPL_DIR = os.path.join(ROOT, "templates")
SECT_DIR = os.path.join(TMPL_DIR, "sections")
OUTPUT = os.path.join(ROOT, "index.html")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def load_json(filename):
    """Load a JSON file from the data directory."""
    path = os.path.join(DATA_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_template(path):
    """Load an HTML template file."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def indent(text, spaces=8):
    """Indent every line of text by the given number of spaces."""
    pad = " " * spaces
    lines = text.split("\n")
    return "\n".join(pad + line if line.strip() else line for line in lines)


# ---------------------------------------------------------------------------
# Section builders — each returns an HTML string
# ---------------------------------------------------------------------------
def build_about():
    data = load_json("about.json")
    tmpl = load_template(os.path.join(SECT_DIR, "about.html"))

    links_html = "\n".join(
        f'        <li><a href="{l["url"]}" target="_blank">{l["label"]}</a></li>'
        for l in data["links"]
    )

    return (
        tmpl.replace("{{name}}", data["name"])
        .replace("{{title}}", data["title"])
        .replace("{{phone_url}}", data["phone"]["url"])
        .replace("{{phone_label}}", data["phone"]["label"])
        .replace("{{email_url}}", data["email"]["url"])
        .replace("{{email_label}}", data["email"]["label"])
        .replace("{{bio}}", data["bio"])
        .replace("{{links}}", links_html)
    )


def build_experience():
    data = load_json("experience.json")
    tmpl = load_template(os.path.join(SECT_DIR, "experience.html"))

    entries = []
    for exp in data:
        points_html = "\n".join(f"            <li>{p}</li>" for p in exp["points"])
        entry = f"""      <div class="entry">
        <div class="entry__body">
          <h3 class="entry__title">{exp["title"]}</h3>
          <h4 class="entry__org">{exp["org"]}</h4>
        </div>
        <div class="entry__date">{exp["date"]}</div>
        <div class="entry__content">
          <ul>
{points_html}
          </ul>
        </div>
      </div>"""
        entries.append(entry)

    return tmpl.replace("{{entries}}", "\n\n".join(entries))


def build_projects():
    data = load_json("projects.json")
    tmpl = load_template(os.path.join(SECT_DIR, "projects.html"))

    entries = []
    for proj in data:
        desc_html = "\n".join(f"          <p>{p}</p>" for p in proj["description"])

        links_html = ""
        if proj.get("links"):
            link_items = "\n".join(
                f'          <li><a href="{l["url"]}" target="_blank">{l["label"]}</a></li>'
                for l in proj["links"]
            )
            links_html = f"""
        <ul class="project__links">
{link_items}
        </ul>"""

        entry = f"""      <div class="project">
        <h3 class="project__title">{proj["title"]}</h3>
        <h4 class="project__subtitle">{proj["subtitle"]}</h4>
        <div class="project__content">
{desc_html}
        </div>{links_html}
      </div>"""
        entries.append(entry)

    return tmpl.replace("{{entries}}", "\n\n".join(entries))


def build_education():
    data = load_json("education.json")
    tmpl = load_template(os.path.join(SECT_DIR, "education.html"))

    entries = []
    for edu in data:
        # Subtitle line
        subtitle = ""
        if edu.get("subtitle"):
            subtitle = f'\n          <h4 class="entry__org">{edu["subtitle"]}</h4>'

        # Content block (details + transcripts)
        content_parts = []
        for d in edu.get("details", []):
            content_parts.append(f"          <p>{d}</p>")
        for t in edu.get("transcripts", []):
            content_parts.append(
                f"          <p>\n"
                f'            {t["label"]}: <a href="{t["url"]}" target="_blank"><strong>{t["text"]}</strong></a>\n'
                f"          </p>"
            )

        content_html = ""
        if content_parts:
            content_html = f"""
        <div class="entry__content">
{chr(10).join(content_parts)}
        </div>"""

        entry = f"""      <div class="entry">
        <div class="entry__body">
          <h3 class="entry__title">{edu["title"]}</h3>{subtitle}
        </div>
        <div class="entry__date">{edu["date"]}</div>{content_html}
      </div>"""
        entries.append(entry)

    return tmpl.replace("{{entries}}", "\n\n".join(entries))


def build_skills():
    data = load_json("skills.json")
    tmpl = load_template(os.path.join(SECT_DIR, "skills.html"))

    groups = []
    for group in data["groups"]:
        if group["type"] == "tags":
            items_html = "\n".join(
                f"          <li>{item}</li>" for item in group["items"]
            )
            html = f"""      <div class="skills-group">
        <h3>{group["name"]}</h3>
        <ul class="skills-list skills-list--tags">
{items_html}
        </ul>
      </div>"""
        else:  # check
            items_html = "\n".join(
                f"          <li>{item}</li>" for item in group["items"]
            )
            html = f"""      <div class="skills-group">
        <h3>{group["name"]}</h3>
        <ul class="skills-check">
{items_html}
        </ul>
      </div>"""
        groups.append(html)

    return tmpl.replace("{{groups}}", "\n\n".join(groups))


def build_awards():
    data = load_json("awards.json")
    tmpl = load_template(os.path.join(SECT_DIR, "awards.html"))

    items = []
    for award in data:
        if award.get("link"):
            items.append(
                f'        <li>{award["text"]} <a href="{award["link"]["url"]}" target="_blank">'
                f"<strong>{award['link']['label']}</strong></a></li>"
            )
        else:
            items.append(f"        <li>{award['text']}</li>")

    return tmpl.replace("{{items}}", "\n".join(items))


def build_organization():
    data = load_json("organization.json")
    tmpl = load_template(os.path.join(SECT_DIR, "organization.html"))

    groups = []
    for org in data:
        entries_html = "\n".join(
            f"""        <div class="org-entry">
          <span class="org-entry__role">{e["role"]}</span>
          <span class="org-entry__date">{e["date"]}</span>
        </div>"""
            for e in org["entries"]
        )
        html = f"""      <div class="org-group">
        <h3>{org["name"]}</h3>
{entries_html}
      </div>"""
        groups.append(html)

    return tmpl.replace("{{groups}}", "\n\n".join(groups))


def build_other():
    data = load_json("other.json")
    tmpl = load_template(os.path.join(SECT_DIR, "other.html"))

    paragraphs = "\n".join(f"      <p>{p}</p>" for p in data["paragraphs"])
    bio_items = "\n".join(
        f"        <li><strong>{b['label']}</strong> {b['value']}</li>"
        for b in data["bio"]
    )

    return tmpl.replace("{{paragraphs}}", paragraphs).replace(
        "{{bio_items}}", bio_items
    )


# ---------------------------------------------------------------------------
# Main assembly
# ---------------------------------------------------------------------------
def build():
    about = load_json("about.json")
    nav = load_json("nav.json")
    base = load_template(os.path.join(TMPL_DIR, "base.html"))

    # Build nav links
    nav_links = "\n".join(
        f'        <li><a href="#{s["id"]}">{s["label"]}</a></li>'
        for s in nav["sections"]
    )

    # Build theme options
    theme_options = "\n".join(
        f'          <li><button data-theme-value="{key}" onclick="setTheme(\'{key}\')">{label}</button></li>'
        for key, label in nav["themes"].items()
    )

    # Build themes JSON for JS
    themes_json = json.dumps(nav["themes"])

    # Section order follows nav.json
    section_builders = {
        "about": build_about,
        "experience": build_experience,
        "projects": build_projects,
        "awards": build_awards,
        "skills": build_skills,
        "education": build_education,
        "organization": build_organization,
        "other": build_other,
    }

    sections = []
    for s in nav["sections"]:
        builder = section_builders.get(s["id"])
        if builder:
            sections.append(builder())

    sections_html = "\n\n".join(sections)

    # Assemble final HTML
    html = (
        base.replace("{{name}}", about["name"])
        .replace("{{meta_description}}", f"{about['name']} - {about['title']}")
        .replace("{{nav_links}}", nav_links)
        .replace("{{theme_options}}", theme_options)
        .replace("{{themes_json}}", themes_json)
        .replace("{{sections}}", sections_html)
    )

    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Built {OUTPUT}")
    print(f"  Sections: {len(sections)}")
    print(f"  Themes:   {len(nav['themes'])}")


if __name__ == "__main__":
    build()
