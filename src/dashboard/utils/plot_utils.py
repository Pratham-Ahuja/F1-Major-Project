import plotly.graph_objects as go


# =========================================================
# PLOT UTILS — Common Plotly Helpers for Dashboard
# =========================================================


# ---------------------------------------------------------
# BASE LAYOUT
# ---------------------------------------------------------

def base_layout(
    title: str = "",
    x_title: str = "",
    y_title: str = "",
    height: int = 400
) -> dict:
    """
    Standard layout configuration for all plots.
    """

    return dict(
        title=title,
        xaxis=dict(title=x_title),
        yaxis=dict(title=y_title),
        height=height,
        margin=dict(l=40, r=40, t=60, b=40),
        template="plotly_white",
        hovermode="x unified"
    )


# ---------------------------------------------------------
# VERTICAL MARKER
# ---------------------------------------------------------

def add_vertical_marker(
    fig: go.Figure,
    x_value: float,
    label: str,
    color: str = "red",
    dash: str = "dash"
):
    """
    Add a vertical reference line to a plot.
    """

    fig.add_vline(
        x=x_value,
        line_dash=dash,
        line_color=color,
        annotation_text=label,
        annotation_position="top"
    )


# ---------------------------------------------------------
# HORIZONTAL MARKER
# ---------------------------------------------------------

def add_horizontal_marker(
    fig: go.Figure,
    y_value: float,
    label: str,
    color: str = "gray",
    dash: str = "dot"
):
    """
    Add horizontal reference line.
    Useful for thresholds or limits.
    """

    fig.add_hline(
        y=y_value,
        line_dash=dash,
        line_color=color,
        annotation_text=label,
        annotation_position="right"
    )


# ---------------------------------------------------------
# SIMPLE LINE PLOT
# ---------------------------------------------------------

def simple_line_plot(
    x,
    y,
    title: str,
    x_label: str,
    y_label: str,
    color: str = "#1f77b4"
) -> go.Figure:
    """
    Create a simple line plot with standard styling.
    """

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=x,
            y=y,
            mode="lines+markers",
            line=dict(color=color, width=3),
            marker=dict(size=6)
        )
    )

    fig.update_layout(
        **base_layout(
            title=title,
            x_title=x_label,
            y_title=y_label
        )
    )

    return fig


# ---------------------------------------------------------
# MULTI LINE PLOT
# ---------------------------------------------------------

def multi_line_plot(
    x,
    series: dict,
    title: str,
    x_label: str,
    y_label: str
) -> go.Figure:
    """
    Plot multiple lines on same figure.

    Example:
    series = {
        "Driver A": values_a,
        "Driver B": values_b
    }
    """

    fig = go.Figure()

    for label, values in series.items():

        fig.add_trace(
            go.Scatter(
                x=x,
                y=values,
                mode="lines+markers",
                name=label
            )
        )

    fig.update_layout(
        **base_layout(
            title=title,
            x_title=x_label,
            y_title=y_label
        )
    )

    return fig


# ---------------------------------------------------------
# BAR CHART
# ---------------------------------------------------------

def bar_chart(
    categories,
    values,
    title: str,
    x_label: str,
    y_label: str,
    color: str = "#3498db"
) -> go.Figure:
    """
    Create standard bar chart.
    """

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=categories,
            y=values,
            marker_color=color
        )
    )

    fig.update_layout(
        **base_layout(
            title=title,
            x_title=x_label,
            y_title=y_label
        )
    )

    return fig


# ---------------------------------------------------------
# HISTOGRAM
# ---------------------------------------------------------

def histogram_plot(
    values,
    title: str,
    x_label: str,
    bins: int = 30,
    color: str = "#1f77b4"
) -> go.Figure:
    """
    Create histogram with standard styling.
    """

    fig = go.Figure()

    fig.add_trace(
        go.Histogram(
            x=values,
            nbinsx=bins,
            marker_color=color,
            opacity=0.75
        )
    )

    fig.update_layout(
        **base_layout(
            title=title,
            x_title=x_label,
            y_title="Frequency"
        )
    )

    return fig


# ---------------------------------------------------------
# TIMELINE EVENT PLOT
# ---------------------------------------------------------

def timeline_events(
    laps,
    labels,
    title: str = "Strategy Events"
) -> go.Figure:
    """
    Plot timeline events (pit stops etc).
    """

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=laps,
            y=["Event"] * len(laps),
            mode="markers+text",
            text=labels,
            textposition="top center",
            marker=dict(size=12, color="#e67e22")
        )
    )

    fig.update_layout(
        title=title,
        yaxis=dict(showticklabels=False),
        xaxis=dict(title="Lap"),
        height=300
    )

    return fig