from dataclasses import dataclass

# ------------------------------------------------------------------------
#   Data Models
# ------------------------------------------------------------------------

@dataclass
class ValidationReport:
    object_name: str
    material_name: str
    issue_type: str
    message: str
    severity: str = 'WARNING'  # 'ERROR' or 'WARNING'
