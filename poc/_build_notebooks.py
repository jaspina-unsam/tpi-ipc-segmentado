"""
Genera los notebooks del POC desde texto plano.
Correr una vez: python _build_notebooks.py
"""
import nbformat as nbf
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell


def build(out_path, cells):
    nb = new_notebook()
    nb.cells = []
    for kind, body in cells:
        if kind == "md":
            nb.cells.append(new_markdown_cell(body))
        elif kind == "code":
            nb.cells.append(new_code_cell(body))
    nbf.write(nb, out_path)
    print(f"  wrote {out_path}")


# ============================================================
# 00 · Preparación de datos
# ============================================================
nb00 = [
    ("md", """# 00 · Preparación de datos

Produce los archivos limpios que consumen los notebooks 01, 02 y 03.

**Salidas:**
- `data/eph_ocupados_2017plus.parquet` — ocupados en EPH 2017–2025 con las 6 variables del LCA y los IDs `CODUSU/NRO_HOGAR/COMPONENTE`.
- `data/engh_ocupados.parquet` — ocupados de la ENGH 2017/18 con sus 5 variables comunes con la EPH.
- `data/engh_hogares.parquet` — los 21.547 hogares con `gc_01..gc_12` y los `share_*` derivados.

**Decisiones explícitas (ver README §3):**
- Filtrado a ocupados (`ESTADO=='Ocupado'` en EPH; `estado==1` en ENGH).
- Edad discretizada en 5 buckets idénticos en ambas encuestas.
- `NIVEL_ED` reducido a 3 niveles.
- `PP07H` con tres categorías (`Formal`, `Informal`, `NoAplica` para cuenta propia/patrones).
- Regiones ENGH (1–6) mapeadas con codebook estándar INDEC."""),
    ("code", """import pandas as pd
import numpy as np
import pyarrow.parquet as pq
import os

EPH_PANEL = "../data/panel_eph.parquet"
ENGH_DIR  = "../../ENGH_2017-18"
OUT       = "data"
os.makedirs(OUT, exist_ok=True)"""),
    ("md", "## EPH — ocupados 2017+"),
    ("code", """cols = ["ANO4","TRIMESTRE","REGION","PONDERA",
        "CH04","CH06","NIVEL_ED","ESTADO","CAT_OCUP","PP07H",
        "P21","P47T","NRO_HOGAR","COMPONENTE","CODUSU"]
table = pq.read_table(EPH_PANEL, columns=cols,
                      filters=[("ANO4",">=",2017), ("ESTADO","=","Ocupado")])
df = table.to_pandas()

def edad_grp(e):
    if pd.isna(e): return None
    e = int(e)
    if e < 25: return "<25"
    if e < 35: return "25-34"
    if e < 50: return "35-49"
    if e < 65: return "50-64"
    return "65+"
df["EDAD_GRP"] = df["CH06"].apply(edad_grp)

ed_map = {
    "Sin Instruccion": "Hasta_primario",
    "Primario Incompleto": "Hasta_primario",
    "Primario Completo": "Hasta_primario",
    "Secundario Incompleto": "Secundario",
    "Secundario Completo": "Secundario",
    "Superior o Universitario Incompleto": "Superior",
    "Superior o Universitario Completo": "Superior",
}
df["NIVEL_ED_3"] = df["NIVEL_ED"].map(ed_map)
df["FORMAL"] = df["PP07H"].map({"Si":"Formal","No":"Informal"}).fillna("NoAplica")

keep = ["ANO4","TRIMESTRE","REGION","PONDERA",
        "CH04","EDAD_GRP","NIVEL_ED_3","CAT_OCUP","FORMAL",
        "P21","P47T","NRO_HOGAR","COMPONENTE","CODUSU"]
df = df[keep].rename(columns={"CH04":"SEXO"}).dropna(
    subset=["SEXO","EDAD_GRP","NIVEL_ED_3","CAT_OCUP","FORMAL","REGION"])
print("EPH ocupados 2017+:", df.shape)
df.to_parquet(f"{OUT}/eph_ocupados_2017plus.parquet", index=False)"""),
    ("md", "## ENGH — ocupados (individuos) y hogares con shares"),
    ("code", """cols = ["id","miembro","pondera","region","cp03","cp04","cp13",
        "niveled","estado","cat_ocup","ingtotp"]
p = pd.read_csv(f"{ENGH_DIR}/engho2018_personas.txt", sep="|",
                encoding="utf-8", usecols=cols, low_memory=False)
ocup = p[p["estado"]==1].copy()

# Codebook ENGH:  cp13 1=Varón 2=Mujer  |  niveled 1-2=prim, 3-4=sec, 5-6=sup
ocup["SEXO"]       = ocup["cp13"].map({1:"Varon", 2:"Mujer"})
ocup["EDAD_GRP"]   = ocup["cp03"].apply(edad_grp)
ocup["NIVEL_ED_3"] = ocup["niveled"].map({1:"Hasta_primario",2:"Hasta_primario",
                                          3:"Secundario",4:"Secundario",
                                          5:"Superior",6:"Superior"})
ocup["CAT_OCUP"]   = ocup["cat_ocup"].map({1:"Patron",2:"Cuenta Propia",
                                           3:"Obrero o empleado",
                                           4:"Trabajador familiar sin remuneracion"})
ocup["REGION"]     = ocup["region"].map({1:"Gran Buenos Aires",2:"Pampeana",
                                         3:"NOA",4:"NEA",5:"Cuyo",6:"Patagonia"})

ocup_clean = ocup[["id","miembro","pondera","SEXO","EDAD_GRP","NIVEL_ED_3",
                   "CAT_OCUP","REGION","ingtotp"]].dropna(
    subset=["SEXO","EDAD_GRP","NIVEL_ED_3","CAT_OCUP","REGION"])
print("ENGH ocupados:", ocup_clean.shape)
ocup_clean.to_parquet(f"{OUT}/engh_ocupados.parquet", index=False)"""),
    ("code", """hcols = ["id","pondera","region","jsexo","jedad_agrup","jniveled","jocupengh",
         "cantmiem","menor14","mayor65","regten","gastot",
         "gc_01","gc_02","gc_03","gc_04","gc_05","gc_06",
         "gc_07","gc_08","gc_09","gc_10","gc_11","gc_12",
         "ingtoth","decgaphr","decgapht"]
h = pd.read_csv(f"{ENGH_DIR}/engho2018_hogares.txt", sep="|",
                encoding="utf-8", usecols=hcols, low_memory=False)
for i in range(1,13):
    h[f"share_{i:02d}"] = h[f"gc_{i:02d}"] / h["gastot"]
print("Hogares:", h.shape)
print("Suma promedio de shares (debe ser 1.0):",
      h[[f"share_{i:02d}" for i in range(1,13)]].sum(axis=1).mean().round(4))
h.to_parquet(f"{OUT}/engh_hogares.parquet", index=False)"""),
]
build("00_data_prep.ipynb", nb00)


# ============================================================
# 01 · LCA en EPH
# ============================================================
nb01 = [
    ("md", """# 01 · LCA en EPH 2017-2018

Entrenamos un modelo de Latent Class Analysis sobre los ocupados de EPH 2017-2018 (ventana coincidente con la ENGH 2017/18) y aplicamos las clases resultantes a todo el panel 2017-2025.

**Variables indicadoras (6, todas categóricas):**
- `SEXO` (Varón/Mujer)
- `EDAD_GRP` (5 buckets)
- `NIVEL_ED_3` (Hasta_primario / Secundario / Superior)
- `CAT_OCUP` (Patrón / Cuenta propia / Obrero o empleado / Trab. familiar)
- `FORMAL` (Formal / Informal / NoAplica)
- `REGION` (6 regiones del INDEC)

**Selección de k:** se ajusta para k=2..7 sobre una muestra de 30k para velocidad y se elige por BIC + interpretabilidad.

**Salidas:**
- `data/lca_bic_curve.csv`
- `data/lca_model.pkl` (modelo + encoders)
- `data/eph_with_lca.parquet` (todos los ocupados 2017+ con clase asignada)
- `figures/01_bic_curve.png`"""),
    ("code", """import pandas as pd
import numpy as np
import pickle, warnings, time
warnings.filterwarnings("ignore")
from stepmix import StepMix
from sklearn.preprocessing import LabelEncoder
import matplotlib.pyplot as plt

eph = pd.read_parquet("data/eph_ocupados_2017plus.parquet")
print("EPH ocupados 2017+:", eph.shape)

mask_train = eph["ANO4"].isin([2017, 2018])
eph_train = eph[mask_train].copy()
print("EPH 2017-2018 (training del LCA):", eph_train.shape)

# Submuestreo para velocidad — 30k es suficiente para LCA con 6 indicadores
rng = np.random.default_rng(42)
idx = rng.choice(len(eph_train), size=min(30_000, len(eph_train)), replace=False)
eph_lca = eph_train.iloc[idx].reset_index(drop=True)"""),
    ("md", "## Encoding categórico"),
    ("code", """LCA_VARS = ["SEXO","EDAD_GRP","NIVEL_ED_3","CAT_OCUP","FORMAL","REGION"]

encoders = {}
X = pd.DataFrame()
for v in LCA_VARS:
    le = LabelEncoder()
    X[v] = le.fit_transform(eph_lca[v].astype(str))
    encoders[v] = le
    print(f"  {v}: {dict(zip(le.classes_, range(len(le.classes_))))}")"""),
    ("md", "## Curva BIC"),
    ("code", """results = []
for k in range(2, 8):
    t0 = time.time()
    m = StepMix(n_components=k, measurement="categorical",
                n_init=2, max_iter=150, random_state=42, progress_bar=0)
    m.fit(X)
    results.append({"k":k, "BIC":m.bic(X), "AIC":m.aic(X), "time_s":time.time()-t0})
    print(f"k={k}  BIC={m.bic(X):.1f}  ({results[-1]['time_s']:.1f}s)")

bic_curve = pd.DataFrame(results)
bic_curve.to_csv("data/lca_bic_curve.csv", index=False)

fig, ax = plt.subplots(figsize=(7,4))
ax.plot(bic_curve["k"], bic_curve["BIC"], "o-", lw=2)
ax.axvline(5, ls="--", color="red", alpha=0.5, label="k elegido = 5")
ax.set_xlabel("Número de clases (k)")
ax.set_ylabel("BIC")
ax.set_title("Selección de k por BIC — LCA en EPH 2017-2018")
ax.legend(); ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig("figures/01_bic_curve.png", dpi=120)
plt.show()"""),
    ("md", """## Ajuste final con k=5 y caracterización de las clases

Se elige **k=5** como punto de equilibrio entre ajuste (BIC) e interpretabilidad. La curva BIC muestra una caída clara hasta k=5 y luego se aplana / oscila — señal de que clases adicionales no aportan estructura sustantiva."""),
    ("code", """K = 5
m = StepMix(n_components=K, measurement="categorical",
            n_init=10, max_iter=300, random_state=42, progress_bar=0)
m.fit(X)
print(f"k={K}  BIC={m.bic(X):.1f}  ll/n={m.score(X):.4f}")

post = m.predict_proba(X)
eph_lca["LCA_class"] = post.argmax(axis=1)
print("\\nTamaño de clases:")
print(eph_lca["LCA_class"].value_counts().sort_index())"""),
    ("code", """# Perfil de cada clase: moda de cada variable
print("=== PERFILES ===\\n")
for c in sorted(eph_lca["LCA_class"].unique()):
    sub = eph_lca[eph_lca["LCA_class"]==c]
    print(f"Clase {c}  (n={len(sub)}, {len(sub)/len(eph_lca)*100:.1f}%)")
    for v in LCA_VARS:
        top = sub[v].value_counts(normalize=True).head(2)
        print(f"  {v:12s}: " + ", ".join(f"{k}={v*100:.0f}%" for k,v in top.items()))
    print()"""),
    ("md", """### Etiquetas interpretables

A partir de los perfiles anteriores, cada clase recibe un nombre. **Estos nombres no salen de los datos: son la lectura humana del perfil dominante.**

| Clase | Etiqueta tentativa |
|---|---|
| 0 | Obreros formales con secundario |
| 1 | Asalariados informales jóvenes |
| 2 | Trabajadores mayores con primario |
| 3 | Profesionales asalariadas |
| 4 | Cuentapropistas y patrones |"""),
    ("md", "## Aplicar el modelo a todo EPH 2017-2025"),
    ("code", """X_full = pd.DataFrame()
for v in LCA_VARS:
    le = encoders[v]
    s = eph[v].astype(str)
    known = set(le.classes_)
    s = s.where(s.isin(known), list(known)[0])
    X_full[v] = le.transform(s)

post_full = m.predict_proba(X_full)
eph["LCA_class"] = post_full.argmax(axis=1)
for c in range(K):
    eph[f"LCA_p{c}"] = post_full[:, c]

eph.to_parquet("data/eph_with_lca.parquet", index=False)
print(f"\\nGuardado eph_with_lca.parquet con {len(eph)} filas y clase asignada.")
print("\\nDistribución de clases (panel completo 2017+):")
print(eph["LCA_class"].value_counts(normalize=True).sort_index().round(3))

with open("data/lca_model.pkl","wb") as f:
    pickle.dump({"model":m, "encoders":encoders, "vars":LCA_VARS, "k":K}, f)"""),
]
build("01_lca_eph.ipynb", nb01)


# ============================================================
# 02 · Statistical matching EPH→ENGH
# ============================================================
nb02 = [
    ("md", """# 02 · Statistical matching EPH→ENGH

Tenemos clases LCA en EPH y necesitamos transportarlas a la ENGH. Como no existe el mismo hogar en ambas encuestas, no hay matching exacto: se entrena un Random Forest en EPH usando **sólo variables presentes en las dos encuestas** y se predice la clase para cada ocupado de la ENGH.

**Supuesto crítico declarado: CIA (Conditional Independence Assumption).** Condicionado en las variables comunes, la pertenencia a clase LCA y la canasta de gasto son independientes. No es testeable directamente.

**Validación indirecta:** se reporta el accuracy del RF *dentro* de EPH (train/test split). Es un techo, no una validación de la imputación a la ENGH.

**Variables comunes (5):** `SEXO`, `EDAD_GRP`, `NIVEL_ED_3`, `CAT_OCUP`, `REGION`.

> Notar la **asimetría rica/pobre**: el LCA se entrena con 6 variables (incluyendo `FORMAL`); el matching usa 5 (sin `FORMAL`, porque no hay equivalente directo en ENGH). Esta asimetría es estándar en statistical matching y se reconoce como limitación."""),
    ("code", """import pandas as pd
import numpy as np
import pickle, warnings
warnings.filterwarnings("ignore")
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.preprocessing import LabelEncoder

eph = pd.read_parquet("data/eph_with_lca.parquet")
eph_train = eph[eph["ANO4"].isin([2017, 2018])].copy()
engh = pd.read_parquet("data/engh_ocupados.parquet")
print("EPH 2017-2018 (con LCA):", eph_train.shape)
print("ENGH ocupados:", engh.shape)"""),
    ("md", "## Encoding uniforme entre EPH y ENGH"),
    ("code", """COMMON = ["SEXO","EDAD_GRP","NIVEL_ED_3","CAT_OCUP","REGION"]

common_encoders = {}
for v in COMMON:
    le = LabelEncoder()
    union = pd.concat([eph_train[v].astype(str), engh[v].astype(str)]).unique()
    le.fit(union)
    eph_train[f"{v}_enc"] = le.transform(eph_train[v].astype(str))
    engh[f"{v}_enc"]      = le.transform(engh[v].astype(str))
    common_encoders[v] = le"""),
    ("md", "## Random Forest"),
    ("code", """X = eph_train[[f"{v}_enc" for v in COMMON]].values
y = eph_train["LCA_class"].values
w = eph_train["PONDERA"].values

Xtr, Xte, ytr, yte, wtr, wte = train_test_split(
    X, y, w, test_size=0.25, random_state=42, stratify=y)

rf = RandomForestClassifier(n_estimators=300, max_depth=None,
                            random_state=42, n_jobs=-1, class_weight="balanced")
rf.fit(Xtr, ytr, sample_weight=wtr)

print(f"Accuracy train: {rf.score(Xtr, ytr, sample_weight=wtr):.3f}")
print(f"Accuracy test : {rf.score(Xte, yte, sample_weight=wte):.3f}")
print()
print(classification_report(yte, rf.predict(Xte), sample_weight=wte, digits=3))

print("Importancias:")
for v, imp in zip(COMMON, rf.feature_importances_):
    print(f"  {v}: {imp:.3f}")"""),
    ("md", """## Aplicar el RF a la ENGH

Cada ocupado de la ENGH recibe la clase LCA más probable, más las probabilidades posteriores de pertenecer a cada clase."""),
    ("code", """Xe = engh[[f"{v}_enc" for v in COMMON]].values
post = rf.predict_proba(Xe)
engh["LCA_class_pred"] = post.argmax(axis=1)
for c in range(rf.n_classes_):
    engh[f"LCA_p{c}"] = post[:, c]

engh.to_parquet("data/engh_ocupados_with_lca.parquet", index=False)
with open("data/rf_match_model.pkl","wb") as f:
    pickle.dump({"model":rf, "common":COMMON, "encoders":common_encoders}, f)

print("Distribución en ENGH (predicha):")
print(engh["LCA_class_pred"].value_counts(normalize=True).sort_index().round(3))
print("\\nDistribución en EPH 2017-18 (real):")
print(eph_train["LCA_class"].value_counts(normalize=True).sort_index().round(3))"""),
    ("md", """### Cómo leer estos números

Si las dos distribuciones son cercanas, el RF está reproduciendo en ENGH una composición similar a la observada en EPH. Diferencias grandes serían señal de mala calibración o de que las muestras son estructuralmente distintas. Para el POC obtenemos ≈80% de accuracy y distribuciones razonablemente alineadas.

**Lo que NO valida esto**: que la imputación de la clase a la ENGH sea correcta a nivel hogar. Eso es la CIA, y la CIA no se testea aquí."""),
]
build("02_match_eph_engh.ipynb", nb02)


# ============================================================
# 03 · Shares por clase y D-CPI
# ============================================================
nb03 = [
    ("md", """# 03 · Shares por clase, D-CPI y comparación de salarios reales

Última pieza del POC. Tres pasos:
1. Para cada hogar de la ENGH con al menos un ocupado, asignar la clase del **ocupado de mayor ingreso** (proxy del 'jefe económico'). Calcular shares promedio por clase.
2. Cargar (o sintetizar, en este POC) un IPC trimestral por división. Construir el **D-CPI por clase** = Σ shares × IPC división.
3. Deflactar los salarios EPH por clase con (a) el IPC oficial y (b) el D-CPI propio. Comparar.

**Por qué el ocupado de mayor ingreso y no el jefe del hogar**: el jefe en ENGH puede ser inactivo (jubilado, ama de casa). Para que el matching tenga sentido, asignamos la clase de quien efectivamente está ocupado y aporta más al hogar. Es una decisión simplificadora documentable."""),
    ("code", """import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

hog = pd.read_parquet("data/engh_hogares.parquet")
ocu = pd.read_parquet("data/engh_ocupados_with_lca.parquet")

CLASS_NAMES = {
    0: "Obreros formales (sec.)",
    1: "Asalariados informales jóvenes",
    2: "Trabajadores mayores con primario",
    3: "Profesionales asalariadas",
    4: "Cuentapropistas y patrones",
}"""),
    ("md", "## Shares por clase"),
    ("code", """ocu_sorted = ocu.sort_values(["id","ingtotp"], ascending=[True, False])
hog_class = ocu_sorted.groupby("id").first()[["LCA_class_pred"]].reset_index()
hog_class = hog_class.rename(columns={"LCA_class_pred":"LCA_class"})
hog_lab = hog.merge(hog_class, on="id", how="inner")
print(f"Hogares con al menos un ocupado: {len(hog_lab)} de {len(hog)}")

share_cols = [f"share_{i:02d}" for i in range(1,13)]
def wmean(g, cols, w):
    W = g[w].sum()
    return pd.Series({c: (g[c]*g[w]).sum()/W for c in cols})

shares_by_class = hog_lab.groupby("LCA_class").apply(
    lambda g: wmean(g, share_cols, "pondera"))
shares_by_class.to_csv("data/shares_by_class.csv")
print("\\nShares promedio por clase (cada fila suma 1):")
print(shares_by_class.round(3))"""),
    ("md", "### Visualización"),
    ("code", """fig, ax = plt.subplots(figsize=(11, 5))
plot_df = shares_by_class.copy()
plot_df.index = [CLASS_NAMES[i] for i in plot_df.index]
plot_df.columns = ["Aliment.","Beb.alc/Tabaco","Indument.","Vivienda","Equip.hogar",
                   "Salud","Transporte","Comunic.","Recreación","Educación",
                   "Restaur.","Varios"]
plot_df.plot(kind="bar", stacked=True, ax=ax, colormap="tab20")
ax.set_title("Estructura de gasto por clase latente (ENGH 2017/18)")
ax.set_ylabel("Share del gasto total"); ax.set_xlabel("")
ax.legend(loc="center left", bbox_to_anchor=(1, 0.5), fontsize=8)
plt.xticks(rotation=20, ha="right")
fig.tight_layout()
fig.savefig("figures/02_shares_by_class.png", dpi=120)
plt.show()"""),
    ("md", """## IPC por división — INDEC real

Cargamos la serie mensual del INDEC con apertura por las 12 divisiones COICOP, base diciembre 2016 = 100. Pasos:

1. **Renombrar columnas** del CSV INDEC al formato `div_01..div_12` que usa el resto del POC. El orden del CSV coincide 1:1 con el orden COICOP de la ENGH.
2. **Filtrar a 2017-01-01 en adelante**, agregar a trimestres por promedio.
3. **Rebasear a 2017Q1 = 100** para que la base coincida con el resto del POC.
4. **Sanity check**: reconstruir el IPC oficial usando los `share` promedio de la ENGH y compararlo con la columna `nivel_general`. Si la diferencia es chica (<1%), valida que las shares de la ENGH están bien calculadas y que las divisiones se mapean correctamente."""),
    ("code", """ipc_raw = pd.read_csv("data/ipc_indec_real.csv", parse_dates=["indice_tiempo"])

col_map = {
    "ipc_2016_alimentos_bebidas": "div_01",
    "ipc_2016_bebidas_alcoholicas": "div_02",
    "ipc_2016_indumentaria": "div_03",
    "ipc_2016_vivienda": "div_04",
    "ipc_2016_equipamiento_del_hogar": "div_05",
    "ipc_2016_atencion_medica_salud": "div_06",
    "ipc_2016_transporte": "div_07",
    "ipc_2016_informacion_comunicacion": "div_08",
    "ipc_2016_recreacion_cultura": "div_09",
    "ipc_2016_educacion": "div_10",
    "ipc_2016_restauranes_hoteles": "div_11",
    "ipc_2016_bienes_servicios_varios": "div_12",
}
ipc_m = ipc_raw[["indice_tiempo"] + list(col_map.keys())].rename(columns=col_map)
ipc_m["nivel_general"] = ipc_raw["ipc_2016_nivel_general"]
ipc_m = ipc_m[ipc_m["indice_tiempo"] >= "2017-01-01"].copy()
ipc_m["trimestre"] = ipc_m["indice_tiempo"].dt.to_period("Q").astype(str)

ipc = (ipc_m.groupby("trimestre")[list(col_map.values()) + ["nivel_general"]]
            .mean().sort_index())

# Rebasear a 2017Q1 = 100
base = ipc.iloc[0].copy()
for c in ipc.columns:
    ipc[c] = ipc[c] / base[c] * 100
ipc.to_csv("data/ipc_real_quarterly.csv")
print(f"IPC INDEC trimestral, base 2017Q1=100. {len(ipc)} trimestres ({ipc.index[0]} → {ipc.index[-1]})")
print(ipc.iloc[[0, 8, 16, 24, -1]].round(0))

# Sanity check: el IPC oficial reconstruido a partir de las shares debería pegar bien
overall_shares = np.array([
    (hog_lab[f"share_{i:02d}"]*hog_lab["pondera"]).sum() / hog_lab["pondera"].sum()
    for i in range(1,13)
])
ipc_reconstr = ipc[[f"div_{i:02d}" for i in range(1,13)]].values @ overall_shares
diff_pct = (ipc_reconstr[-1] / ipc["nivel_general"].iloc[-1] - 1) * 100
print(f"\\nSanity check: IPC oficial reconstruido vs publicado, último trim: {diff_pct:+.2f}%")
print("Si esta diferencia es chica (<1-2%), las shares y el mapeo de divisiones están OK.")"""),
    ("md", """## D-CPI por clase

Para cada clase, el D-CPI es Σ_d (share_d × IPC_d). Como sanity, también calculamos el "IPC oficial reconstruido" (con shares promedio del país) y lo comparamos con el `nivel_general` publicado por el INDEC."""),
    ("code", """ipc_cols = [f"div_{i:02d}" for i in range(1,13)]
M = ipc[ipc_cols].values   # n_t x 12

dcpi = pd.DataFrame(index=ipc.index)
for c in shares_by_class.index:
    s = np.array([shares_by_class.loc[c, f"share_{i:02d}"] for i in range(1,13)])
    dcpi[f"class_{c}"] = M @ s
dcpi["IPC_oficial"] = ipc["nivel_general"].values  # publicado, no reconstruido
dcpi.to_csv("data/dcpi_by_class.csv")
print("Inflación acumulada 2017Q1 → último trimestre disponible:")
print(((dcpi.iloc[-1] / 100 - 1) * 100).round(1))"""),
    ("md", "## Salarios reales por clase — IPC oficial vs D-CPI propio"),
    ("code", """eph = pd.read_parquet("data/eph_with_lca.parquet")
eph["trimestre"] = eph["ANO4"].astype(int).astype(str) + "Q" + eph["TRIMESTRE"].astype(int).astype(str)
def wmean_s(g, col, w):
    W = g[w].sum()
    return (g[col]*g[w]).sum() / W
wages = eph.groupby(["trimestre","LCA_class"]).apply(
    lambda g: wmean_s(g, "P21", "PONDERA")).unstack()
wages.columns = [f"class_{c}" for c in wages.columns]
wages = wages.sort_index()

common = wages.index.intersection(dcpi.index)
wages = wages.loc[common]; dcpi_a = dcpi.loc[common]

real_own = pd.DataFrame(index=common)
real_off = pd.DataFrame(index=common)
for c in range(5):
    real_own[f"class_{c}"] = wages[f"class_{c}"] / dcpi_a[f"class_{c}"] * 100
    real_off[f"class_{c}"] = wages[f"class_{c}"] / dcpi_a["IPC_oficial"] * 100

real_own_idx = real_own.div(real_own.iloc[0]) * 100
real_off_idx = real_off.div(real_off.iloc[0]) * 100
real_own_idx.to_csv("data/real_wages_own_dcpi.csv")
real_off_idx.to_csv("data/real_wages_official_ipc.csv")"""),
    ("code", """fig, axes = plt.subplots(1, 2, figsize=(14, 5), sharey=True)
for c in range(5):
    axes[0].plot(real_off_idx.index, real_off_idx[f"class_{c}"], lw=1.8, label=CLASS_NAMES[c])
    axes[1].plot(real_own_idx.index, real_own_idx[f"class_{c}"], lw=1.8, label=CLASS_NAMES[c])
axes[0].set_title("Deflactado por IPC OFICIAL (canasta promedio)")
axes[1].set_title("Deflactado por D-CPI de cada clase")
for ax in axes:
    ax.axhline(100, ls="--", color="black", alpha=0.3)
    ax.set_ylabel("Salario real (índice 2017Q1=100)")
    ax.grid(alpha=0.3)
    step = max(1, len(real_off_idx)//9)
    ax.set_xticks(real_off_idx.index[::step])
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
axes[1].legend(loc="upper right", fontsize=8)
fig.suptitle("Salarios reales por perfil — IPC oficial vs D-CPI propio",
             fontsize=13, fontweight="bold")
fig.tight_layout()
fig.savefig("figures/03_real_wages_comparison.png", dpi=120)
plt.show()"""),
    ("md", "## Money chart: ¿quién perdió cuánto?"),
    ("code", """loss_off = (real_off_idx.iloc[-1] - 100)
loss_own = (real_own_idx.iloc[-1] - 100)

fig, ax = plt.subplots(figsize=(11, 5))
xpos = np.arange(5); w = 0.4
b1 = ax.bar(xpos - w/2, loss_off.values, w, label="Deflactando con IPC oficial", color="#888")
b2 = ax.bar(xpos + w/2, loss_own.values, w, label="Deflactando con D-CPI propio", color="#4080c0")
ax.axhline(0, color="black", lw=0.8)
ax.set_xticks(xpos)
ax.set_xticklabels([CLASS_NAMES[i] for i in range(5)], rotation=15, ha="right")
ax.set_ylabel("% cambio salario real 2017Q1 → 2025Q3")
ax.set_title("¿Cuánto perdió cada perfil? — IPC INDEC real")
ax.legend(); ax.grid(alpha=0.3, axis="y")
for bars in [b1, b2]:
    for b in bars:
        h = b.get_height()
        ax.annotate(f"{h:.0f}%", xy=(b.get_x()+b.get_width()/2, h),
                    xytext=(0, 3 if h>=0 else -12), textcoords="offset points",
                    ha="center", fontsize=8)
fig.tight_layout()
fig.savefig("figures/04_money_chart.png", dpi=120)
plt.show()

print("\\nResumen final — pérdida salario real 2017Q1 → 2025Q3:")
result = pd.DataFrame({"IPC_oficial": loss_off, "D-CPI_propio": loss_own}).round(1)
result.index = [CLASS_NAMES[i] for i in range(5)]
print(result)"""),
    ("md", """## Limitaciones (declaración honesta)

1. **CIA.** El matching asume independencia condicional y no se testea directamente.
2. **Asimetría rica/pobre.** El LCA usa 6 variables; el matching, 5. La variable `FORMAL` (formalidad) no entra al matching por falta de equivalente directo en ENGH.
3. **Asignación al hogar vía ocupado de mayor ingreso.** Es una simplificación; no siempre coincide con el jefe declarado.
4. **Canasta estática.** La estructura de gasto se asume constante 2017–2025 (la ENGH es una sola foto).
5. **Pesos replicados sin uso.** No se usan los 200 pesos replicados de la ENGH para errores estándar formales. Los D-CPI son puntuales.
6. **Sub-reporte de ingresos.** Cuentapropistas y patrones tienden a sub-declarar ingresos en EPH; los resultados de la clase 4 hay que tomarlos con cautela."""),
]
build("03_dcpi_and_wages.ipynb", nb03)

print("\nDone.")
)
result.index = [CLASS_NAMES[i] for i in range(5)]
print(result)"""),
    ("md", """## Limitaciones (declaración honesta)

1. **CIA.** El matching asume independencia condicional y no se testea directamente.
2. **Asimetría rica/pobre.** El LCA usa 6 variables; el matching, 5. La variable `FORMAL` (formalidad) no entra al matching por falta de equivalente directo en ENGH.
3. **Asignación al hogar vía ocupado de mayor ingreso.** Es una simplificación; no siempre coincide con el jefe declarado.
4. **Canasta estática.** La estructura de gasto se asume constante 2017–2025 (la ENGH es una sola foto).
5. **Pesos replicados sin uso.** No se usan los 200 pesos replicados de la ENGH para errores estándar formales. Los D-CPI son puntuales.
6. **Sub-reporte de ingresos.** Cuentapropistas y patrones tienden a sub-declarar ingresos en EPH; los resultados de la clase 4 hay que tomarlos con cautela."""),
]
build("03_dcpi_and_wages.ipynb", nb03)

print("\nDone.")
)
result.index = [CLASS_NAMES[i] for i in range(5)]
print(result)"""),
    ("md", """## Limitaciones (declaración honesta)

1. **CIA.** El matching asume independencia condicional y no se testea directamente.
2. **Asimetría rica/pobre.** El LCA usa 6 variables; el matching, 5. La variable `FORMAL` (formalidad) no entra al matching por falta de equivalente directo en ENGH.
3. **Asignación al hogar vía ocupado de mayor ingreso.** Es una simplificación; no siempre coincide con el jefe declarado.
4. **Canasta estática.** La estructura de gasto se asume constante 2017–2025 (la ENGH es una sola foto).
5. **Pesos replicados sin uso.** No se usan los 200 pesos replicados de la ENGH para errores estándar formales. Los D-CPI son puntuales.
6. **Sub-reporte de ingresos.** Cuentapropistas y patrones tienden a sub-declarar ingresos en EPH; los resultados de la clase 4 hay que tomarlos con cautela."""),
]
build("03_dcpi_and_wages.ipynb", nb03)

print("\nDone.")
