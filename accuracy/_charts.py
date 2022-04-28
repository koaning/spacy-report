import numpy as np
import pandas as pd
import altair as alt
from clumper import Clumper
from sklearn.metrics import precision_score, recall_score, accuracy_score


def create_density_chart(dataf):
    """Creates a density chart."""
    return (
        alt.Chart(dataf)
        .transform_density(
            "score", as_=["score", "density"], groupby=["group"], bandwidth=0.05
        )
        .mark_area(opacity=0.7)
        .encode(
            x="score:Q",
            y="density:Q",
            color="group:N",
            tooltip=["score:Q", "density:Q", "group:N"],
        )
        .properties(title="Density of Examples")
    )


def create_line_chart(dataf, x_col, y_col, group_col):
    """Based on https://altair-viz.github.io/gallery/multiline_tooltip.html"""
    # Create a selection that chooses the nearest point & selects based on x-value
    nearest = alt.selection(
        type="single", nearest=True, on="mouseover", fields=[x_col], empty="none"
    )

    # The basic line
    line = (
        alt.Chart(dataf)
        .mark_line(interpolate="basis")
        .encode(x=f"{x_col}:Q", y=f"{y_col}:Q", color=f"{group_col}:N")
    )

    # Transparent selectors across the chart. This is what tells us
    # the x-value of the cursor
    selectors = (
        alt.Chart(dataf)
        .mark_point()
        .encode(
            x=f"{x_col}:Q",
            opacity=alt.value(0),
        )
        .add_selection(nearest)
    )

    # Draw points on the line, and highlight based on selection
    points = line.mark_point().encode(
        opacity=alt.condition(nearest, alt.value(1), alt.value(0))
    )

    # Draw text labels near the points, and highlight based on selection
    text = line.mark_text(align="left", dx=5, dy=-5).encode(
        text=alt.condition(nearest, f"{y_col}:Q", alt.value(" "))
    )

    # Draw a rule at the location of the selection
    rules = (
        alt.Chart(dataf)
        .mark_rule(color="gray")
        .encode(
            x=f"{x_col}:Q",
        )
        .transform_filter(nearest)
    )

    # Put the five layers into a chart and bind the data
    return alt.layer(line, selectors, points, rules, text).properties(
        title="Threshold Effect"
    )


def make_plots(orig_data, pred_data, tag):
    """Creates a 2x2 grid of charts for debugging."""
    orig_dictlist = [{"text": _.text, "labels": _.cats} for _ in orig_data]
    combined = [{**clump, "pred": d.cats} for clump, d in zip(orig_dictlist, pred_data)]

    conf_data = (
        Clumper(combined)
        .mutate(
            confidence=lambda d: d["pred"][tag], hit=lambda d: d["labels"][tag] == 1.0
        )
        .collect()
    )

    # Prepare the density chart
    x_hit = np.array([d["confidence"] for d in conf_data if d["hit"]])
    x_miss = np.array([d["confidence"] for d in conf_data if not d["hit"]])

    df_density = pd.concat(
        [
            pd.DataFrame({"score": x_hit}).assign(group=lambda d: tag),
            pd.DataFrame({"score": x_miss}).assign(group=lambda d: f"not-{tag}"),
        ]
    )

    p_density = create_density_chart(df_density)

    # Prepare the scores chart
    xs = np.linspace(0.01, 0.95, 100)
    precisions = np.zeros(xs.shape)
    recalls = np.zeros(xs.shape)
    accuracies = np.zeros(xs.shape)

    y_true = np.array([d["hit"] for d in conf_data])
    confs = np.array([d["confidence"] for d in conf_data])

    for i, x in enumerate(xs):
        y_pred = confs > x
        precisions[i] = precision_score(y_true, y_pred, zero_division=0)
        recalls[i] = recall_score(y_true, y_pred, zero_division=0)
        accuracies[i] = accuracy_score(y_true, y_pred)

    precisions = np.round(precisions, 4)
    recalls = np.round(recalls, 4)
    accuracies = np.round(accuracies, 4)

    df_scores = pd.concat(
        [
            pd.DataFrame(
                {
                    "threshold": xs,
                    "score": precisions,
                    "group": ["precision" for _ in xs],
                }
            ),
            pd.DataFrame(
                {"threshold": xs, "score": recalls, "group": ["recall" for _ in xs]}
            ),
            pd.DataFrame(
                {
                    "threshold": xs,
                    "score": accuracies,
                    "group": ["accuracy" for _ in xs],
                }
            ),
        ]
    )

    p_scores = create_line_chart(
        df_scores, x_col="threshold", y_col="score", group_col="group"
    )
    return p_density, p_scores
