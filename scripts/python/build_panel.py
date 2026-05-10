"""
build_panel.py
Construcción del panel unificado EPH (puntual + continua)

Responsabilidades:
  - Lectura idempotente de todos los parquets en data/
  - Separación explícita de fuentes (puntual / continua)
  - Normalización y mapeo de etiquetas al esquema común
  - Construcción de variable de fecha para series de tiempo
  - Exportación del panel unificado a data/panel_eph.parquet

No realiza EDA ni visualizaciones — eso queda en los notebooks.
"""

import os
import pandas as pd
import numpy as np
from pathlib import Path

DATA_DIR   = Path("data")
OUTPUT_PATH = DATA_DIR / "panel_eph.parquet"

# =============================================================================
# Mapeos de etiquetas — esquema común
# Fuente puntual usa códigos numéricos; continua puede tener etiquetas de
# organize_labels(). Ambos se normalizan aquí al mismo string.
# =============================================================================

MAP_SEXO = {1: "Varon", 2: "Mujer"}

MAP_REGION = {
    1: "Gran Buenos Aires",
    40: "NOA", 41: "NEA", 42: "Cuyo",
    43: "Pampeana", 44: "Patagonia"
}

MAP_NIVEL_ED = {
    1: "Primario Incompleto",
    2: "Primario Completo",
    3: "Secundario Incompleto",
    4: "Secundario Completo",
    5: "Superior o Universitario Incompleto",
    6: "Superior o Universitario Completo",
    7: "Sin Instruccion",
    9: "NS/NR"
}

MAP_ESTADO = {
    0: "Sin respuesta",
    1: "Ocupado",
    2: "Desocupado",
    3: "Inactivo",
    4: "Menor de 10 anios"
}

MAP_CAT_OCUP = {
    0: "Inactivo",
    1: "Patron",
    2: "Cuenta Propia",
    3: "Obrero o empleado",
    4: "Trabajador familiar sin remuneracion",
    9: "NS/NR"
}

MAP_CAT_INAC = {
    0: "Ocupado",
    1: "Jubilado",
    2: "Rentista",
    3: "Estudiante",
    4: "Ama de Casa",
    5: "Menor de 6 anios",
    6: "Discapacitado",
    7: "Otros"
}

MAP_EMPLEO = {1: "Formal", 2: "Informal", 9: "NS/NR"}

MAP_PP07H = {0: np.nan, 1: "Si", 2: "No"}

MAP_CH08 = {
    1: "Obra Social, PAMI",
    2: "Mutual, Prepagas, Servicio de Emergencia",
    3: "Planes y Seguros Publicos",
    4: "No paga ni le descuentan",
    9: "NS/NR",
    12: "Obra Social y Mutual/Prepagas",
    13: "Obra Social y Planes Publicos",
    23: "Mutual/Prepagas y Planes Publicos",
    123: "Obra Social, Mutual/Prepagas y Planes Publicos"
}


MAP_RAMA = {
    1: "Actividades Primarias",
    2: "Ind.alimentos, bebidas y tabaco",
    3: "Ind.Textiles, confecciones y calzado",
    4: "Ind.Prod.quimicos y de la refinación petróleo y combustible nuclear",
    5: "Ind.Prod.metálicos, maquinarias y equipos",
    6: "Otras industrias manufactureras",
    7: "Suministro de electricidad, gas y agua",
    8: "Construcción",
    9: "Comercio al por Mayor",
   10: "Comercio al por Menor",
   11: "Restaurantes y Hoteles",
   12: "Transporte Servicios Conexos de Transporte y comunic.",
   14: "Intermediacion Financiera",
   15: "Actividades inmobiliarias, empresariales y de alquiler",
   16: "Administración Pública y Defensa",
   17: "Enseñanza",
   18: "Servicios Sociales y de Salud",
   19: "Otras Actividades de Servicios Comunitarios y sociales",
   20: "Servicios de Reparación",
   21: "Hogares privados con serv.doméstico.",
   22: "Otros Servicios personales",
   89: "Nuevos Trabajadores",
   99: "Sin especificar"
}

# =============================================================================
# Lectura de parquets
# =============================================================================

def leer_parquets(data_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Lee todos los parquets del directorio y los separa por fuente.
    Retorna (df_puntual, df_continua).
    Idempotente: el resultado depende solo del contenido de data/.
    """
    puntual   = []
    continua  = []

    archivos = sorted(data_dir.glob("*.parquet"))
    archivos = [f for f in archivos if f.name != "panel_eph.parquet"]

    for path in archivos:
        df = pd.read_parquet(path)
        fuente = df["FUENTE_BASE"].iloc[0] if "FUENTE_BASE" in df.columns else None

        if fuente == "puntual":
            puntual.append(df)
            print(f"  [puntual]   {path.name} — {len(df):,} filas")
        elif fuente == "continua":
            continua.append(df)
            print(f"  [continua]  {path.name} — {len(df):,} filas")
        else:
            print(f"  [?]         {path.name} — FUENTE_BASE ausente, omitido")

    df_puntual  = pd.concat(puntual,  ignore_index=True) if puntual  else pd.DataFrame()
    df_continua = pd.concat(continua, ignore_index=True) if continua else pd.DataFrame()

    return df_puntual, df_continua


# =============================================================================
# Normalización
# =============================================================================

def _aplicar_map_seguro(series: pd.Series, mapping: dict) -> pd.Series:
    """
    Aplica un mapping numérico a una serie, tolerando que la serie ya
    contenga strings (caso: organize_labels() ya etiquetó en R).
    """
    if pd.api.types.is_numeric_dtype(series):
        return series.map(mapping)
    # Ya es string — devolver tal cual (organize_labels lo hizo en R)
    return series


def normalizar(df: pd.DataFrame, fuente: str) -> pd.DataFrame:
    """
    Aplica etiquetas y transformaciones al esquema común.
    fuente: "puntual" | "continua"
    """
    if df.empty:
        return df

    df = df.copy()

    # --- Etiquetas comunes ---
    df["CH04"]     = _aplicar_map_seguro(df["CH04"],     MAP_SEXO)
    df["REGION"]   = _aplicar_map_seguro(df["REGION"],   MAP_REGION)
    df["NIVEL_ED"] = _aplicar_map_seguro(df["NIVEL_ED"], MAP_NIVEL_ED)
    df["ESTADO"]   = _aplicar_map_seguro(df["ESTADO"],   MAP_ESTADO)
    df["CAT_OCUP"] = _aplicar_map_seguro(df["CAT_OCUP"], MAP_CAT_OCUP)
    df["CAT_INAC"] = _aplicar_map_seguro(df["CAT_INAC"], MAP_CAT_INAC)
    df["CH08"]     = _aplicar_map_seguro(df["CH08"],     MAP_CH08)
    df["PP07H"]    = _aplicar_map_seguro(df["PP07H"],    MAP_PP07H)
    df["RAMA"]     = _aplicar_map_seguro(df["RAMA"],     MAP_RAMA)


    # EMPLEO: solo continua post-2023
    if "EMPLEO" in df.columns:
        df["EMPLEO"] = _aplicar_map_seguro(df["EMPLEO"], MAP_EMPLEO)

    # --- Fecha para series de tiempo ---
    # Puntual: onda 1 ≈ abril, onda 2 ≈ octubre
    # Continua: trimestre → mes inicio del trimestre
    if fuente == "puntual":
        mes_map = {1: 4, 2: 10}
        df["mes"] = df["PERIODO"].astype("Int64").map(mes_map)
    else:
        mes_map = {1: 1, 2: 4, 3: 7, 4: 10}
        df["mes"] = df["PERIODO"].astype("Int64").map(mes_map)

    df["fecha"] = pd.to_datetime(
        df["ANO4"].astype("Int64").astype(str) + "-" +
        df["mes"].astype("Int64").astype(str).str.zfill(2) + "-01"
    )
    df = df.drop(columns=["mes"])

    # Categoría ocupacional unificada (CAT_OCUP + CAT_INAC)
    # Las columnas extra de la continua (caes_*, CATEGORIA, JERARQUIA, etc.)
    # fluyen sin modificación — NaN en registros de puntual
    df["desc_ocup"] = np.where(
        df["CAT_INAC"] == "Ocupado",
        df["CAT_OCUP"],
        df["CAT_INAC"]
    )

    return df


# =============================================================================
# Pipeline principal
# =============================================================================

def build_panel():
    print("=== build_panel.py ===\n")

    # Verificar si el panel ya existe (info, no bloquea re-build)
    if OUTPUT_PATH.exists():
        print(f"⚠  Panel existente encontrado: {OUTPUT_PATH}")
        print("   Se va a sobreescribir con los datos actuales de data/\n")

    print("Leyendo parquets...")
    df_puntual, df_continua = leer_parquets(DATA_DIR)

    print(f"\nRegistros puntual:  {len(df_puntual):>10,}")
    print(f"Registros continua: {len(df_continua):>10,}")

    print("\nNormalizando...")
    df_puntual  = normalizar(df_puntual,  "puntual")
    df_continua = normalizar(df_continua, "continua")

    panel = pd.concat([df_puntual, df_continua], ignore_index=True)
    panel = panel.sort_values(["fecha", "FUENTE_BASE"]).reset_index(drop=True)

    print(f"\nPanel unificado: {len(panel):,} registros")
    print(f"Rango temporal:  {panel['fecha'].min().date()} → {panel['fecha'].max().date()}")
    print(f"Fuentes:         {panel['FUENTE_BASE'].value_counts().to_dict()}")

    print(f"\nExportando → {OUTPUT_PATH}")
    panel.to_parquet(OUTPUT_PATH, index=False)
    print("✓ Completado")

    return panel


if __name__ == "__main__":
    panel = build_panel()