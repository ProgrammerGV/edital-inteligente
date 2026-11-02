"""Normalização adaptada de ProgrammerGV/INF032-Programa-o_Python.

Origem: projeto/rastreador-editais/src/utils.py, commit 84768f4.
"""
import unicodedata


def normalize(text: str) -> str:
    return ''.join(c for c in unicodedata.normalize('NFKD', text.lower())
                   if not unicodedata.combining(c))
