"""App Streamlit: Qué Cocino Hoy."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from utils.inventario import (
    agregar_o_sumar_ingrediente,
    cargar_inventario,
    descontar_ingredientes,
    editar_ingrediente,
    eliminar_ingrediente,
    guardar_inventario,
    ingredientes_stock_bajo,
    inventario_a_lista_tabla,
)
from utils.recetas import cargar_recetas, filtrar_recetas
from utils.sugerencias import generar_sugerencias, sugerir_lista_compras

RUTA_INVENTARIO = Path("inventario.json")
RUTA_RECETAS = Path("recetas.json")


@st.cache_data(show_spinner=False)
def cargar_recetas_cache():
    return cargar_recetas(RUTA_RECETAS)


def recargar_inventario_sesion() -> dict:
    """Carga inventario en sesión para mantener estado entre interacciones."""
    if "inventario" not in st.session_state:
        st.session_state.inventario = cargar_inventario(RUTA_INVENTARIO)
    return st.session_state.inventario


def guardar_inventario_sesion() -> None:
    guardar_inventario(RUTA_INVENTARIO, st.session_state.inventario)


def main() -> None:
    st.set_page_config(page_title="Qué Cocino Hoy", page_icon="🍳", layout="wide")

    st.title("🍳 Qué Cocino Hoy")
    st.caption("Gestiona tu inventario del hogar y encuentra recetas posibles con lo que ya tienes.")

    inventario = recargar_inventario_sesion()
    recetas = cargar_recetas_cache()

    st.sidebar.header("Navegación")
    seccion = st.sidebar.radio(
        "Ir a",
        ["Inventario", "Compras", "Recetas y sugerencias"],
        index=0,
    )

    if seccion == "Inventario":
        render_inventario(inventario)
    elif seccion == "Compras":
        render_compras(inventario)
    else:
        render_recetas_sugerencias(inventario, recetas)


def render_inventario(inventario: dict) -> None:
    st.subheader("📦 Inventario actual")
    filas = inventario_a_lista_tabla(inventario)

    if filas:
        st.dataframe(pd.DataFrame(filas), use_container_width=True, hide_index=True)
    else:
        st.info("El inventario está vacío.")

    alertas = ingredientes_stock_bajo(inventario, umbral=2)
    if alertas:
        st.warning("⚠️ Stock bajo detectado (<= 2 unidades):")
        st.table(pd.DataFrame(alertas))

    st.markdown("---")
    st.markdown("### ➕ Agregar ingrediente")
    with st.form("form_agregar_ingrediente"):
        col1, col2, col3 = st.columns(3)
        with col1:
            nombre = st.text_input("Ingrediente", placeholder="ej: tomate")
        with col2:
            cantidad = st.number_input("Cantidad", min_value=0.0, value=1.0, step=0.5)
        with col3:
            unidad = st.text_input("Unidad", value="unidad")

        enviado = st.form_submit_button("Guardar ingrediente")

    if enviado:
        ok, mensaje = agregar_o_sumar_ingrediente(inventario, nombre, cantidad, unidad)
        if ok:
            guardar_inventario_sesion()
            st.success(mensaje)
            st.rerun()
        else:
            st.error(mensaje)

    st.markdown("### ✏️ Editar o eliminar ingrediente")
    if inventario:
        nombres = sorted(inventario.keys())
        seleccionado = st.selectbox("Selecciona ingrediente", nombres)

        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            nueva_cantidad = st.number_input(
                "Nueva cantidad",
                min_value=0.0,
                value=float(inventario[seleccionado]["cantidad"]),
                step=0.5,
                key="editar_cantidad",
            )
        with col2:
            nueva_unidad = st.text_input(
                "Nueva unidad", value=inventario[seleccionado]["unidad"], key="editar_unidad"
            )
        with col3:
            st.write("")
            st.write("")
            boton_editar = st.button("Actualizar", type="primary")
            boton_eliminar = st.button("Eliminar")

        if boton_editar:
            ok, mensaje = editar_ingrediente(inventario, seleccionado, nueva_cantidad, nueva_unidad)
            if ok:
                guardar_inventario_sesion()
                st.success(mensaje)
                st.rerun()
            else:
                st.error(mensaje)

        if boton_eliminar:
            ok, mensaje = eliminar_ingrediente(inventario, seleccionado)
            if ok:
                guardar_inventario_sesion()
                st.success(mensaje)
                st.rerun()
            else:
                st.error(mensaje)


def render_compras(inventario: dict) -> None:
    st.subheader("🛒 Registrar compra")
    st.write("Cada compra se guarda automáticamente en el inventario.")

    with st.form("form_compras"):
        col1, col2, col3 = st.columns(3)
        with col1:
            producto = st.text_input("Producto comprado", placeholder="ej: arroz")
        with col2:
            cantidad = st.number_input("Cantidad comprada", min_value=0.0, value=1.0, step=0.5)
        with col3:
            unidad = st.text_input("Unidad", value="g")

        registrar = st.form_submit_button("Registrar compra")

    if registrar:
        ok, mensaje = agregar_o_sumar_ingrediente(inventario, producto, cantidad, unidad)
        if ok:
            guardar_inventario_sesion()
            st.success(f"Compra registrada. {mensaje}")
            st.rerun()
        else:
            st.error(mensaje)


def render_recetas_sugerencias(inventario: dict, recetas: list[dict]) -> None:
    st.subheader("🍽️ Recetas y sugerencias")

    col_filtro1, col_filtro2 = st.columns(2)
    with col_filtro1:
        categorias = sorted({receta.get("categoria", "general") for receta in recetas})
        opcion_categoria = st.selectbox("Filtrar por categoría", ["todas", *categorias])
    with col_filtro2:
        busqueda = st.text_input("Buscar receta por nombre", placeholder="ej: tortilla")

    recetas_filtradas = filtrar_recetas(recetas, opcion_categoria, busqueda)
    analisis = generar_sugerencias(recetas_filtradas, inventario)

    if not analisis:
        st.info("No hay recetas para mostrar con los filtros seleccionados.")
        return

    for idx, item in enumerate(analisis):
        receta = item["receta"]
        disponible = item["disponible"]
        badge = "✅ Disponible" if disponible else "❌ Incompleta"

        with st.expander(f"{receta['nombre']} | {receta['categoria']} | {receta['tiempo']} min | {badge}"):
            st.write(f"**Coincidencia de ingredientes:** {item['porcentaje']}%")
            st.markdown("**Ingredientes requeridos:**")
            st.table(pd.DataFrame(receta["ingredientes"]))

            if disponible:
                if st.button("Cocinar", key=f"cocinar_{idx}"):
                    ok, mensaje = descontar_ingredientes(inventario, receta["ingredientes"])
                    if ok:
                        guardar_inventario_sesion()
                        st.success(f"¡Listo! Cocinaste {receta['nombre']}. {mensaje}")
                        st.rerun()
                    else:
                        st.error(mensaje)
            else:
                st.markdown("**Falta comprar:**")
                st.table(pd.DataFrame(item["faltantes"]))

    st.markdown("---")
    st.markdown("### 🧾 Lista de compras sugerida")
    lista_compras = sugerir_lista_compras(analisis)
    if lista_compras:
        st.dataframe(pd.DataFrame(lista_compras), use_container_width=True, hide_index=True)
    else:
        st.success("No faltan ingredientes para las recetas filtradas. ¡Excelente!")


if __name__ == "__main__":
    main()
