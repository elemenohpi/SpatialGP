import json
import os
import pickle
import subprocess
import sys
import webbrowser

from Handlers.PlotHandler import *


class VisualizationHandler:
    def __init__(self):
        self.heatmap_output_path = None
        self.radius = None

    def get_files_in_path(self, path):
        file_list = []

        for root, dirs, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                file_list.append(file_path)

        return file_list

    def analyze_model(self, path_to_experiment):
        path_to_pop = path_to_experiment + "Population/pop.sgp"
        evo_file = path_to_experiment + "evo.csv"
        output_path = path_to_experiment + "Analysis/"
        try:
            create_evo_plots(evo_file, output_path)
        except FileNotFoundError:
            evo_file = path_to_experiment + "Evo/evo_0.csv"
            create_evo_plots(evo_file, output_path)
        # ToDo::Make dynamic
        path_to_html = "Output/Analysis/analysis.html"
        canvases = []
        all_coordinates = []
        all_execution_info = []
        all_annotations = []
        all_fitness = []
        all_individuals = []
        all_exe_p_count = []
        all_exe_s_count = []
        print(path_to_pop)
        try:
            pickled_object = open(path_to_pop, "rb")
        except FileNotFoundError:
            exp_num = input("Experiment detected, enter experiment number: ")
            path_to_pop = path_to_pop[:-7] + "P" + exp_num + "/" + "pop.sgp"
            pickled_object = open(path_to_pop, "rb")

        pop_object = pickle.load(pickled_object)
        for index, individual in enumerate(pop_object.pop):
            # get_execution_info should run first in case you want to tag programs with an id before proceeding. Perhaps
            # this could be moved elsewhere?
            if not hasattr(individual, "executed_programs"):
                individual.executed_programs = []
            fitness, execution_info, additional_info = individual.get_execution_info()
            fitness = round(fitness, 10)

            program_info = individual.get_programs_info()

            radius = float(individual.config["init_radius"])
            self.radius = radius

            canvas = {'id': f'canvas{index}', 'radius': radius}

            coordinates = []
            annotations = []
            for info in program_info:
                coordinates.append(info[1])
                annotations.append(info[2])

            canvases.append(canvas)
            all_coordinates.append(coordinates)
            all_execution_info.append(execution_info)
            all_annotations.append(annotations)
            all_fitness.append(fitness)
            all_individuals.append(individual)
            all_exe_p_count.append(additional_info["exe_p_count"])
            all_exe_s_count.append(additional_info["exe_s_count"])

        heatmap_output_path = path_to_experiment + "Analysis/heatmap.png"
        self.heatmap_output_path = heatmap_output_path

        self.generate_heatmap(all_individuals, heatmap_output_path)

        self.generate_html_file(path_to_html, canvases, all_coordinates, all_annotations, all_execution_info,
                                all_fitness, all_exe_p_count, all_exe_s_count)
        full_path = os.path.abspath(path_to_html)
        try:
            os.startfile(full_path)
        except AttributeError:
            opener = "open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, full_path])

    def generate_html_headers(self):
        return '''
        <html>
        <head>
            <style>
                .individual_container {
                    display: flex;
                    flex-wrap: wrap;
                }
                .canvas {
                    position: relative;
                    width: 400px;
                    height: 400px;
                    float: left;
                    border: 1px solid #000;
                }
                .axis {
                    position: absolute;
                    border: 1px solid #000;
                }
                .circle {
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    border: 1px solid #000;
                    border-radius: 50%;
                }
                
                .tooltip {
                    position: absolute;
                    width: 200px;
                    top: -20px;
                    left: 20;
                    background-color: #fff;
                    color: #000;
                    padding: 5px;
                    border-style: solid;
                    border-color: black;
                    border-width: thin;
                    z-index: 100;
                    
                    /* Custom tooltip styles */
                    font-size: 12px;
                    font-weight: 700;
                    border-radius: 3px;
                }
            </style>
            <script src="../../Handlers/leader-line.min.js"></script>
        </head>
        <body>
        '''

    def generate_html_footer(self, program_annotations):
        return_text = ""

        for indv_index, model_annotation in enumerate(program_annotations):
            for index, program_annotations in enumerate(model_annotation):
                return_text += self.generate_tooltip_html(program_annotations, f"indv_{indv_index}_p_{index}")

        return_text += '''
        </body>
        </html>
        '''
        return return_text

    def generate_coordinate_system(self, canvas_id, radius, circle_coordinates, index, execution_info, fitness, all_p,
                                   all_s):
        execution_info_set = set(tuple(sublist) for sublist in execution_info[index])
        loop_text = self.extract_loop_info(execution_info[index])
        number_of_programs = len(circle_coordinates)
        number_of_executions = len(execution_info[index])
        unique_execution_flows = len(execution_info_set)
        return f'''
        <div class="individual_container">
            <div id="{canvas_id}" class="canvas">
                <b>Individual {index}</b>
                {self.generate_x_axis(canvas_id)}
                {self.generate_y_axis(canvas_id)}
                {self.generate_source_circle(canvas_id, index)}
                {self.generate_circle(canvas_id, radius)}
                {self.generate_coordinate_circles(canvas_id, circle_coordinates, index)}
                {self.generate_arrow_html(canvas_id, circle_coordinates, execution_info_set, index)}
            </div>
            <p style="padding: 10px">
                Fitness: {fitness[index]}
                <br>
                Number of Programs: {number_of_programs}
                <br>
                Number of Evaluations: {number_of_executions}
                <br>
                Number of Unique Execution Orders: {unique_execution_flows}
                <br>
                Number of Executed Programs: {all_p[index]}
                <br>
                <br>
                Number of Executed Programs on Average: {all_p[index]/len(execution_info[index])}
                <br>
                Number of Executed Statements: {all_s[index]}
                <br>
                {loop_text}
            </p>
            
            {self.generate_evo_plot_html(index)}
            {self.generate_heatmap_plot_html(index)}
            
        </div>
        <br>
        '''

    def generate_source_circle(self, canvas_id, indv_index):
        circle = ''
        x, y = 0, 0
        circle_style = f'width: 10px; cursor: pointer; height: 10px; margin-top: -5px; margin-left: -5px;' \
                       f' background-color: orange; visibility: hidden; top: calc(50% - {y}px); left: calc(50% + {x}px); '
        circle += f'<div class="circle" id="indv_{indv_index}_p_source" style="{circle_style}" data-canvas="{canvas_id}">' \
                   f'</div> '

        return circle

    def generate_coordinate_circles(self, canvas_id, coordinates, indv_index):
        circles = ''
        for index, coord in enumerate(coordinates):
            x, y = coord
            circle_style = f'width: 10px; cursor: pointer; height: 10px; margin-top: -5px; margin-left: -5px;' \
                           f' background-color: orange; top: calc(50% - {y}px); left: calc(50% + {x}px); '
            circles += f'<div class="circle" id="indv_{indv_index}_p_{index}" style="{circle_style}" data-canvas="{canvas_id}">' \
                       f'</div> '

        return circles

    def generate_x_axis(self, canvas_id):
        return f'<div class="axis" style="width: 100%; top: 50%; left: 0;" data-canvas="{canvas_id}"></div>'

    def generate_y_axis(self, canvas_id):
        return f'<div class="axis" style="height: 100%; top: 0; left: 50%;" data-canvas="{canvas_id}"></div>'

    def generate_circle(self, canvas_id, r):
        circle_style = f'width: {2 * r}px; height: {2 * r}px; margin-top: -{r}px; margin-left: -{r}px;'
        return f'<div class="circle" style="{circle_style}" data-canvas="{canvas_id}"></div>'

    def generate_html_file(self, file_name, canvases, circle_coordinates, program_annotations, execution_info, fitness,
                           all_p_count, all_s_count):

        html_content = self.generate_html_headers()

        for index, canvas in enumerate(canvases):
            html_content += self.generate_coordinate_system(canvas['id'], canvas['radius'], circle_coordinates[index],
                                                            index, execution_info, fitness, all_p_count, all_s_count)

        html_content += self.generate_html_footer(program_annotations)

        with open(file_name, 'w') as file:
            file.write(html_content)

    def generate_tooltip_html(self, text, element_id):
        text = f"{element_id} code:\n\n{text}"
        escaped_text = json.dumps(text)[1:-1]

        return f'''
        <script>
            window.addEventListener('DOMContentLoaded', () => {{
                const element = document.getElementById('{element_id}');
                element.addEventListener('mouseover', () => {{
                    const tooltip = document.createElement('div');
                    tooltip.innerText = "{escaped_text}";
                    tooltip.classList.add('tooltip');
                    element.appendChild(tooltip);
                }});
                element.addEventListener('mouseout', () => {{
                    const tooltip = element.querySelector('.tooltip');
                    tooltip.remove();
                }});
            }});
        </script>
        '''

    def generate_arrow_html(self, canvas_id, coordinates, execution_info, indv_id):
        html = ""

        colors = ["#FF000066", "#61FF0066", "#00B6FF66", "#7800FF66", "#FFFF0D66", "#00000066"]
        for index, info in enumerate(execution_info):
            if index >= len(colors) - 1:
                line_color = "#000000"
            else:
                line_color = colors[index]

            start_element = f"indv_{indv_id}_p_source"

            for arrow in info:
                destination_element = f"indv_{indv_id}_p_{arrow}"

                html += self.add_arrows_html(start_element, destination_element, line_color)

                start_element = destination_element

        return html

    def add_arrows_html(self, id1, id2, color):
        element_one = f'''document.getElementById('{id1}')'''
        element_two = f'''document.getElementById('{id2}')'''
        arrow_format = "{color: '" + color + "', exp_path: 'straight', size: 3, opacity: 0.5}"
        arrow_html = f'''
            <script>
                new LeaderLine({element_one},{element_two},{arrow_format} 
                );
            </script>
            '''
        return arrow_html

    def generate_evo_plot_html(self, index):
        html = ''''''
        if index == 0:
            html = f'''
                <img src='best_plot.png' style="width: 600px; height: 430px ">
                </img>
            '''
        if index == 1:
            html = f'''
                <img src='avg_plot.png' style="width: 600px; height: 430px ">
                </img>
            '''
            return html
        return html

    def generate_heatmap_plot_html(self, index):
        if index == 2:
            html = f'''
                <img src='../../{self.heatmap_output_path}' style="width: 600px; height: 600px ">
                </img>
            '''
            return html
        return ''''''

    def generate_heatmap(self, all_individuals, output_path):
        radius = float(all_individuals[0].config["init_radius"])
        coordinates = []
        for individual in all_individuals:
            for program in individual.programs:
                coordinates.append(program.pos)

        create_heatmap(coordinates, output_path, radius)

    def extract_loop_info(self, execution_info):
        looped_evaluation_count = 0
        frequency = {}
        average_frequency = {}
        notable_looped_programs = []
        for order in execution_info:
            if len(set(order)) != len(order):
                looped_evaluation_count += 1
            for element in set(order):
                count = order.count(element)
                if element not in frequency.keys():
                    frequency[element] = 0
                frequency[element] += count

        for key, value in frequency.items():
            average_frequency[key] = value / len(execution_info)

        values = sorted(average_frequency.values(), reverse=True)
        loop_count = [count for count in values if count > 1]
        loop_count = sum(loop_count)

        sorted_average_frequencies = sorted(average_frequency.items(), key=lambda x: x[1], reverse=True)
        if looped_evaluation_count > 0:
            if len(sorted_average_frequencies) > 3:
                notable_looped_programs = sorted_average_frequencies[0:3]
            else:
                notable_looped_programs = sorted_average_frequencies

        length = len(notable_looped_programs)
        index = 0
        while index < length:
            if notable_looped_programs[index][1] == 1:
                del(notable_looped_programs[index])
                length -= 1
            index += 1

        notable_text = ""
        for program, count in notable_looped_programs:
            notable_text += f"P{program}: {count}, "
        notable_text = notable_text[:-2]

        loop_text = ""
        if looped_evaluation_count == 0:
            loop_text += "Loop: None <br>"
        elif looped_evaluation_count == len(execution_info):
            loop_text += f"Loop: Always<br>" \
                         f"Average Looped Evaluations: {looped_evaluation_count / len(execution_info)}<br>" \
                         f"Average Loop Count: {loop_count}<br>" \
                         f"Notable Looped Programs: {notable_text}<br>"
        else:
            loop_text += f"Loop: Sometimes <br>Average Looped Evaluations" \
                         f": {looped_evaluation_count / len(execution_info)}<br>Notable Looped "\
                         f"Programs: {notable_text}<br>"
        return loop_text

