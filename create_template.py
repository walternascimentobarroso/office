#!/usr/bin/env python3
"""Script to create the Excel template"""

import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
SRC_TEMPLATE = BASE_DIR / 'templates' / 'excel_template.xlsx'
DEST_TEMPLATE = BASE_DIR / 'templates' / 'excel_template2.xlsx'


def create_template_from_existing():
    """Copy the provided template file so output is exactly the same."""
    if not SRC_TEMPLATE.exists():
        raise FileNotFoundError(f"Template base não encontrado: {SRC_TEMPLATE}")

    try:
        from openpyxl import load_workbook
    except ModuleNotFoundError:
        shutil.copyfile(SRC_TEMPLATE, DEST_TEMPLATE)
        print(f"openpyxl não encontrado; template copiado de {SRC_TEMPLATE} para {DEST_TEMPLATE}")
        return

    wb = load_workbook(SRC_TEMPLATE)
    wb.save(DEST_TEMPLATE)
    print(f"Template criado com base em {SRC_TEMPLATE} para {DEST_TEMPLATE}")


if __name__ == '__main__':
    create_template_from_existing()
