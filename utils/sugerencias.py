"""Lógica para determinar recetas disponibles e incompletas."""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, List

from utils.inventario import Inventario, normalizar_nombre


def analizar_receta_vs_inventario(receta: dict, inventario: Inventario) -> dict:
    """Analiza si una receta puede prepararse con el inventario actual."""
    faltantes = []
    total_ingredientes = len(receta.get("ingredientes", []))
    ingredientes_ok = 0

    for ingrediente in receta.get("ingredientes", []):
        nombre = normalizar_nombre(ingrediente["nombre"])
        requerido = float(ingrediente["cantidad"])
        unidad_req = ingrediente["unidad"].strip().lower()

        if nombre not in inventario:
            faltantes.append(
                {
                    "nombre": nombre,
                    "falta": requerido,
                    "unidad": unidad_req,
                    "motivo": "no_disponible",
                }
            )
            continue

        disponible = float(inventario[nombre]["cantidad"])
        unidad_inv = inventario[nombre]["unidad"]

        if unidad_inv != unidad_req:
            faltantes.append(
                {
                    "nombre": nombre,
                    "falta": requerido,
                    "unidad": unidad_req,
                    "motivo": f"unidad_incompatible ({unidad_inv})",
                }
            )
            continue

        if disponible < requerido:
            faltantes.append(
                {
                    "nombre": nombre,
                    "falta": round(requerido - disponible, 2),
                    "unidad": unidad_req,
                    "motivo": "cantidad_insuficiente",
                }
            )
            continue

        ingredientes_ok += 1

    porcentaje = (ingredientes_ok / total_ingredientes) * 100 if total_ingredientes else 0

    return {
        "receta": receta,
        "disponible": len(faltantes) == 0,
        "faltantes": faltantes,
        "porcentaje": round(porcentaje, 1),
    }


def generar_sugerencias(recetas: List[dict], inventario: Inventario) -> List[dict]:
    """Retorna análisis de todas las recetas, ordenadas por disponibilidad."""
    analisis = [analizar_receta_vs_inventario(receta, inventario) for receta in recetas]

    # Primero disponibles, luego por mayor porcentaje.
    analisis.sort(
        key=lambda item: (
            not item["disponible"],
            -item["porcentaje"],
            item["receta"]["nombre"].lower(),
        )
    )

    return analisis


def sugerir_lista_compras(recetas_analizadas: List[dict]) -> List[dict]:
    """Crea lista de compras agregada según ingredientes faltantes."""
    acumulado: Dict[tuple, float] = defaultdict(float)

    for item in recetas_analizadas:
        if item["disponible"]:
            continue

        for faltante in item["faltantes"]:
            llave = (faltante["nombre"], faltante["unidad"])
            acumulado[llave] += float(faltante["falta"])

    lista = [
        {"ingrediente": nombre, "cantidad_sugerida": round(cantidad, 2), "unidad": unidad}
        for (nombre, unidad), cantidad in sorted(acumulado.items())
    ]

    return lista
