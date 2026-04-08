"""Utilidades para cargar y filtrar recetas."""

from __future__ import annotations

from pathlib import Path
from typing import List

from utils.inventario import cargar_json, normalizar_nombre


Receta = dict


def cargar_recetas(ruta: str | Path) -> List[Receta]:
    """Carga las recetas desde JSON."""
    recetas = cargar_json(ruta, [])

    # Normaliza nombres de ingredientes para facilitar comparación.
    for receta in recetas:
        receta["nombre"] = receta.get("nombre", "Sin nombre")
        receta["categoria"] = receta.get("categoria", "general").strip().lower()
        receta["tiempo"] = int(receta.get("tiempo", 0))

        ingredientes = receta.get("ingredientes", [])
        for ingrediente in ingredientes:
            ingrediente["nombre"] = normalizar_nombre(ingrediente.get("nombre", ""))
            ingrediente["cantidad"] = float(ingrediente.get("cantidad", 0))
            ingrediente["unidad"] = ingrediente.get("unidad", "unidad").strip().lower()

    return recetas


def filtrar_recetas(
    recetas: List[Receta], categoria: str | None = None, texto_busqueda: str = ""
) -> List[Receta]:
    """Filtra recetas por categoría y texto de búsqueda."""
    resultado = recetas

    if categoria and categoria != "todas":
        categoria = categoria.strip().lower()
        resultado = [r for r in resultado if r.get("categoria", "") == categoria]

    texto = texto_busqueda.strip().lower()
    if texto:
        resultado = [r for r in resultado if texto in r.get("nombre", "").lower()]

    return resultado
