import pandas as pd
import streamlit as st

COLUMNAS_REQUERIDAS = ["Mes", "IMACEC", "Precio", "Parque", "TPM", "Covid"]
DUMMIES_MES = {
    "Enero": 35790,
    "Febrero": 13850,
    "Marzo": 28200,
    "Abril": 5131,
    "Mayo": 6379,
    "Junio": -9603,
    "Julio": 1202,
    "Agosto": 9298,
    "Septiembre": 4579,
    "Octubre": 17680,
    "Noviembre": 7061,
    "Diciembre": 46840,
}


def calcular_demanda(df: pd.DataFrame, columna_precio: str) -> pd.Series:
    return (
        166500
        + 159100 * df["IMACEC"]
        + 0.0133 * df["Covid"]
        - 45.4491 * df[columna_precio]
        + 0.061 * df["Parque"]
        + 3746.5555 * df["TPM"]
        + df["dummy_mes"]
    )


st.set_page_config(page_title="Calculadora de Demanda Base", page_icon="📊")
st.title("Calculadora de Demanda Base")

archivo = st.file_uploader("Sube un archivo Excel (.xlsx)", type=["xlsx"])

if archivo is not None:
    try:
        df = pd.read_excel(archivo)

        st.subheader("Vista previa del Excel")
        st.dataframe(df.head(), use_container_width=True)

        columnas_faltantes = [col for col in COLUMNAS_REQUERIDAS if col not in df.columns]
        if columnas_faltantes:
            st.error("Faltan columnas requeridas: " + ", ".join(columnas_faltantes))
        else:
            cambio_precio = st.slider("Cambio en Precio (%)", min_value=-30, max_value=30, value=0)

            df_resultado = df.copy()
            df_resultado["dummy_mes"] = df_resultado["Mes"].map(DUMMIES_MES).fillna(0)
            df_resultado["Demanda_base"] = calcular_demanda(df_resultado, "Precio")

            df_resultado["Precio_simulado"] = df_resultado["Precio"] * (1 + cambio_precio / 100)
            df_resultado["Demanda_simulada"] = calcular_demanda(df_resultado, "Precio_simulado")
            df_resultado["Diferencia"] = df_resultado["Demanda_simulada"] - df_resultado["Demanda_base"]

            st.subheader("Resultado de simulación")
            st.dataframe(
                df_resultado[
                    [
                        "Mes",
                        "Precio",
                        "Precio_simulado",
                        "Demanda_base",
                        "Demanda_simulada",
                        "Diferencia",
                    ]
                ],
                use_container_width=True,
            )

            total_base = df_resultado["Demanda_base"].sum()
            total_simulada = df_resultado["Demanda_simulada"].sum()
            diferencia_total = df_resultado["Diferencia"].sum()

            st.subheader("Métricas resumen")
            col1, col2, col3 = st.columns(3)
            col1.metric("Suma Demanda_base", f"{total_base:,.2f}")
            col2.metric("Suma Demanda_simulada", f"{total_simulada:,.2f}")
            col3.metric("Diferencia total", f"{diferencia_total:,.2f}")

    except Exception as error:
        st.error(f"No se pudo leer el archivo: {error}")
else:
    st.info("Sube un archivo Excel para comenzar.")
