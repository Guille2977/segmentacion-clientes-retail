from pathlib import Path

import altair as alt
import joblib
import numpy as np
import pandas as pd
import streamlit as st

BASE = Path(__file__).parent
DATOS = BASE / "data" / "processed"
MODELOS = BASE / "models"
FIGURAS = BASE / "reports" / "figuras"

NOMBRES = {0: "Recientes ocasionales", 1: "Campeones", 2: "Inactivos", 3: "En riesgo"}
ORDEN = ["Campeones", "En riesgo", "Recientes ocasionales", "Inactivos"]
ACCIONES = {
    "Campeones": "Programa de fidelización, acceso anticipado a la campaña navideña y atención preferente.",
    "En riesgo": "Campaña de reactivación antes de la temporada alta (septiembre), con ofertas basadas en sus compras anteriores.",
    "Recientes ocasionales": "Incentivar la siguiente compra con recomendaciones de productos y envío gratis desde cierto monto.",
    "Inactivos": "Acciones de bajo costo (correo masivo) y medir la respuesta antes de invertir más.",
}

st.set_page_config(page_title="Segmentación de clientes", page_icon="🛍️", layout="wide")


@st.cache_data
def cargar_datos():
    rfm = pd.read_csv(DATOS / "rfm_segmentos.csv")
    mensual = pd.read_csv(DATOS / "ventas_mensuales.csv")
    paises = pd.read_csv(DATOS / "ventas_pais.csv")
    reglas = pd.read_csv(DATOS / "reglas_asociacion.csv")
    return rfm, mensual, paises, reglas


@st.cache_resource
def cargar_modelos():
    return joblib.load(MODELOS / "kmeans.pkl"), joblib.load(MODELOS / "scaler.pkl")


rfm, mensual, paises, reglas = cargar_datos()
kmeans, scaler = cargar_modelos()

# ---------- Menú lateral ----------
st.sidebar.title("Segmentación de clientes")
pagina = st.sidebar.radio(
    "Sección", ["Resumen del negocio", "Segmentos", "Productos que se compran juntos"]
)
st.sidebar.caption(
    "Datos: Online Retail II (UCI), dic-2009 a dic-2011. "
    "Incluye solo clientes identificados y compras de productos."
)

# ---------- Página 1: Resumen ----------
if pagina == "Resumen del negocio":
    st.title("Resumen del negocio")

    ventas_total = mensual["ventas"].sum()
    facturas = mensual["facturas"].sum()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Ventas", f"£{ventas_total / 1e6:,.2f} M")
    c2.metric("Clientes", f"{len(rfm):,}")
    c3.metric("Facturas", f"{facturas:,}")
    c4.metric("Ticket promedio", f"£{ventas_total / facturas:,.0f}")

    st.subheader("Ventas mensuales (£)")
    st.line_chart(mensual.set_index("mes")["ventas"])
    st.caption("Diciembre de 2011 está incompleto (datos hasta el día 9).")

    st.subheader("Top 10 países por ventas (£)")
    top = paises.head(10)
    grafico = alt.Chart(top).mark_bar().encode(
        x=alt.X("ventas:Q", title="Ventas (£)"),
        y=alt.Y("country:N", sort="-x", title=None),
    )
    st.altair_chart(grafico)

# ---------- Página 2: Segmentos ----------
elif pagina == "Segmentos":
    st.title("Segmentos de clientes")
    st.write("Clientes agrupados con K-Means según Recency, Frequency y Monetary (RFM).")

    resumen = (
        rfm.groupby("segmento_nombre")
        .agg(
            clientes=("customer_id", "count"),
            recency=("recency", "median"),
            frequency=("frequency", "median"),
            monetary=("monetary", "median"),
            ventas=("monetary", "sum"),
        )
        .reindex(ORDEN)
    )
    resumen["pct_clientes"] = resumen["clientes"] / resumen["clientes"].sum() * 100
    resumen["pct_ventas"] = resumen["ventas"] / resumen["ventas"].sum() * 100

    comparacion = (
        resumen[["pct_clientes", "pct_ventas"]]
        .rename(columns={"pct_clientes": "% de clientes", "pct_ventas": "% de ventas"})
        .reset_index()
        .melt(id_vars="segmento_nombre", var_name="medida", value_name="porcentaje")
    )
    grafico = alt.Chart(comparacion).mark_bar().encode(
        x=alt.X("segmento_nombre:N", sort=ORDEN, title=None, axis=alt.Axis(labelAngle=0)),
        xOffset="medida:N",
        y=alt.Y("porcentaje:Q", title="%"),
        color=alt.Color("medida:N", title=None),
    )
    st.altair_chart(grafico)
    st.info("El 19 % de los clientes (Campeones) genera el 71.6 % de las ventas.")

    vista = pd.DataFrame({
        "Clientes": resumen["clientes"],
        "% clientes": resumen["pct_clientes"].round(1),
        "% ventas": resumen["pct_ventas"].round(1),
        "Última compra (días, mediana)": resumen["recency"].round(0),
        "Compras (mediana)": resumen["frequency"].round(1),
        "Gasto £ (mediana)": resumen["monetary"].round(0),
        "Acción recomendada": [ACCIONES[n] for n in resumen.index],
    })
    vista.index.name = "Segmento"
    st.dataframe(vista)

    with st.expander("Ver los segmentos en 2D (PCA) y la distribución de R, F y M"):
        st.image(str(FIGURAS / "segmentos_pca.png"))
        st.image(str(FIGURAS / "rfm_por_segmento.png"))

    st.subheader("Buscar un cliente")
    cid = st.number_input("Customer ID", min_value=0, value=int(rfm["customer_id"].iloc[0]), step=1)
    cliente = rfm[rfm["customer_id"] == cid]
    if cliente.empty:
        st.warning("No hay un cliente identificado con ese ID.")
    else:
        c = cliente.iloc[0]
        st.write(
            f"**Segmento:** {c['segmento_nombre']} · **País:** {c['country']} · "
            f"**Última compra:** hace {c['recency']} días · **Compras:** {c['frequency']} · "
            f"**Gasto:** £{c['monetary']:,.2f}"
        )
        st.write(f"**Acción recomendada:** {ACCIONES[c['segmento_nombre']]}")

    st.subheader("Clasificar un cliente nuevo")
    st.write("Ingresa su comportamiento de compra y el modelo le asigna un segmento.")
    c1, c2, c3 = st.columns(3)
    r = c1.number_input("Días desde la última compra", min_value=0, max_value=1000, value=30)
    f = c2.number_input("Número de compras", min_value=1, max_value=500, value=5)
    m = c3.number_input("Gasto total (£)", min_value=1.0, max_value=1_000_000.0, value=1000.0)

    X = np.log1p(pd.DataFrame({"recency": [r], "frequency": [f], "monetary": [m]}))
    segmento = NOMBRES[int(kmeans.predict(scaler.transform(X))[0])]
    st.success(f"Segmento asignado: **{segmento}**. {ACCIONES[segmento]}")

# ---------- Página 3: Reglas de asociación ----------
else:
    st.title("Productos que se compran juntos")
    st.write(
        "Reglas de asociación (FP-Growth) sobre las facturas del Reino Unido. "
        "Se leen así: quien compra el primer producto suele comprar también el segundo."
    )

    c1, c2 = st.columns(2)
    lift_min = c1.slider(
        "Lift mínimo",
        float(reglas["lift"].min()), float(reglas["lift"].max()), float(reglas["lift"].min()),
    )
    buscar = c2.text_input("Buscar producto (nombre en inglés)")

    filtro = reglas[reglas["lift"] >= lift_min]
    if buscar:
        filtro = filtro[
            filtro["si_compra"].str.contains(buscar, case=False)
            | filtro["tambien_compra"].str.contains(buscar, case=False)
        ]

    st.dataframe(pd.DataFrame({
        "Si compra": filtro["si_compra"],
        "También compra": filtro["tambien_compra"],
        "Support %": (filtro["support"] * 100).round(1),
        "Confidence %": (filtro["confidence"] * 100).round(1),
        "Lift": filtro["lift"].round(2),
    }), hide_index=True)

    st.caption(
        "Support: % de facturas con ambos productos. "
        "Confidence: % de las facturas con el primer producto que también tienen el segundo. "
        "Lift: cuántas veces más probable es la compra conjunta que por azar."
    )