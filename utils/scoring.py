# utils/scoring.py — Lógica de puntaje del Prode

import pandas as pd
from utils.data_loader import read_participantes, read_pronosticos, read_resultados
from config import PUNTOS_EXACTO, PUNTOS_RESULTADO, PUNTOS_ERROR


def calcular_puntaje_partido(
    g_local_pron: int,
    g_visit_pron: int,
    g_local_real: int,
    g_visit_real: int,
) -> tuple[int, str]:
    """
    Calcula los puntos obtenidos para un partido individual.
    Retorna (puntos, descripción).
    """
    if int(g_local_pron) == int(g_local_real) and int(g_visit_pron) == int(g_visit_real):
        return PUNTOS_EXACTO, "✅ Exacto"

    # Determinar resultado pronosticado y real
    def resultado(gl, gv):
        if gl > gv:
            return "L"
        elif gl == gv:
            return "E"
        return "V"

    if resultado(g_local_pron, g_visit_pron) == resultado(g_local_real, g_visit_real):
        return PUNTOS_RESULTADO, "🟡 Resultado"

    return PUNTOS_ERROR, "❌ Error"


def calcular_ranking() -> pd.DataFrame:
    """
    Calcula el ranking completo de todos los participantes.
    Retorna un DataFrame ordenado por puntos.
    """
    participantes = read_participantes()
    pronosticos = read_pronosticos()
    resultados = read_resultados()

    if participantes.empty:
        return pd.DataFrame(
            columns=["Nombre", "Puntos", "✅ Exactos", "🟡 Result.", "❌ Errores", "Pronós."]
        )

    ranking = []

    for _, p in participantes.iterrows():
        if pronosticos.empty:
            user_prons = pd.DataFrame()
        else:
            user_prons = pronosticos[pronosticos["usuario_id"] == p["usuario_id"]]

        total_pts = 0
        exactos = 0
        resultados_ok = 0
        errores = 0
        pronosticados = len(user_prons)

        for _, pron in user_prons.iterrows():
            if resultados.empty:
                continue
            result = resultados[resultados["partido_id"] == pron["partido_id"]]
            if result.empty:
                continue

            r = result.iloc[0]
            pts, _ = calcular_puntaje_partido(
                pron["goles_local"], pron["goles_visitante"],
                r["goles_local"], r["goles_visitante"],
            )
            total_pts += pts
            if pts == PUNTOS_EXACTO:
                exactos += 1
            elif pts == PUNTOS_RESULTADO:
                resultados_ok += 1
            else:
                errores += 1

        ranking.append({
            "usuario_id": p["usuario_id"],
            "Nombre": p["nombre"],
            "Puntos": total_pts,
            "✅ Exactos": exactos,
            "🟡 Result.": resultados_ok,
            "❌ Errores": errores,
            "Pronós.": pronosticados,
        })

    df_ranking = (
        pd.DataFrame(ranking)
        .sort_values("Puntos", ascending=False)
        .reset_index(drop=True)
    )
    df_ranking.index = df_ranking.index + 1
    df_ranking.index.name = "Pos"
    return df_ranking
