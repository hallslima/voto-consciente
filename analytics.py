from __future__ import annotations

from typing import Iterable

import plotly.graph_objects as go


COLORS = ["#3B82F6", "#14B8A6", "#F59E0B", "#8B5CF6", "#EF4444", "#64748B", "#06B6D4", "#84CC16"]


def overall_bar(results):
    ordered = sorted(results, key=lambda item: item.score)
    figure = go.Figure(
        go.Bar(
            x=[item.score for item in ordered],
            y=[item.name for item in ordered],
            orientation="h",
            marker_color=["#14B8A6" if item.coverage == 100 else "#3B82F6" for item in ordered],
            text=[f"{item.score:.1f}%" for item in ordered],
            textposition="auto",
            customdata=[[item.party, item.coverage] for item in ordered],
            hovertemplate=(
                "<b>%{y}</b><br>Partido: %{customdata[0]}<br>"
                "Correspondência: %{x:.1f}%<br>Cobertura: %{customdata[1]:.0f}%<extra></extra>"
            ),
        )
    )
    figure.update_layout(
        title="Comparação geral das candidaturas",
        xaxis_title="Índice de Correspondência Temática (%)",
        yaxis_title="",
        xaxis_range=[0, 100],
        height=440,
        margin=dict(l=15, r=15, t=60, b=25),
    )
    return figure


def candidate_radar(result):
    classified = [detail for detail in result.details if detail["similarity"] is not None]
    categories = [detail["theme"] for detail in classified]
    values = [detail["theme_score"] for detail in classified]
    weights = [detail["weight"] for detail in classified]
    if not categories:
        return go.Figure()
    categories_closed = categories + [categories[0]]
    values_closed = values + [values[0]]
    weights_closed = weights + [weights[0]]
    figure = go.Figure(
        go.Scatterpolar(
            r=values_closed,
            theta=categories_closed,
            fill="toself",
            name=result.name,
            line_color="#3B82F6",
            customdata=weights_closed,
            hovertemplate=(
                "<b>%{theta}</b><br>Compatibilidade: %{r:.0f}%<br>"
                "Peso informado: %{customdata}<extra></extra>"
            ),
        )
    )
    figure.update_layout(
        title=f"Correspondência por tema: {result.name}",
        polar=dict(radialaxis=dict(visible=True, range=[0, 100], ticksuffix="%")),
        showlegend=False,
        height=470,
        margin=dict(l=45, r=45, t=70, b=35),
    )
    return figure


def top_three_by_theme(results: Iterable):
    top_results = list(results)[:3]
    themes: list[str] = []
    for result in top_results:
        for detail in result.details:
            if detail["similarity"] is not None and detail["theme"] not in themes:
                themes.append(detail["theme"])

    figure = go.Figure()
    for index, result in enumerate(top_results):
        by_theme = {
            detail["theme"]: detail["theme_score"]
            for detail in result.details
            if detail["similarity"] is not None
        }
        figure.add_trace(
            go.Bar(
                name=result.name,
                x=themes,
                y=[by_theme.get(theme) for theme in themes],
                marker_color=COLORS[index],
                hovertemplate="<b>%{x}</b><br>Compatibilidade: %{y:.0f}%<extra>%{fullData.name}</extra>",
            )
        )
    figure.update_layout(
        title="Comparação temática dos três primeiros resultados",
        barmode="group",
        yaxis_title="Correspondência no tema (%)",
        yaxis_range=[0, 100],
        height=470,
        margin=dict(l=15, r=15, t=60, b=90),
        legend_title="Candidatura",
    )
    return figure
