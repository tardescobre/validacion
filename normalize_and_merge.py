import csv
import io
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import chardet  # type: ignore
import pandas as pd


BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "limpios"
OUTPUT_DIR.mkdir(exist_ok=True)

# Canonical columns for unified export
CANONICAL_COLS: List[str] = [
    "nombre_profesional",
    "utilidad",
    "eficiencia",
    "intencion_uso",
    "satisfaccion_claridad",
    "satisfaccion_diseño",
    "modificar_secciones",
    "comentarios",
    "fecha_envio",
    "cedula_profesional",
    "profesion_profesional",
]

# Known alternative header spellings mapping -> canonical
HEADER_ALIASES: Dict[str, str] = {
    # diseño variations
    "satisfaccion_diseno": "satisfaccion_diseño",
    # sometimes accents removed or case variants
    "profesion": "profesion_profesional",
    "cedula": "cedula_profesional",
}


def detect_encoding(file_path: Path, sample_bytes: int = 65536) -> str:
    with open(file_path, "rb") as f:
        raw = f.read(sample_bytes)
    result = chardet.detect(raw)
    enc = result.get("encoding") or "utf-8"
    # Prefer utf-8-sig to preserve BOM handling if detector says UTF-8
    if enc.lower().startswith("utf-8"):
        return "utf-8-sig"
    return enc


def sniff_dialect(file_path: Path, encoding: str) -> Tuple[str, str]:
    # Return (delimiter, quotechar)
    with open(file_path, "rb") as fb:
        raw = fb.read(65536)
    try:
        text = raw.decode(encoding, errors="replace")
    except LookupError:
        text = raw.decode("utf-8", errors="replace")
    sniffer = csv.Sniffer()
    # Ensure header presence is not mandatory for sniff
    try:
        dialect = sniffer.sniff(text)
        delim = getattr(dialect, "delimiter", ",") or ","
        quote = getattr(dialect, "quotechar", '"') or '"'
        return delim, quote
    except Exception:
        return ",", '"'


def normalize_headers(cols: List[str]) -> List[str]:
    normed: List[str] = []
    for c in cols:
        cc = (c or "").strip()
        # Normalize whitespace and case
        cc = cc.replace("\ufeff", "")  # remove BOM if inside header
        # Replace common invisible replacement char
        cc = cc.replace("\ufffd", "")
        # Lowercase for mapping but preserve diacritics
        low = cc.lower()
        # Map aliases
        if low in HEADER_ALIASES:
            cc = HEADER_ALIASES[low]
        elif low.endswith("_opcion"):
            # Drop *_opcion columns later by returning same name; we'll filter
            cc = low
        else:
            cc = low
        # Fix common typo: diseno -> diseño
        if "diseno" in cc and "diseño" not in cc:
            cc = cc.replace("diseno", "diseño")
        normed.append(cc)
    return normed


def read_csv_robust(path: Path) -> pd.DataFrame:
    enc = detect_encoding(path)
    delim, quote = sniff_dialect(path, enc)
    # Try pandas read_csv with python engine to support complex quoting/newlines
    try:
        df = pd.read_csv(
            path,
            encoding=enc,
            engine="python",
            sep=delim,
            quotechar=quote,
            doublequote=True,
            skipinitialspace=True,
            dtype=str,
            keep_default_na=False,
            on_bad_lines="warn",
        )
    except Exception:
        # Fallback: read via csv into rows, then DataFrame
        with open(path, "r", encoding=enc, errors="replace", newline="") as f:
            reader = csv.reader(f, delimiter=delim, quotechar=quote, doublequote=True)
            rows = list(reader)
        if not rows:
            return pd.DataFrame()
        headers = rows[0]
        data = rows[1:]
        df = pd.DataFrame(data, columns=headers)

    # Normalize headers
    df.columns = normalize_headers(list(df.columns))

    # Drop any *_opcion columns
    opcion_cols = [c for c in df.columns if c.endswith("_opcion")]
    if opcion_cols:
        df = df.drop(columns=opcion_cols)

    # Keep only known canonical columns plus any unknowns for debugging
    for col in CANONICAL_COLS:
        if col not in df.columns:
            df[col] = ""

    # Order columns
    df = df[CANONICAL_COLS]

    # Strip whitespace around all string cells (column-wise to avoid applymap deprecation)
    df = df.apply(lambda col: col.map(lambda x: x.strip() if isinstance(x, str) else x))

    return df


def process_all() -> Tuple[List[Path], Path]:
    csv_paths = sorted(BASE_DIR.glob("feedback*.csv"))
    cleaned_paths: List[Path] = []
    frames: List[pd.DataFrame] = []

    for p in csv_paths:
        try:
            df = read_csv_robust(p)
            if df.empty:
                print(f"[WARN] {p.name}: sin filas")
                continue
            out = OUTPUT_DIR / f"{p.stem}_limpio.csv"
            # Limpiar TODOS los caracteres especiales + QUOTE_NONE + delimitador coma
            df_clean = df.copy()
            for col in df_clean.select_dtypes(include=['object']).columns:
                df_clean[col] = (df_clean[col].astype(str)
                                .str.replace(',', ' ')    # ELIMINAR comas
                                .str.replace('"', ' ')    # ELIMINAR comillas dobles
                                .str.replace("'", ' ')    # ELIMINAR comillas simples
                                .str.replace(';', ' ')    # ELIMINAR punto y coma
                                .str.replace('\n', ' ')   # Saltos de línea
                                .str.replace('\r', ' ')   # Retornos de carro
                                .str.replace('\t', ' ')   # Tabs
                                .str.replace('|', ' ')    # Pipes
                                .str.replace('\\', ' '))  # Barras invertidas
            # Limpiar espacios múltiples
            for col in df_clean.select_dtypes(include=['object']).columns:
                df_clean[col] = df_clean[col].str.replace(r'\s+', ' ', regex=True).str.strip()
            df_clean.to_csv(out, index=False, encoding="utf-8-sig", quoting=3)
            cleaned_paths.append(out)
            frames.append(df_clean)
            print(f"[OK]   {p.name} -> {out.name}  filas={len(df_clean)}")
        except Exception as e:
            print(f"[ERROR] {p.name}: {e}")

    unified = BASE_DIR / "validacion_unificado.csv"
    if frames:
        big = pd.concat(frames, ignore_index=True)
        # Remove exact duplicate rows across files, keep first
        big = big.drop_duplicates()
        # Limpiar TODOS los caracteres especiales en el unificado
        for col in big.select_dtypes(include=['object']).columns:
            big[col] = (big[col].astype(str)
                       .str.replace(',', ' ')    # ELIMINAR comas
                       .str.replace('"', ' ')    # ELIMINAR comillas dobles
                       .str.replace("'", ' ')    # ELIMINAR comillas simples
                       .str.replace(';', ' ')    # ELIMINAR punto y coma
                       .str.replace('\n', ' ')   # Saltos de línea
                       .str.replace('\r', ' ')   # Retornos de carro
                       .str.replace('\t', ' ')   # Tabs
                       .str.replace('|', ' ')    # Pipes
                       .str.replace('\\', ' '))  # Barras invertidas
        # Limpiar espacios múltiples
        for col in big.select_dtypes(include=['object']).columns:
            big[col] = big[col].str.replace(r'\s+', ' ', regex=True).str.strip()
        big.to_csv(unified, index=False, encoding="utf-8-sig", quoting=3)
        print(f"[OK]   Unificado -> {unified.name}  filas={len(big)}")
    else:
        print("[WARN] No se generó un archivo unificado: no hay datos")
    return cleaned_paths, unified


if __name__ == "__main__":
    process_all()
