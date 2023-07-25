#!/usr/bin/env python3

import io
import os
import json
import subprocess
from copy import copy

def fill_template_var(template: str, template_var: str, content_var: str) -> str:
    return template.replace("{[ " + template_var + " ]}", content_var)

def fill_out_summary(template, summary, lang):
    template = fill_template_var(template, "summary_heading", summary["heading"][lang])
    template = fill_template_var(template, "summary_body", summary["body"][lang])
    return template

def format_string_list_as_table_row(string_list: list[str]) -> str:
    return "| " + " | ".join(str(h) for h in string_list) + " |"

def fill_out_table(template, data, lang,
                   template_heading_name, content_heading_name,
                   template_headers_name, content_headers_name,
                   template_records_name, content_records_name):
    template = fill_template_var(template, template_heading_name, data[content_heading_name][lang])
    table_headers_as_string = format_string_list_as_table_row(data[content_headers_name][lang])
    template = fill_template_var(template, template_headers_name, table_headers_as_string)
    
    table_records = []
    for record in data[content_records_name][lang]:
        record = format_string_list_as_table_row(record)
        table_records.append(record)
    table_records_as_string = "\n".join(str(record) for record in table_records)
    template = fill_template_var(template, template_records_name, table_records_as_string)
    return template

def fill_out_contact(template, contact, lang):
    template = fill_template_var(template, "contact_heading", contact["heading"][lang])
    
    template = fill_template_var(template, "name_word",     contact["elements"]["name_word"][lang])
    template = fill_template_var(template, "email_word",    contact["elements"]["email_word"][lang])
    template = fill_template_var(template, "location_word", contact["elements"]["location_word"][lang])
    template = fill_template_var(template, "phone_word",    contact["elements"]["phone_word"][lang])
    
    template = fill_template_var(template, "name",     contact["elements"]["name"])
    template = fill_template_var(template, "email",    contact["elements"]["email"])
    template = fill_template_var(template, "location", contact["elements"]["location"][lang])
    template = fill_template_var(template, "phone",    contact["elements"]["phone"])
    return template;

def fill_out_experience(template, experience, lang):
    template = fill_out_table(template, experience, lang,
                              "experience_heading", "heading",
                              "experience_table_headers", "table_headers",
                              "experience_table_records", "table_records")
    return template

def fill_out_education(template, education, lang):
    template = fill_out_table(template, education, lang,
                              "education_heading", "heading",
                              "education_table_headers", "table_headers",
                              "education_table_records", "table_records")
    return template
    
def fill_out_awards(template, awards, lang):
    template = fill_out_table(template, awards, lang,
                              "awards_heading", "heading",
                              "awards_table_headers", "table_headers",
                              "awards_table_records", "table_records")
    return template

def fill_out_organizations(template, organizations, lang):
    template = fill_out_table(template, organizations, lang,
                              "organizations_heading", "heading",
                              "organizations_table_headers", "table_headers",
                              "organizations_table_records", "table_records")
    return template

def fill_out_skills(template, skills, lang):
    template = fill_template_var(template, "hard_skills_heading", skills["hard"]["heading"])
    template = fill_template_var(template, "soft_skills_heading", skills["soft"]["heading"])
    
    hard = skills["hard"]["skills"][lang]
    soft = skills["soft"]["skills"][lang]

    hard_skills_as_strings = []
    for skill in hard:
        hard_skills_as_strings.append("{{{task(" + skill + ")}}}")
    hard_skills = "\n".join(hard_skills_as_strings)
    
    soft_skills_as_strings = []
    for skill in soft:
        soft_skills_as_strings.append("{{{task(" + skill + ")}}}")
    soft_skills = "\n".join(soft_skills_as_strings)

    template = fill_template_var(template, "hard_skills", hard_skills)
    template = fill_template_var(template, "soft_skills", soft_skills)

    return template

if __name__ == "__main__":

    with io.open("curriculum_vitae.org", mode="r", encoding="utf-8") as template_file:
        template = template_file.read()

    with io.open("content.json", mode="r", encoding="utf-8") as content_file:
        content = json.load(content_file)
        cv_langs      = content["cv_langs"]
        summary       = content["summary"]
        experience    = content["experience"]
        education     = content["education"]
        awards        = content["awards"]
        organizations = content["organizations"]
        skills        = content["skills"]
        
    with io.open(".secret_content.json", mode="r", encoding="utf-8") as secret_content:
        secret_content = json.load(secret_content)
        contact = secret_content["contact"]

    cwd = str(os.getcwd())
        
    setup_file_path = cwd + "/setup.org"
    template = fill_template_var(template, "setup_file", setup_file_path)

    my_latex_package = cwd + "/mycv"
    template = fill_template_var(template, "my_latex_package", my_latex_package)
    
    for lang in cv_langs:
        template_copy = template[:]
        template_copy = fill_out_summary(template_copy, summary, lang)
        template_copy = fill_out_contact(template_copy, contact, lang)
        template_copy = fill_out_experience(template_copy, experience, lang)
        template_copy = fill_out_education(template_copy, education, lang)
        template_copy = fill_out_awards(template_copy, awards, lang)
        template_copy = fill_out_organizations(template_copy, organizations, lang)
        template_copy = fill_out_skills(template_copy, skills, lang)

        filename_without_extension = f"ruben_sorensen_curriculum_vitae_{lang}"
        org_filename = f"{filename_without_extension}.org"
        
        build_dir = f"{cwd}/build"
        if not os.path.exists(build_dir):
            os.makedirs(build_dir)
            
        with io.open(build_dir + "/" + org_filename, mode="w", encoding="utf-8") as f:
            f.write(template_copy)
                        
        subprocess.run(["emacs", "-batch", f"{build_dir}/{org_filename}", "--load", f"{cwd}/config.el", "-f", "org-latex-export-to-pdf"])
        subprocess.run(["emacs", "-batch", f"{build_dir}/{org_filename}", "--load", f"{cwd}/config.el", "-f", "org-html-export-to-html"])
