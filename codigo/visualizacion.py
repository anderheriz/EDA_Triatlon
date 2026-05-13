"""Funciones de visualizacion para el EDA de triatlon.
Las funciones estan pensadas para trabajar con el dataframe final `triatlon_clean`: una fila por atleta y carrera, con tiempos ya homogeneizados a segundos."""

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

PALETA_MODALIDAD = {"ironman": "#B32A2E","olimpica": "#1864AB",}

PALETA_SEGMENTOS = {"Natacion": "#0D758C","Bicicleta": "#9D361C","Carrera": "#1B813F","Transiciones": "#A8A8A8",}


def normalizar_genero(df):
    """Unifica las etiquetas de genero entre Ironman y World Triathlon."""
    df = df.copy()
    if "genero" in df.columns:
        df["genero"] = df["genero"].replace(
            {
                "female": "Female",
                "male": "Male",
                "F": "Female",
                "M": "Male",
                "Women": "Female",
                "Men": "Male",
            }
        )
    return df


def _orden_modalidades(df):
    """Devuelve las modalidades en un orden estable."""
    orden = [m for m in ["ironman", "olimpica"] if m in df["tipo_distancia"].unique()]
    resto = [m for m in df["tipo_distancia"].unique() if m not in orden]
    return orden + resto


def _formatear_ejes(ax):
    """Aplica limpieza visual comun a los graficos."""
    sns.despine(ax=ax)
    ax.grid(axis="y", color="#E7E2D6", linewidth=0.8)
    ax.grid(axis="x", visible=False)
    return ax


def configurar_estilo():
    """Aplica un estilo base comun para todos los graficos."""
    sns.set_theme(
        style="whitegrid",
        context="notebook",
        palette=list(PALETA_MODALIDAD.values()),
    )
    plt.rcParams["figure.figsize"] = (9, 5)
    plt.rcParams["axes.titlesize"] = 14
    plt.rcParams["axes.labelsize"] = 11
    plt.rcParams["legend.fontsize"] = 10
    plt.rcParams["axes.titleweight"] = "bold"
    plt.rcParams["figure.facecolor"] = "white"
    plt.rcParams["axes.facecolor"] = "white"


def preparar_df_graficos(df, posicion_max=None):
    """Elimina registros no comparables y recalcula porcentajes.

    En el dataset hay alguna fila con un segmento a 0 segundos. Para analisis de rendimiento, esos valores no son tiempos reales y deben excluirse 
    antes de graficar. Si se informa posicion_max, filtra por la columna posicion, que ya representa el ranking de cada carrera/genero."""

    df = normalizar_genero(df)
    columnas_tiempo = ["segundos_total", "segundos_natacion", "segundos_bicicleta", "segundos_carrera",]

    for col in columnas_tiempo:
        df = df[df[col].notna()]
        df = df[df[col] > 0]

    if posicion_max is not None:
        df = df[df["posicion"] <= posicion_max].copy()

    df["pct_natacion"] = df["segundos_natacion"] / df["segundos_total"] * 100
    df["pct_bicicleta"] = df["segundos_bicicleta"] / df["segundos_total"] * 100
    df["pct_carrera"] = df["segundos_carrera"] / df["segundos_total"] * 100
    df["pct_transiciones"] = (df["segundos_t1"] + df["segundos_t2"]) / df["segundos_total"] * 100
    df["top_10"] = df["posicion"] <= 10
    return df


def grafico_muestra_por_modalidad_genero(df):
    """Grafico descriptivo: numero de atletas por modalidad y genero."""
    
    tabla = (df.groupby(["tipo_distancia", "genero"]).size().reset_index(name="resultados"))

    # Traducir etiquetas de genero para que la leyenda quede en español
    tabla["genero"] = tabla["genero"].replace({"Female": "Mujeres","Male": "Hombres"})

    fig, ax = plt.subplots(figsize=(8, 5))

    colores_genero = {"Mujeres": "#C44E52","Hombres": "#4C72B0",}

    sns.barplot(
        data=tabla,
        x="tipo_distancia",
        y="resultados",
        hue="genero",
        order=_orden_modalidades(df),
        palette=colores_genero,
        ax=ax,
    )

    for container in ax.containers:
        ax.bar_label(container, fmt="%.0f", padding=3, fontsize=9)

    ax.set_title("Muestra final por modalidad y género")
    ax.set_xlabel("Modalidad")
    ax.set_ylabel("Número de resultados")
    ax.tick_params(axis="x", rotation=0)

    # Leyenda sin titulo
    ax.legend(title=None, frameon=False, loc="upper left")

    _formatear_ejes(ax)
    plt.tight_layout()
    return ax



def grafico_peso_segmentos_apilado(df):
    """H1: barra apilada del porcentaje medio por segmento."""
    media_segmentos = df.groupby("tipo_distancia")[["pct_natacion", "pct_bicicleta", "pct_carrera", "pct_transiciones"]].mean()
    media_segmentos = media_segmentos.rename(
        columns={"pct_natacion": "Natacion", "pct_bicicleta": "Bicicleta", "pct_carrera": "Carrera", "pct_transiciones": "Transiciones",})
    media_segmentos = media_segmentos.loc[_orden_modalidades(df)]

    fig, ax = plt.subplots(figsize=(9, 4.8))
    left = pd.Series(0, index=media_segmentos.index, dtype=float)

    for segmento in ["Natacion", "Bicicleta", "Carrera", "Transiciones"]:
        valores = media_segmentos[segmento]
        ax.barh(
            media_segmentos.index,
            valores,
            left=left,
            color=PALETA_SEGMENTOS[segmento],
            label=segmento,
            edgecolor="white",
            linewidth=1,
        )
        for y, valor, inicio in zip(media_segmentos.index, valores, left):
            if valor >= 4:
                ax.text(
                    inicio + valor / 2,
                    y,
                    f"{valor:.1f}%",
                    ha="center",
                    va="center",
                    fontsize=9,
                    color="white",
                    fontweight="bold",
                )
        left = left + valores

    ax.set_title("Como se reparte el tiempo total en cada modalidad")
    ax.set_xlabel("% del tiempo total")
    ax.set_ylabel("")
    ax.set_xlim(0, 100)
    ax.grid(axis="x", color="#E7E2D6", linewidth=0.8)
    ax.grid(axis="y", visible=False)
    sns.despine(ax=ax, left=True)
    ax.legend(title=None, ncol=4, frameon=False, loc="lower center", bbox_to_anchor=(0.5, -0.28))
    plt.tight_layout()
    return ax, media_segmentos


def calcular_correlaciones_segmentos_por_evento(df):
    """H2: correlaciones Spearman por evento/genero y modalidad."""
    filas = []
    segmentos = {"Natacion": "segundos_natacion", "Bicicleta": "segundos_bicicleta", "Carrera": "segundos_carrera",}

    for (tipo, evento, genero), grupo in df.groupby(["tipo_distancia", "evento", "genero"]):
        if len(grupo) <= 5:
            continue

        fila = {"tipo_distancia": tipo, "evento": evento, "genero": genero}
        for nombre, columna in segmentos.items():
            fila[nombre] = grupo[columna].corr(grupo["posicion"], method="spearman")
        filas.append(fila)

    return pd.DataFrame(filas)


def grafico_correlaciones_segmentos(df):
    """H2: matriz de porcentajes entre ranking de carrera y posicion final."""
    corr_eventos = calcular_correlaciones_segmentos_por_evento(df)
    corr_media = corr_eventos.groupby("tipo_distancia")[["Natacion", "Bicicleta", "Carrera"]].mean()
    corr_media = corr_media.loc[_orden_modalidades(df)]

    rank_carrera = preparar_rank_carrera_por_modalidad(df)
    rank_carrera["grupo_posicion_final"] = pd.cut(
        rank_carrera["posicion"],
        bins=[0, 10, 20, 30, 40],
        labels=["1-10", "11-20", "21-30", "31-40"],
        include_lowest=True,
    )

    matriz = (
        rank_carrera.groupby(
            ["tipo_distancia", "grupo_rank_carrera", "grupo_posicion_final"],
            observed=False,
        )
        .size()
        .reset_index(name="n")
    )
    matriz["porcentaje"] = matriz.groupby(
        ["tipo_distancia", "grupo_rank_carrera"],
        observed=False,
    )["n"].transform(lambda serie: serie / serie.sum() * 100)

    modalidades = _orden_modalidades(rank_carrera)
    fig, axes = plt.subplots(
        1,
        len(modalidades),
        figsize=(11, 4.8),
        sharex=True,
        sharey=True,
    )
    if len(modalidades) == 1:
        axes = [axes]

    for ax, modalidad in zip(axes, modalidades):
        tabla = matriz[matriz["tipo_distancia"] == modalidad].pivot(
            index="grupo_rank_carrera",
            columns="grupo_posicion_final",
            values="porcentaje",
        )
        sns.heatmap(
            tabla,
            annot=True,
            fmt=".0f",
            cmap="Blues" if modalidad == "olimpica" else "Reds",
            cbar=False,
            linewidths=1,
            linecolor="white",
            ax=ax,
        )
        ax.set_title(modalidad)
        ax.set_xlabel("Grupo de posicion final")
        ax.set_ylabel("Grupo de ranking en carrera" if ax is axes[0] else "")
        ax.tick_params(axis="x", rotation=0)
        ax.tick_params(axis="y", rotation=0)

    fig.suptitle(
        "Donde acaban los atletas segun su ranking en carrera (%)",
        fontweight="bold",
        y=1.02,
    )
    fig.tight_layout()
    return fig, corr_media, corr_eventos


def preparar_diferencia_ganador(df):
    """H3: diferencia porcentual respecto al ganador de cada evento/genero."""
    df = df.copy()
    df["tiempo_ganador_evento"] = df.groupby(["tipo_distancia", "evento", "genero"])["segundos_total"].transform("min")
    df["diferencia_ganador_pct"] = ((df["segundos_total"] - df["tiempo_ganador_evento"])/ df["tiempo_ganador_evento"]) * 100
    return df


def grafico_variabilidad_respecto_ganador(df):
    """H3: boxplot de diferencia porcentual respecto al ganador."""
    df = preparar_diferencia_ganador(df)

    fig, ax = plt.subplots(figsize=(9, 5))
    sns.boxplot(
        data=df,
        y="tipo_distancia",
        x="diferencia_ganador_pct",
        order=_orden_modalidades(df),
        hue="tipo_distancia",
        palette=PALETA_MODALIDAD,
        width=0.55,
        showfliers=False,
        legend=False,
        ax=ax,
    )
    sns.stripplot(
        data=df,
        y="tipo_distancia",
        x="diferencia_ganador_pct",
        order=_orden_modalidades(df),
        color="#172126",
        alpha=0.18,
        size=2.5,
        jitter=0.22,
        ax=ax,
    )

    resumen = df.groupby("tipo_distancia")["diferencia_ganador_pct"].agg(["median", "std"])
    for y, modalidad in enumerate(_orden_modalidades(df)):
        mediana = resumen.loc[modalidad, "median"]
        desviacion = resumen.loc[modalidad, "std"]
        ax.text(
            mediana,
            y - 0.35,
            f"mediana {mediana:.1f}% | desv. {desviacion:.1f}",
            ha="center",
            va="bottom",
            fontsize=9,
            color="#172126",
        )

    ax.set_title("Variabilidad de tiempos: cuanto se alejan los atletas del ganador")
    ax.set_xlabel("Diferencia respecto al ganador (%)")
    ax.set_ylabel("Modalidad")
    ax.grid(axis="x", color="#E7E2D6", linewidth=0.8)
    ax.grid(axis="y", visible=False)
    sns.despine(ax=ax, left=True)
    plt.tight_layout()
    return ax, df


def calcular_diferencia_genero(df):
    """Analisis auxiliar: diferencia porcentual Female vs Male por anio."""
    df = normalizar_genero(df)
    columna_anio = "año" if "año" in df.columns else "anio"
    genero_anual = (
        df.groupby(["tipo_distancia", columna_anio, "genero"])["segundos_total"]
        .mean()
        .reset_index()
    )
    genero_pivot = genero_anual.pivot_table(
        index=["tipo_distancia", columna_anio],
        columns="genero",
        values="segundos_total",
    ).reset_index()
    genero_pivot = genero_pivot.rename(columns={columna_anio: "año"})

    genero_pivot["diferencia_genero_pct"] = (
        (genero_pivot["Female"] - genero_pivot["Male"]) / genero_pivot["Male"]
    ) * 100
    return genero_pivot


def grafico_diferencia_genero(df):
    """Analisis auxiliar: linea temporal de diferencia porcentual entre generos."""
    genero_pivot = calcular_diferencia_genero(df)
    fig, ax = plt.subplots(figsize=(9, 5))
    sns.lineplot(
        data=genero_pivot,
        x="año",
        y="diferencia_genero_pct",
        hue="tipo_distancia",
        marker="o",
        palette=PALETA_MODALIDAD,
        ax=ax,
    )
    ax.set_title("Diferencia porcentual entre mujeres y hombres")
    ax.set_xlabel("Anio")
    ax.set_ylabel("Diferencia Mujeres vs Hombres (%)")
    ax.legend(title="Modalidad", frameon=False)
    _formatear_ejes(ax)
    plt.tight_layout()
    return ax, genero_pivot


def preparar_rank_carrera_por_modalidad(df):
    """H2: ranking de carrera por modalidad, evento y genero.

    El ranking se calcula dentro de cada modalidad, evento y genero para
    comparar Ironman y Olimpica sin mezclar carreras distintas.
    """
    df = df.copy()
    df["rank_carrera_evento"] = df.groupby(["tipo_distancia", "evento", "genero"])["segundos_carrera"].rank(method="min")
    df["grupo_rank_carrera"] = pd.cut(
        df["rank_carrera_evento"],
        bins=[0, 10, 20, 30, 40],
        labels=["1-10", "11-20", "21-30", "31-40"],
        include_lowest=True,
    )
    return df


def calcular_brecha_genero_segmentos(df):
    """H4: diferencia porcentual Female vs Male por segmento y modalidad.

    Primero se calcula la mediana por modalidad, evento, anio y genero.
    Despues se compara Female frente a Male en cada evento comparable.
    """
    df = normalizar_genero(df)
    columna_anio = df.columns[1]
    segmentos = {"Natacion": "segundos_natacion","Bicicleta": "segundos_bicicleta","Carrera": "segundos_carrera",}
    filas = []

    for segmento, columna in segmentos.items():
        datos_segmento = (
            df.groupby(["tipo_distancia", columna_anio, "evento", "genero"])[columna]
            .median()
            .reset_index()
        )
        pivot = datos_segmento.pivot_table(
            index=["tipo_distancia", columna_anio, "evento"],
            columns="genero",
            values=columna,
        ).reset_index()
        pivot = pivot.dropna(subset=["Female", "Male"]).copy()
        pivot["diferencia_genero_pct"] = (
            (pivot["Female"] - pivot["Male"]) / pivot["Male"]
        ) * 100
        pivot["segmento"] = segmento
        pivot = pivot.rename(columns={columna_anio: "anio"})
        filas.append(pivot)

    return pd.concat(filas, ignore_index=True)


def grafico_brecha_genero_segmentos(df):
    """H4: brecha porcentual Mujeres-Hombres por segmento y modalidad."""
    brecha_segmentos = calcular_brecha_genero_segmentos(df)

    fig, ax = plt.subplots(figsize=(9.5, 5.2))
    sns.barplot(
        data=brecha_segmentos,
        x="segmento",
        y="diferencia_genero_pct",
        hue="tipo_distancia",
        hue_order=_orden_modalidades(brecha_segmentos),
        palette=PALETA_MODALIDAD,
        errorbar=None,
        ax=ax,
    )
    for container in ax.containers:
        ax.bar_label(container, fmt="%.1f%%", padding=3, fontsize=9)

    ax.set_title("Brecha Mujeres-Hombres por segmento")
    ax.set_xlabel("Segmento")
    ax.set_ylabel("Diferencia de tiempo Mujeres vs Hombres (%)")
    ax.legend(title="", frameon=False)
    _formatear_ejes(ax)
    plt.tight_layout()
    return ax, brecha_segmentos
