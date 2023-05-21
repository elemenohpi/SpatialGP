import json
import os
import pickle
import webbrowser

from Handlers.PlotHandler import *


class VisualizationHandler:
    def __init__(self):
        self.radius = None

    def get_files_in_path(self, path):
        file_list = []

        for root, dirs, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                file_list.append(file_path)

        return file_list

    def analyze_model(self, path_to_experiment):
        path_to_models = path_to_experiment + "Population/"
        evo_file = path_to_experiment + "evo.csv"
        output_path = path_to_experiment + "Analysis/"
        create_evo_plots(evo_file, output_path)
        files = self.get_files_in_path(path_to_models)
        # ToDo::Make dynamic
        path_to_html = "Output/Analysis/analysis.html"
        canvases = []
        all_coordinates = []
        all_execution_info = []
        all_annotations = []
        all_fitness = []
        all_individuals = []
        for file_id, path_to_model in enumerate(files):
            pickled_object = open(path_to_model, "rb")
            model_object = pickle.load(pickled_object)
            # get_execution_info should run first in case you want to tag programs with an id before proceeding. Perhaps
            # this could be moved elsewhere?
            fitness, execution_info = model_object.get_execution_info()
            program_info = model_object.get_programs_info()

            radius = float(model_object.config["init_radius"])
            self.radius = radius

            canvas = {'id': f'canvas{file_id}', 'radius': radius}

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
            all_individuals.append(model_object)

        heatmap_output_path = path_to_experiment + "Analysis/heatmap.png"

        self.generate_heatmap(all_individuals, heatmap_output_path)

        self.generate_html_file(path_to_html, canvases, all_coordinates, all_annotations, all_execution_info,
                                all_fitness)
        full_path = os.path.abspath(path_to_html)
        os.startfile(full_path)

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

    def generate_coordinate_system(self, canvas_id, radius, circle_coordinates, index, execution_info, fitness):
        execution_info_set = set(tuple(sublist) for sublist in execution_info[index])
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

    def generate_html_file(self, file_name, canvases, circle_coordinates, program_annotations, execution_info, fitness):

        html_content = self.generate_html_headers()

        for index, canvas in enumerate(canvases):
            html_content += self.generate_coordinate_system(canvas['id'], canvas['radius'], circle_coordinates[index],
                                                            index, execution_info, fitness)

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
                    tooltip.innerText = '{escaped_text}';
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
        arrow_format = "{color: '" + color + "', path: 'straight', size: 3, opacity: 0.5}"
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
                <img src='heatmap.png' style="width: 600px; height: 430px ">
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

