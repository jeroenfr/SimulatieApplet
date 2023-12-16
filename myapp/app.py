
import numpy as np
import seaborn as sns
import pandas as pd
from shiny import App, reactive, render, ui
import shinyswatch
 
choices = {"a": "Eenzijdig rechts", "b": "Eenzijdig links", "c": "Tweezijdig"}

app_ui = ui.page_fluid(
    # theme
    #shinyswatch.theme_picker_ui(),
    ui.panel_title("Hypothesetest met proporties"),
    
    
    ui.layout_sidebar(
        ui.panel_sidebar(
            ui.input_numeric("n", "Steekproefgrootte", 40),
            ui.input_slider("p_observed", "Geobserveerde steekproefproportie", value=0.5, min=0, max=1),
            ui.input_slider("p_0", "Nulhypothese : p_0 = ", value=0.5, min=0, max=1),
            ui.input_numeric("n_sim", "Aantal simulaties onder nulhypothese", 1000),
            ui.input_radio_buttons("rb1", "Type test", choices),
        ),
        ui.panel_main(
            ui.row(
                ui.column(8, ui.output_plot("histogram")),
                ui.column(4,
                     ui.output_text("txt1"),
                     ui.output_text("empirical_p"),
                ),
            ),
            
            ui.row(
                ui.column(12, ui.output_data_frame("out")),
            ),   
        ),
    ),
)


def server(input, output, session):
    shinyswatch.theme.minty()

    @reactive.Calc
    def drempelwaarde():
        return input.n()*input.p_observed()

    @output
    @render.text
    def txt1():
        return f'Drempelwaarde is "{round(drempelwaarde())}"'
        
    #dataset = pd.DataFrame({'waarden': pd.Series(dtype = 'int'), 'vlag':pd.Series(dtype = 'int')})
    #dataset = pd.DataFrame(columns = ['waarden', 'vlag'])

    @reactive.Calc
    def vlag_conditie():
        if input.rb1() == "a":
            return "x >= d"
        elif input.rb1() == "b":
            return "x <= d"
        else:
            return "x >= d" #TODO: dit moet nog aangepast worden voor tweezijdig

    @reactive.Calc    
    def dataset():
        d = drempelwaarde()
        x = np.random.binomial(input.n(), input.p_0(), input.n_sim())
        y = np.where(eval(vlag_conditie()), 1, 0)
        df = pd.DataFrame({'waarden': x, 'vlag':y})
        return df
    
    @output
    @render.data_frame
    def out():
        df = dataset()
        return render.DataTable(df, row_selection_mode='multiple')

        
    @output
    @render.plot(alt="A histogram")
    def histogram():
        df = dataset()
        plot = sns.histplot(data = df , x = 'waarden', hue='vlag', hue_order = [0,1], binwidth=1, alpha=0.5, palette=['skyblue', 'salmon'])
        plot.set(title='Steekproevenverdeling', xlabel = 'Steekproefproporties', ylabel = 'Frequentie')
        return plot

    @output
    @render.text
    def empirical_p():
        df = dataset()
        mean = round(df['vlag'].mean(), 3)
        return f'Empirische p-waarde is "{mean}"'
    
app = App(app_ui, server, debug=True)
