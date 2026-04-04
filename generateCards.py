#!/usr/bin/env python3
"""Generate cards.tex from Spells.json

Architecture:
  - SchoolConfig: Defines all spell schools (metadata: names, colors, icons)
  - SpellData: Validates & normalizes spell JSON input
  - SpellFormatter: Generates LaTeX output
  - Main logic: Orchestrates the pipeline
"""

import json
import sys


# ==============================================================================
# CONFIGURATION: School Definitions
# ==============================================================================
class SchoolConfig:
    """Central definition of all spell schools with metadata"""
    
    SCHOOLS = {
        "Hervorrufungsmagie": "hervorrufungsmagie",
        "Bannmagie": "bannmagie",
        "Beschwörungsmagie": "beschwoerungsmagie",
        "Erkenntnismagie": "erkenntnismagie",
        "Verzauberungsmagie": "verzauberungsmagie",
        "Illusionsmagie": "illusionsmagie",
        "Verwandlungsmagie": "verwandlungsmagie",
        "Nekromantie": "nekromantie",
    }
    
    @classmethod
    def is_valid_school(cls, school_name: str) -> bool:
        """Check if school is in the known list"""
        return school_name in cls.SCHOOLS
    
    @classmethod
    def get_color_key(cls, school_name: str) -> str:
        """Get lowercase color identifier from school name"""
        if not cls.is_valid_school(school_name):
            raise ValueError(f"Unknown school: {school_name}")
        return cls.SCHOOLS[school_name]
    
    @classmethod
    def all_schools(cls) -> list:
        """Get list of all school names"""
        return list(cls.SCHOOLS.keys())


# ==============================================================================
# DATA: Spell Validation & Normalization
# ==============================================================================
class SpellData:
    """Validates and normalizes spell data from JSON"""
    
    def __init__(self, spell_dict: dict, spell_index: int):
        self.index = spell_index
        self.raw = spell_dict
        self.errors = []
        self.warnings = []
        self._validate()
    
    def _validate(self):
        """Validate spell data and collect errors/warnings"""
        required_fields = ["name", "level", "school", "casting_time", "range", "save", "duration", "components", "description"]
        
        # Check required fields
        for field in required_fields:
            if field not in self.raw:
                self.errors.append(f"Spell #{self.index}: Missing required field '{field}'")
        
        # Validate school
        if "school" in self.raw:
            if not SchoolConfig.is_valid_school(self.raw["school"]):
                self.errors.append(f"Spell #{self.index} '{self.raw.get('name')}': Unknown school '{self.raw['school']}'")
        
        # Check for description length
        if "description" in self.raw:
            desc = self.raw["description"]
            if isinstance(desc, list) and len(desc) > 6:
                self.warnings.append(f"Spell #{self.index} '{self.raw.get('name')}': Description has {len(desc)} lines, may overflow card")
        
        # Check if obsolete "color" field exists
        if "color" in self.raw:
            self.warnings.append(f"Spell #{self.index} '{self.raw.get('name')}': Obsolete 'color' field found (will be auto-generated)")
    
    def is_valid(self) -> bool:
        """True if no errors (warnings are OK)"""
        return len(self.errors) == 0
    
    def report(self):
        """Print errors and warnings"""
        for err in self.errors:
            print(f"ERROR: {err}", file=sys.stderr)
        for warn in self.warnings:
            print(f"WARNING: {warn}")


# ==============================================================================
# FORMAT: LaTeX Generation
# ==============================================================================
class SpellFormatter:
    """Generates LaTeX spell card commands"""
    
    # Separator between components and description in LaTeX parameter
    COMPONENT_DESC_SEPARATOR = "@@@"
    
    @staticmethod
    def format_description(desc_input) -> str:
        r"""
        Format description as bulleted LaTeX text
        
        Input: list of strings or single string
        Output: LaTeX formatted string with bullets
        
        NOTE: We use a single \small scope over the entire list
        rather than \small for each bullet to avoid LaTeX stack overflow
        """
        if isinstance(desc_input, str):
            return desc_input
        
        if not isinstance(desc_input, list):
            return str(desc_input)
        
        # Join list with bullet separators in text mode
        return r" \textbullet ".join(desc_input)
    
    @staticmethod
    def generate_spell_call(spell_data: SpellData) -> str:
        """
        Generate 8-parameter \\spell{} LaTeX command
        
        Parameters:
          1. name
          2. school (color key, e.g., "hervorrufungsmagie")
          3. level
          4. casting_time
          5. range
          6. save
          7. duration
          8. components|description (combined with separator)
        
        The school determines the color; redundant color field is removed.
        """
        s = spell_data.raw
        
        # Format components + description
        components = s.get("components", "").strip()
        description = SpellFormatter.format_description(s.get("description", ""))
        combined = f"{components}{SpellFormatter.COMPONENT_DESC_SEPARATOR}{description}"
        
        # Get color key from school name
        school_name = s["school"]
        color_key = SchoolConfig.get_color_key(school_name)
        
        # Generate 8-parameter call
        spell_call = (
            f"\\spell{{{s['name']}}}"
            f"{{{color_key}}}"
            f"{{{s.get('level', 0)}}}"
            f"{{{s['casting_time']}}}"
            f"{{{s['range']}}}"
            f"{{{s['save']}}}"
            f"{{{s['duration']}}}"
            f"{{{combined}}}"
        )
        return spell_call


# ==============================================================================
# PAGE LAYOUT: LaTeX Tabular Generation
# ==============================================================================
class PageLayout:
    """Generates LaTeX page structure for spell cards"""
    
    CARDS_PER_PAGE = 6
    COLS_PER_ROW = 2
    HSPACE_MM = "2mm"
    VSPACE_MM = "2mm"
    
    @staticmethod
    def get_tabular_preamble() -> str:
        """LaTeX tabular column specification"""
        return "@{}*{" + str(PageLayout.COLS_PER_ROW) + "}{p{\\cardwidth}}@{}"

    @staticmethod
    def make_row(cells: list) -> str:
        """Render a single fixed-width row as a separate tabular* block."""
        return (
            "\\hspace*{\\leftmargin}\\noindent\n"
            "\\begin{tabular*}{\\gridwidth}{" + PageLayout.get_tabular_preamble() + "}\n"
            + " & ".join(cells) + "\n"
            "\\end{tabular*}\n"
        )

    @staticmethod
    def generate_pages(spells_data: list) -> str:
        """Generate complete LaTeX output for all pages"""
        output = ""
        
        for page_num in range(0, len(spells_data), PageLayout.CARDS_PER_PAGE):
            page_spells = spells_data[page_num:page_num + PageLayout.CARDS_PER_PAGE]
            page_number = page_num // PageLayout.CARDS_PER_PAGE + 1
            
            # Front page
            output += f"% Page {page_number} fronts\n"
            output += "\\vspace*{\\topmargin}\n"
            
            for row_start in range(0, len(page_spells), PageLayout.COLS_PER_ROW):
                row_spells = []
                for col in range(PageLayout.COLS_PER_ROW):
                    if row_start + col < len(page_spells):
                        spell_data = page_spells[row_start + col]
                        row_spells.append(SpellFormatter.generate_spell_call(spell_data))
                    else:
                        row_spells.append("")

                output += PageLayout.make_row(row_spells)
                if row_start + PageLayout.COLS_PER_ROW < len(page_spells):
                    output += "\\vgap\n"
            
            output += "\\newpage\n"
            
            # Back page
            output += f"% Page {page_number} backs\n"
            output += "\\vspace*{\\topmargin}\n"
            
            for row_start in range(0, len(page_spells), PageLayout.COLS_PER_ROW):
                row_backs = []
                for col in range(PageLayout.COLS_PER_ROW):
                    if row_start + col < len(page_spells):
                        row_backs.append("\\cardback")
                    else:
                        row_backs.append("")

                output += PageLayout.make_row(row_backs)
                if row_start + PageLayout.COLS_PER_ROW < len(page_spells):
                    output += "\\vgap\n"
            
            if page_num + PageLayout.CARDS_PER_PAGE < len(spells_data):
                output += "\\newpage\n"
        
        return output
# ==============================================================================
# MAIN
# ==============================================================================
def main():
    """Load spells, validate, generate LaTeX output"""
    
    # Load JSON
    try:
        with open("Spells.json", "r", encoding="utf-8") as f:
            spells_raw = json.load(f)
    except FileNotFoundError:
        print("ERROR: Spells.json not found", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in Spells.json: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Validate & normalize
    spells_data = []
    error_count = 0
    for idx, spell_dict in enumerate(spells_raw):
        spell = SpellData(spell_dict, idx)
        spell.report()
        if spell.is_valid():
            spells_data.append(spell)
        else:
            error_count += 1
    
    if error_count > 0:
        print(f"\nERROR: {error_count} spell(s) failed validation, aborting", file=sys.stderr)
        sys.exit(1)
    
    # Generate LaTeX
    latex_output = PageLayout.generate_pages(spells_data)
    
    # Write output
    try:
        with open("cards.tex", "w", encoding="utf-8") as f:
            f.write(latex_output)
    except IOError as e:
        print(f"ERROR: Could not write cards.tex: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Report success
    num_pages = (len(spells_data) + PageLayout.CARDS_PER_PAGE - 1) // PageLayout.CARDS_PER_PAGE
    print(f"✓ Generated: {len(spells_data)} spells on {num_pages} pages → cards.tex")


if __name__ == "__main__":
    main()
