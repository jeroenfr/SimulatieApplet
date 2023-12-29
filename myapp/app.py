
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
                                ui.output_text("empirical_p_prop"),
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

                ui.layout_sidebar(
                    ui.panel_sidebar(
                        ui.input_numeric("n_norm", "Steekproefgrootte", 40),
                        ui.input_numeric("mu_observed_norm", "Geobserveerde steekproefgemiddelde", 0),
                        ui.input_numeric("sigma_observed_norm", "Geobserveerde standaardafwijking", 1, min=0.00001),
                        ui.input_numeric("mu_0", "Nulhypothese : mu_0 = ", 0),
                        ui.input_numeric("n_sim_norm", "Aantal simulaties onder nulhypothese", 1000),
                        ui.input_radio_buttons("rb2", "Type test", choices),
                        ),
                    ui.panel_main(
                        ui.row(
                            ui.column(8, 
                                #ui.output_plot("histogram"),
                                #ui.input_switch("x2", "Verander naar proporties")
                            ),
                            ui.column(4,
                                #ui.output_text("txt1"),
                                #ui.output_text("empirical_p_prop"),
                            ),
                        ),
            
                        ui.row(
                            ui.column(12, ui.output_data_frame("out_norm")),
                        ),   
                    ),
                ),
            ),
    ),
    # theme
    #shinyswatch.theme_picker_ui(),
   
)


def server(input, output, session):
    shinyswatch.theme.minty()

    @reactive.Calc
    def drempelwaarde_prop():
        """
        Geeft de drempelwaarde terug afhankelijk van de gekozen radio button. De drempelwaarde is het aantal successen in de steekproef even extreem 
        of extremer dan de geobserveerde steekproefproportie. De drempelwaarde is afhankelijk van de gekozen radio button. 
        Bij een eenzijdige test is de drempelwaarde de geobserveerde steekproefproportie. Bij een tweezijdige test zijn er twee drempelwaarden: één gelijk aan de geobserveerde
        steekproefproportie en één  symmetrisch t.o.v. de proportie onder de nulhypothese. Deze wordt berekend mbv 'distance' in de functie.

       """
        distance = abs(input.p_0() - input.p_observed())
        if input.rb1() == 'a' :
            return [input.n()*input.p_observed()]
        elif input.rb1() == 'b':
            return [input.n()*input.p_observed()]
        elif input.rb1() == "c":
            return [input.n()*(input.p_0() - distance), input.n()*(input.p_0() + distance)]

    @reactive.Calc
    def drempelwaarde_norm():
        """
        Geeft de drempelwaarde terug afhankelijk van de gekozen radio button. De drempelwaarde is het aantal successen in de steekproef even extreem 
        of extremer dan de geobserveerde steekproefproportie. De drempelwaarde is afhankelijk van de gekozen radio button. 
        Bij een eenzijdige test is de drempelwaarde de geobserveerde steekproefproportie. Bij een tweezijdige test zijn er twee drempelwaarden: één gelijk aan de geobserveerde
        steekproefproportie en één  symmetrisch t.o.v. de proportie onder de nulhypothese. Deze wordt berekend mbv 'distance' in de functie.

       """
        distance = abs(input.mu_0() - input.mu_observed_norm())
        if input.rb2() == 'a' :
            return [input.mu_observed_norm()]
        elif input.rb2() == 'b':
            return [input.mu_observed_norm()]
        elif input.rb2() == "c":
            return [input.mu_0() - distance, input.mu_0() + distance]


    @output
    @render.text
    def txt1():
        if len(drempelwaarde_prop()) == 2:
            return f'Drempelwaarden zijn {np.round(drempelwaarde_prop()[0])} en {np.round(drempelwaarde_prop()[1])}'
        else:
            return f'Drempelwaarde is {np.round(drempelwaarde_prop()[0])}'
        
    
    @reactive.Calc
    def vlag_proportie():
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
            return "(x <= d[0]) | (x >= d[1])" 
        
    @reactive.Calc
    def vlag_norm():
        """
        Returns the condition based on the selected radio button. d is treshold value in dataset and differs for 
        left, right and two sided test. Two sided test has two thresholds.

        If the radio button 'a' is selected, the condition is 'x >= d'.
        If the radio button 'b' is selected, the condition is 'x <= d'.
        If button c is selected, the condition is 'x <= d[0]) | (x >= d[1]' where first is lower treshold and second is upper treshold.

        Returns:
            str: The condition based on the selected radio button.
        """
        if input.rb2() == "a":
            return "x >= d[0]"
        elif input.rb2() == "b":
            return "x <= d[0]"
        else:
            return "(x <= d[0]) | (x >= d[1])" 

    @reactive.Calc    
    def dataset_proportie():
        d = drempelwaarde_prop()
        x = np.random.binomial(input.n(), input.p_0(), input.n_sim())
        y = np.where(eval(vlag_proportie()), 1, 0)
        z = x/input.n()
        df = pd.DataFrame({'waarden': x, 'proporties' : z, 'vlag':y})
        return df
    
    @reactive.Calc    
    def dataset_norm():
        d = drempelwaarde_norm()
        se = input.sigma_observed_norm()/np.sqrt(input.n_norm())
        x = np.random.normal(input.mu_0(), se, input.n_sim_norm())
        y = np.where(eval(vlag_norm()), 1, 0)
        df = pd.DataFrame({'Steekproefgemiddelden': x,  'vlag':y})
        return df

    
    @output
    @render.data_frame
    def out():
        df = dataset_proportie()
        return render.DataTable(df, row_selection_mode='multiple')

    @output
    @render.data_frame
    def out_norm():
        df = dataset_norm()
        return render.DataTable(df, row_selection_mode='multiple')

    @output
    @render.plot(alt="A histogram")
    def histogram():
        df = dataset_proportie()
        if input.x2():
            plot = sns.histplot(data = df , x = 'proporties',bins='scott', alpha=1, hue='vlag', hue_order = [0,1], palette=['skyblue', 'salmon'])
            plot.set(title='Steekproevenverdeling', xlabel = 'Steekproefproporties', ylabel = 'Frequentie')
        else:
            plot = sns.histplot(data = df , x = 'waarden', hue='vlag', hue_order = [0,1], discrete=True, palette=['skyblue', 'salmon'])
            plot.set(title='Steekproevenverdeling', xlabel = 'Aantal successen in steekproef', ylabel = 'Frequentie')
        return plot

    @output
    @render.text
    def empirical_p_prop_prop():
        df = dataset_proportie()
        mean = round(df['vlag'].mean(), 3)
        return f'Empirische p-waarde is "{mean}"'
    
app = App(app_ui, server, debug=True)
