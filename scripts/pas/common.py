"""Funções compartilhadas pelos extratores do PAS/UnB.

Leitura dos PDFs com cache, normalização do texto extraído pelo pypdf,
detecção de cabeçalhos de campus/curso e anonimização da inscrição.
"""
import hashlib
import json
import os
import re
import unicodedata

import pypdf

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
RAW = os.path.join(ROOT, 'raw_data')
PARSED = os.path.join(ROOT, 'parsed_data')
INTERMEDIARIOS = os.path.join(PARSED, 'intermediarios')
CACHE = os.path.join(ROOT, '.cache', 'pdf_text')

SUBPROGRAMAS = ['14-16', '15-17', '16-18', '17-19', '18-20',
                '19-21', '20-22', '21-23', '22-24', '23-25']

# Sal fixo da anonimização: o mesmo aluno recebe sempre o mesmo id, mas o id
# não permite recuperar a inscrição sem conhecer o sal.
SALT = 'artigo-tac-pas-unb'

DASHES = '‐‑‒–—−'


def anon_id(subprograma, inscricao):
    raw = f'{SALT}|{subprograma}|{inscricao}'.encode()
    return hashlib.sha256(raw).hexdigest()[:16]


def pdf_pages(path):
    """Texto de cada página do PDF, com cache em .cache/pdf_text."""
    os.makedirs(CACHE, exist_ok=True)
    rel = os.path.relpath(path, ROOT)
    st = os.stat(path)
    key = hashlib.md5(f'{rel}|{st.st_size}|{int(st.st_mtime)}'.encode()).hexdigest()
    cache_file = os.path.join(CACHE, key + '.json')
    if os.path.exists(cache_file):
        with open(cache_file, encoding='utf-8') as f:
            return json.load(f)
    reader = pypdf.PdfReader(path)
    pages = [page.extract_text() or '' for page in reader.pages]
    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump(pages, f)
    return pages


def flat(text):
    """Texto em uma linha só, com espaços simples e hífens normalizados."""
    for d in DASHES:
        text = text.replace(d, '-')
    return ' '.join(text.split())


def strip_accents(text):
    return ''.join(c for c in unicodedata.normalize('NFD', text)
                   if unicodedata.category(c) != 'Mn')


def norm_key(text):
    """Chave de comparação: sem acentos, maiúsculas, espaços simples."""
    text = strip_accents(flat(text)).upper()
    text = re.sub(r'\s*-\s*', ' - ', text)
    text = re.sub(r'\s*/\s*', '/', text)
    text = re.sub(r'\(\s*', '(', text)
    text = re.sub(r'\s*\)', ')', text)
    return ' '.join(text.split()).strip(' *')


def to_float(token):
    token = re.sub(r'\s', '', token)
    if token in ('', '-'):
        return None
    return float(token)


def to_int(token):
    token = re.sub(r'\s', '', token)
    if token in ('', '-'):
        return None
    return int(token)


INSCRICAO_RE = re.compile(r'(?<![\d.])(\d{4}\s?\d{4})(?=\s*,)')


def count_inscricoes(text):
    return len(INSCRICAO_RE.findall(text))
