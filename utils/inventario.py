"""Utilidades para gestionar el inventario de cocina."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Tuple


Inventario = Dict[str, Dict[str, float | str]]


def cargar_json(ruta: str | Path, valor_por_defecto):
    """Carga un archivo JSON y devuelve un valor por defecto si no existe."""
    ruta = Path(ruta)
    if not ruta.exists():
        return valor_por_defecto

    with ruta.open("r", encoding="utf-8") as archivo:
        return json.load(archivo)


def guardar_json(ruta: str | Path, datos) -> None:
    """Guarda datos en formato JSON con codificación UTF-8."""
    ruta = Path(ruta)
    with ruta.open("w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, ensure_ascii=False, indent=2)


def cargar_inventario(ruta: str | Path) -> Inventario:
    """Carga inventario desde JSON y normaliza los nombres."""
    inventario = cargar_json(ruta, {})
    inventario_normalizado: Inventario = {}

    for nombre, info in inventario.items():
        nombre_normalizado = normalizar_nombre(nombre)
        inventario_normalizado[nombre_normalizado] = {
            "cantidad": float(info.get("cantidad", 0)),
            "unidad": str(info.get("unidad", "unidad")),
        }

    return inventario_normalizado


def guardar_inventario(ruta: str | Path, inventario: Inventario) -> None:
    """Guarda inventario en JSON ordenado alfabéticamente."""
    inventario_ordenado = dict(sorted(inventario.items(), key=lambda item: item[0]))
    guardar_json(ruta, inventario_ordenado)


def normalizar_nombre(nombre: str) -> str:
    """Normaliza nombres para evitar duplicados por mayúsculas/espacios."""
    return nombre.strip().lower()


def agregar_o_sumar_ingrediente(
    inventario: Inventario, nombre: str, cantidad: float, unidad: str
) -> Tuple[bool, str]:
    """Agrega un ingrediente nuevo o suma cantidad si ya existe."""
    nombre_norm = normalizar_nombre(nombre)

    if not nombre_norm:
        return False, "El nombre del ingrediente no puede estar vacío."

    if cantidad <= 0:
        return False, "La cantidad debe ser mayor a cero."

    unidad = unidad.strip().lower() or "unidad"

    if nombre_norm in inventario:
        unidad_existente = inventario[nombre_norm]["unidad"]
        if unidad_existente != unidad:
            return (
                False,
                f"La unidad de '{nombre_norm}' ya existe como '{unidad_existente}'.",
            )

        inventario[nombre_norm]["cantidad"] = float(inventario[nombre_norm]["cantidad"]) + cantidad
        return True, f"Se sumó {cantidad} {unidad} de {nombre_norm}."

    inventario[nombre_norm] = {"cantidad": float(cantidad), "unidad": unidad}
    return True, f"Se agregó {nombre_norm} al inventario."


def editar_ingrediente(
    inventario: Inventario, nombre_original: str, cantidad: float, unidad: str
) -> Tuple[bool, str]:
    """Edita cantidad y unidad de un ingrediente existente."""
    nombre_norm = normalizar_nombre(nombre_original)

    if nombre_norm not in inventario:
        return False, "El ingrediente no existe en el inventario."

    if cantidad < 0:
        return False, "La cantidad no puede ser negativa."

    unidad = unidad.strip().lower() or "unidad"
    inventario[nombre_norm] = {"cantidad": float(cantidad), "unidad": unidad}
    return True, f"Se actualizó {nombre_norm}."


def eliminar_ingrediente(inventario: Inventario, nombre: str) -> Tuple[bool, str]:
    """Elimina un ingrediente del inventario."""
    nombre_norm = normalizar_nombre(nombre)

    if nombre_norm not in inventario:
        return False, "El ingrediente no existe."

    del inventario[nombre_norm]
    return True, f"Se eliminó {nombre_norm} del inventario."


def descontar_ingredientes(
    inventario: Inventario, ingredientes_receta: List[dict]
) -> Tuple[bool, str]:
    """Descuenta ingredientes del inventario si hay stock suficiente."""
    # Validación previa: no se descuenta nada si falla algún ingrediente.
    for ingrediente in ingredientes_receta:
        nombre = normalizar_nombre(ingrediente["nombre"])
        requerido = float(ingrediente["cantidad"])
        unidad = ingrediente["unidad"].strip().lower()

        if nombre not in inventario:
            return False, f"No existe '{nombre}' en el inventario."

        disponible = float(inventario[nombre]["cantidad"])
        unidad_inv = inventario[nombre]["unidad"]

        if unidad != unidad_inv:
            return False, (
                f"Unidad incompatible para '{nombre}': receta usa '{unidad}' y stock está en '{unidad_inv}'."
            )

        if disponible < requerido:
            return False, f"Stock insuficiente de '{nombre}'. Requiere {requerido} {unidad}."

    # Descuento real después de validar todo.
    for ingrediente in ingredientes_receta:
        nombre = normalizar_nombre(ingrediente["nombre"])
        requerido = float(ingrediente["cantidad"])
        inventario[nombre]["cantidad"] = max(0.0, float(inventario[nombre]["cantidad"]) - requerido)

    return True, "Ingredientes descontados correctamente."


def inventario_a_lista_tabla(inventario: Inventario) -> List[dict]:
    """Convierte el inventario a lista para mostrar en tablas."""
    filas = []
    for nombre, info in sorted(inventario.items()):
        filas.append(
            {
                "ingrediente": nombre,
                "cantidad": float(info["cantidad"]),
                "unidad": info["unidad"],
            }
        )
    return filas


def ingredientes_stock_bajo(inventario: Inventario, umbral: float = 2) -> List[dict]:
    """Retorna ingredientes con cantidad menor o igual al umbral."""
    alertas = []
    for nombre, info in sorted(inventario.items()):
        if float(info["cantidad"]) <= umbral:
            alertas.append(
                {
                    "ingrediente": nombre,
                    "cantidad": float(info["cantidad"]),
                    "unidad": info["unidad"],
                }
            )
    return alertas
