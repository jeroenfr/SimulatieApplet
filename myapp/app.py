
import numpy as np
import seaborn as sns
import pandas as pd
from shiny import App, reactive, render, ui
import shinyswatch
 
choices = {"a": "Eenzijdig rechts", "b": "Eenzijdig links", "c": "Tweezijdig"}

app_ui = ui.page_fluid(

    ui.navset_tab_card(

        ui.nav("Hypothesetest met proporties",
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
                            ui.column(8, 
                                ui.output_plot("histogram"),
                                ui.input_switch("x2", "Verander naar proporties")
                            ),
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
            ),
        ui.nav("Hypothesetest met gemiddeldes",
               ui.panel_title("Hypothesetest met gemiddeldes"),

               ),
    ),
    # theme
    #shinyswatch.theme_picker_ui(),
   
)


def server(input, output, session):
    shinyswatch.theme.minty()

    @reactive.Calc
    def drempelwaarde():
        distance = abs(input.p_0() - input.p_observed())
        if input.rb1() == 'a' :
            return [input.n()*input.p_observed()]
        elif input.rb1() == 'b':
            return [input.n()*input.p_observed()]
        elif input.rb1() == "c":
            return [input.n()*(input.p_0() - distance), input.n()*(input.p_0() + distance)]


    @output
    @render.text
    def txt1():
        if len(drempelwaarde()) == 2:
            return f'Drempelwaarden zijn {np.round(drempelwaarde()[0])} en {np.round(drempelwaarde()[1])}'
        else:
            return f'Drempelwaarde is {np.round(drempelwaarde()[0])}'
        
    
    @reactive.Calc
    def vlag_conditie():
        """
        Returns the condition based on the selected radio button. d is treshold value in dataset and differs for 
        left, right and two sided test. Two sided test has two thresholds.

        If the radio button 'a' is selected, the condition is 'x >= d'.
        If the radio button 'b' is selected, the condition is 'x <= d'.
        If button c is selected, the condition is 'x <= d[0]) | (x >= d[1]' where first is lower treshold and second is upper treshold.

        Returns:
            str: The condition based on the selected radio button.
        """
        if input.rb1() == "a":
            return "x >= d[0]"
        elif input.rb1() == "b":
            return "x <= d[0]"
        else:
            return "(x <= d[0]) | (x >= d[1])" #TODO: dit moet nog aangepast worden voor tweezijdig

    @reactive.Calc    
    def dataset():
        d = drempelwaarde()
        x = np.random.binomial(input.n(), input.p_0(), input.n_sim())
        y = np.where(eval(vlag_conditie()), 1, 0)
        z = x/input.n()
        df = pd.DataFrame({'waarden': x, 'proporties' : z, 'vlag':y})
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
        if input.x2():
            plot = sns.histplot(data = df , x = 'proporties',bins='scott', alpha=1, hue='vlag', hue_order = [0,1], palette=['skyblue', 'salmon'])
            plot.set(title='Steekproevenverdeling', xlabel = 'Steekproefproporties', ylabel = 'Frequentie')
        else:
            plot = sns.histplot(data = df , x = 'waarden', hue='vlag', hue_order = [0,1], discrete=True, palette=['skyblue', 'salmon'])
            plot.set(title='Steekproevenverdeling', xlabel = 'Aantal successen in steekproef', ylabel = 'Frequentie')
        return plot

    @output
    @render.text
    def empirical_p():
        df = dataset()
        mean = round(df['vlag'].mean(), 3)
        return f'Empirische p-waarde is "{mean}"'
    
app = App(app_ui, server, debug=True)
