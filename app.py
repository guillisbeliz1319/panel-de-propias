import faicons as fa
import plotly.express as px



from shared import app_dir, tips
from shiny import reactive, render
from shiny.express import input, ui
from shinywidgets import render_plotly


bill_rng = (min(tips.total_bill), max(tips.total_bill))


ui.page_opts(title='Propias Restaurante', fillable=True)

with ui.sidebar(open="desktop"):
    ui.input_slider(
        'total_bill',                
        'Bill amount',               
        min=bill_rng[0],             
        max=bill_rng[1],             
        value=bill_rng,              
        post='€',                    

    )
    ui.input_checkbox_group(
        'day',                      
        'Días de la semana',             
       ['Thur', 'Fri', 'Sat', 'Sun'],         
        selected=['Thur'], 
        inline=True,                 
    )

    ui.input_action_button('reset', 'Reset filter') 

ICONS = {
    "user": fa.icon_svg("user", "regular"),
    "wallet": fa.icon_svg("wallet"),
    "currency-euro": fa.icon_svg("euro-sign"),
    "ellipsis": fa.icon_svg("ellipsis"),
}

with ui.layout_columns(fill=False):
    # Primera caja de valor: Total de propinas
    with ui.value_box(showcase=ICONS["user"]):
        "Total tippers"

        @render.express
        def total_tippers():
            tips_data().shape[0]  # Contar filas en los datos filtrados

with ui.value_box(showcase=ICONS["wallet"]):
        "Average tip"

        @render.express
        def average_tip():
            d = tips_data()
            if d.shape[0] > 0:
                perc = d.tip / d.total_bill  # Calcular porcentaje de propina
                f"{perc.mean():.1%}"    

with ui.value_box(showcase=ICONS["currency-euro"]):
        "Average bill"

        @render.express
        def average_bill():
            d = tips_data()
            if d.shape[0] > 0:
                bill = d.total_bill.mean()  # Calcular factura promedio
                f"€{bill:.2f}"    

ui.include_css(app_dir / "styles.css")  

@reactive.calc
def tips_data():
    bill = input.total_bill()  # Obtener rango de facturas seleccionado
    idx1 = tips.total_bill.between(bill[0], bill[1])  # Filtrar por factura
    idx2 = tips.day.isin(input.day())  # Filtrar por momento
    return tips[idx1 & idx2]  

@reactive.effect
@reactive.event(input.reset)  # Activar cuando se haga clic en "reset"
def _():
    ui.update_slider("total_bill", value=bill_rng)  # Restablecer control deslizante
    ui.update_checkbox_group("day", selected=["Thur"])  

with ui.layout_columns(col_widths=[6, 6, 12]):
    # Primera tarjeta: Tabla de datos
    with ui.card(full_screen=True):
        ui.card_header("Tips data")

        @render.data_frame
        def table():
            return render.DataGrid(tips_data())
with ui.card(full_screen=True):
        with ui.card_header(class_='d-flex justify-content-between align-items-center'):
            'Porcentaje de propinas'
            # Menú emergente para opciones de color
            with ui.popover(title='añade un color variable', placement='top'):
                ICONS['ellipsis']
                ui.input_radio_buttons(
                    'tip_perc_yl',
                    'Split by:',
                    ['sex', 'smoker', 'day', 'time'],
                    inline=True,
                )

        # Renderizar el gráfico de dispersión
        @render_plotly
        def scatterplot():
            color = input.scatter_color()
            return px.scatter(
                tips_data(),
                x="total_bill",
                y="tip",
                color=None if color == "none" else color,
                trendline="lowess",  # Añadir línea de tendencia
            )
with ui.card(full_screen=True):
        with ui.card_header(class_="d-flex justify-content-between align-items-center"):
            "Tip percentages"
            # Menú emergente para opciones de división
            with ui.popover(title="Add a color variable"):
                ICONS["ellipsis"]
                ui.input_radio_buttons(
                    "tip_perc_y",
                    "Split by:",
                    ["sex", "smoker", "day", "time"],
                    selected="day",  # Valor predeterminado
                    
                )

        # Renderizar el gráfico de densidad
        @render_plotly
        def tip_perc():
            from ridgeplot import ridgeplot  # Importamos la función ridgeplot

            # Preparar datos
            dat = tips_data()
            dat["percent"] = dat.tip / dat.total_bill  # Calcular porcentaje de propina
            yvar = input.tip_perc_y()  # Variable para dividir
            uvals = dat[yvar].unique()  # Valores únicos de esa variable

            # Crear muestras para cada valor único
            samples = [[dat.percent[dat[yvar] == val]] for val in uvals]

            # Crear el gráfico ridgeplot
            plt = ridgeplot(
                samples=samples,
                labels=uvals,
                bandwidth=0.01,
                colorscale="viridis",
                colormode="row-index",
            )

            # Ajustar la leyenda
            plt.update_layout(
                legend=dict(
                    orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5
                )
            )

            return plt
        
      