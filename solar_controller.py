import tkinter
from tkinter.filedialog import *
from solar_model import SolarSystemModel, gravitational_constant
from solar_objects import Star, Planet, Satellite
from solar_view import SolarSystemView, window_width, window_height
import math
import random


class SolarSystemController:
    def __init__(self, root):
        self.root = root
        self.model = SolarSystemModel()
        self.view = SolarSystemView(root, self.model)

        self.perform_execution = False
        self.time_step = tkinter.DoubleVar()
        self.time_step.set(1000000)
        self.displayed_time = tkinter.StringVar()
        self.displayed_time.set("0.0 seconds gone")

        self.create_ui()

    def create_ui(self):
        frame = tkinter.Frame(self.root)
        frame.pack(side=tkinter.BOTTOM)

        self.start_button = tkinter.Button(frame, text="Start", command=self.start_execution, width=6)
        self.start_button.pack(side=tkinter.LEFT)

        time_step_entry = tkinter.Entry(frame, textvariable=self.time_step)
        time_step_entry.pack(side=tkinter.LEFT)

        time_speed = tkinter.DoubleVar()
        scale = tkinter.Scale(frame, variable=time_speed, orient=tkinter.HORIZONTAL)
        scale.pack(side=tkinter.LEFT)

        load_button = tkinter.Button(frame, text="Open File", command=self.open_file_dialog)
        load_button.pack(side=tkinter.LEFT)

        generate_button = tkinter.Button(frame, text="Generate System", command=self.generate_system_dialog)
        generate_button.pack(side=tkinter.LEFT)

        save_button = tkinter.Button(frame, text="Save to file", command=self.save_file_dialog)
        save_button.pack(side=tkinter.LEFT)

        orbit_button = tkinter.Button(frame, text="Toggle Orbits", command=self.toggle_orbits)
        orbit_button.pack(side=tkinter.LEFT)

        time_label = tkinter.Label(frame, textvariable=self.displayed_time, width=30)
        time_label.pack(side=tkinter.RIGHT)

    def execution(self):
        if not self.perform_execution:
            return

        self.view.space.delete("all")
        self.model.recalculate_positions(self.time_step.get())

        for body in self.model.space_objects:
            if body.type == 'star':
                self.view.create_star_image(body)
            else:
                self.view.create_planet_image(body)

        if self.view.show_orbits:
            self.view.draw_orbits()

        self.displayed_time.set(f"{self.model.physical_time:.1f} seconds gone")
        self.view.space.update_idletasks()
        self.view.space.update()
        self.view.space.after(50, self.execution)

    def start_execution(self):
        self.perform_execution = True
        self.start_button['text'] = "Pause"
        self.start_button['command'] = self.stop_execution
        self.execution()

    def stop_execution(self):
        self.perform_execution = False
        self.start_button['text'] = "Start"
        self.start_button['command'] = self.start_execution

    def generate_solar_system(self):
        self.model.space_objects = []
        star_positions = [(-300e9, 0), (0, 0), (300e9, 0)]
        star_colors = ["yellow", "red", "blue"]
        planet_counts = [10, 20, 10]

        for i in range(3):
            star = Star(*star_positions[i], color=star_colors[i])
            star.m = 1.98892E30 * random.uniform(0.9, 1.1)
            star.R = 15
            self.model.space_objects.append(star)

            num_planets = planet_counts[i]
            orbits_needed = math.ceil(num_planets / 4)  # Max 4 planets per orbit

            # Генерируем наклонения для каждой орбиты (в радианах)
            inclinations = [random.uniform(-0.2, 0.2) for _ in range(orbits_needed)]

            for orbit_num in range(1, orbits_needed + 1):
                planets_in_orbit = min(4, num_planets - (orbit_num - 1) * 4)

                # Разные радиусы для планет на одной орбите (чтобы избежать точного совпадения)
                base_orbit_radius = 50e9 * orbit_num
                orbit_radii = [base_orbit_radius * (1 + 0.05 * j) for j in range(planets_in_orbit)]

                # Разные наклонения для планет на одной орбите
                orbit_inclination = inclinations[orbit_num - 1]
                planet_inclinations = [orbit_inclination + random.uniform(-0.05, 0.05)
                                       for _ in range(planets_in_orbit)]

                for planet_idx in range(planets_in_orbit):
                    planet = Planet()
                    planet.parent_star = star
                    planet.orbit_radius = orbit_radii[planet_idx]

                    # Угол между планетами на одной орбите
                    angle = 2 * math.pi * planet_idx / planets_in_orbit + random.uniform(-0.1, 0.1)
                    planet.orbit_angle = angle

                    # Рассчитываем 3D позицию (но проецируем на 2D)
                    inclination = planet_inclinations[planet_idx]
                    planet.x = star.x + planet.orbit_radius * math.cos(angle) * math.cos(inclination)
                    planet.y = star.y + planet.orbit_radius * math.sin(angle) * math.cos(inclination)

                    # Орбитальная скорость с учетом наклонения
                    linear_speed = 10e3 / math.sqrt(orbit_num)
                    planet.orbit_speed = linear_speed / planet.orbit_radius
                    planet.clockwise = (orbit_num % 2 == 0)

                    # Начальная скорость с учетом наклонения орбиты
                    speed = linear_speed
                    if planet.clockwise:
                        planet.Vx = speed * math.sin(angle) * math.cos(inclination)
                        planet.Vy = -speed * math.cos(angle) * math.cos(inclination)
                    else:
                        planet.Vx = -speed * math.sin(angle) * math.cos(inclination)
                        planet.Vy = speed * math.cos(angle) * math.cos(inclination)

                    planet.m = random.uniform(1e24, 1e26)
                    planet.color = f"#{random.randint(50, 255):02x}{random.randint(50, 255):02x}{random.randint(50, 255):02x}"
                    planet.R = random.randint(3, 8)
                    self.model.space_objects.append(planet)

                    # Добавляем спутники (с проверкой расстояний)
                    if i == 1 and orbit_num % 2 == 1:
                        satellite = Satellite()
                        sat_orbit_radius = planet.R * 1e9 * random.uniform(0.8, 1.2)
                        angle = random.uniform(0, 2 * math.pi)

                        # Позиция спутника с небольшим случайным смещением
                        satellite.x = planet.x + sat_orbit_radius * math.cos(angle) * random.uniform(0.9, 1.1)
                        satellite.y = planet.y + sat_orbit_radius * math.sin(angle) * random.uniform(0.9, 1.1)

                        satellite.orbit_radius = sat_orbit_radius
                        orbital_speed = (gravitational_constant * planet.m / sat_orbit_radius) ** 0.5
                        satellite.Vx = planet.Vx - orbital_speed * math.sin(angle)
                        satellite.Vy = planet.Vy + orbital_speed * math.cos(angle)
                        satellite.orbit_angle = angle
                        satellite.orbit_speed = orbital_speed / sat_orbit_radius
                        satellite.parent_planet = planet
                        satellite.m = planet.m * 0.001
                        satellite.R = planet.R * 0.3
                        satellite.clockwise = True
                        self.model.space_objects.append(satellite)

        max_distance = max(max(abs(obj.x), abs(obj.y)) for obj in self.model.space_objects)
        self.model.scale_factor = 0.4 * min(window_height, window_width) / max_distance
        return self.model.space_objects
    def open_file_dialog(self):
        self.perform_execution = False
        filename = askopenfilename(filetypes=(("Text files", "*.txt"), ("All files", "*.*")))

        if filename:
            success = self.load_from_file(filename)
            if success:
                self.display_system()
                self.view.update_system_name("Loaded from: " + filename)
            else:
                tkinter.messagebox.showerror("Error", "Failed to load the file")

    def generate_system_dialog(self):
        self.perform_execution = False
        self.generate_solar_system()
        self.display_system()
        self.view.update_system_name("Generated Solar System")

    def display_system(self):
        self.view.space.delete("all")
        for obj in self.model.space_objects:
            if obj.type == 'star':
                self.view.create_star_image(obj)
            elif obj.type in ['planet', 'satellite']:
                self.view.create_planet_image(obj)

        if self.view.show_orbits:
            self.view.draw_orbits()

    def save_file_dialog(self):
        out_filename = asksaveasfilename(filetypes=(("Text file", ".txt"),))
        if out_filename:
            self.write_space_objects_data_to_file(out_filename)

    def load_from_file(self, filename):
        """Загружает солнечную систему из файла"""
        self.model.space_objects = []
        object_types = {'Star': Star, 'Planet': Planet, 'Satellite': Satellite}

        try:
            with open(filename, 'r') as f:
                for line in f:
                    if not line.strip():
                        continue

                    parts = line.split()
                    obj_type = parts[0]
                    if obj_type not in object_types:
                        continue

                    # Создаем объект
                    obj = object_types[obj_type]()
                    obj.R = float(parts[1])
                    obj.color = parts[2]
                    obj.m = float(parts[3])
                    obj.x = float(parts[4])
                    obj.y = float(parts[5])
                    obj.Vx = float(parts[6])
                    obj.Vy = float(parts[7])

                    # Для планет и спутников устанавливаем родительские объекты
                    if obj_type == 'Planet':
                        # Находим ближайшую звезду как родительскую
                        min_dist = float('inf')
                        for potential_parent in self.model.space_objects:
                            if potential_parent.type == 'star':
                                dist = ((obj.x - potential_parent.x) ** 2 +
                                        (obj.y - potential_parent.y) ** 2) ** 0.5
                                if dist < min_dist:
                                    min_dist = dist
                                    obj.parent_star = potential_parent

                        # Устанавливаем орбитальные параметры
                        if obj.parent_star:
                            dx = obj.x - obj.parent_star.x
                            dy = obj.y - obj.parent_star.y
                            obj.orbit_radius = (dx ** 2 + dy ** 2) ** 0.5
                            obj.orbit_angle = math.atan2(dy, dx)

                            # Вычисляем угловую скорость
                            velocity_tangent = (-obj.Vx * dy + obj.Vy * dx) / obj.orbit_radius
                            obj.orbit_speed = velocity_tangent / obj.orbit_radius
                            obj.clockwise = velocity_tangent > 0

                    elif obj_type == 'Satellite':
                        # Находим ближайшую планету как родительскую
                        min_dist = float('inf')
                        for potential_parent in self.model.space_objects:
                            if potential_parent.type == 'planet':
                                dist = ((obj.x - potential_parent.x) ** 2 +
                                        (obj.y - potential_parent.y) ** 2) ** 0.5
                                if dist < min_dist:
                                    min_dist = dist
                                    obj.parent_planet = potential_parent

                        # Устанавливаем орбитальные параметры
                        if obj.parent_planet:
                            dx = obj.x - obj.parent_planet.x
                            dy = obj.y - obj.parent_planet.y
                            obj.orbit_radius = (dx ** 2 + dy ** 2) ** 0.5
                            obj.orbit_angle = math.atan2(dy, dx)

                            # Вычисляем угловую скорость
                            velocity_tangent = (-obj.Vx * dy + obj.Vy * dx) / obj.orbit_radius
                            obj.orbit_speed = velocity_tangent / obj.orbit_radius
                            obj.clockwise = velocity_tangent > 0

                    self.model.space_objects.append(obj)

            # Рассчитываем масштаб для отображения
            max_distance = max(max(abs(obj.x), abs(obj.y)) for obj in self.model.space_objects) or 1e12
            self.model.scale_factor = 0.4 * min(window_height, window_width) / max_distance

            return True

        except Exception as e:
            print(f"Ошибка загрузки файла: {e}")
            return False
    def write_space_objects_data_to_file(self, output_filename):
        """Сохраняет текущую систему в файл"""
        with open(f'{output_filename}.txt', 'w') as out_file:
            for obj in self.model.space_objects:
                if isinstance(obj, Star):
                    obj_type = "Star"
                elif isinstance(obj, Planet):
                    obj_type = "Planet"
                elif isinstance(obj, Satellite):
                    obj_type = "Satellite"
                else:
                    continue

                out_file.write(
                    f"{obj_type} {obj.R} {obj.color} {obj.m} {obj.x} {obj.y} {obj.Vx} {obj.Vy}\n"
                )

    def toggle_orbits(self):
        self.view.show_orbits = not self.view.show_orbits
        if not self.view.show_orbits:
            self.view.space.delete("orbit")
        else:
            self.view.draw_orbits()


root = tkinter.Tk()
SolarSystemController(root)
root.mainloop()