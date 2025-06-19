import math
import random

G = 6.67408E-11
sun_mass = 1.989E30
earth_mass = 5.972E24
pi = 3.1415926535
black_hole_mass = 1E35

star_mass_min = 0.08 * sun_mass    # ~1.6E29 кг
star_mass_max = 20.0 * sun_mass     # ~4.0E31 кг

# от суперземель до газовых гигантов
planet_mass_min = 0.5 * earth_mass # ~3.0E24 кг
planet_mass_max = 1500 * earth_mass # ~9.0E27 кг

# --- диапазоны расстояний ---
# 1 световой год ~ 9.46E15 м
# межзвездные расстояния
star_orbit_radius_min = 2E14      # 200 трлн км
star_orbit_radius_max = 1E15      # 1 квадриллион км (~0.1 св. года)

# <<< ИСПРАВЛЕНО: внутрисистемные расстояния >>>
# 1 а.е. = 1.496E11 м
planet_orbit_radius_min = 0.5 * 1.496E11  # ~0.5 а.е.
planet_orbit_radius_max = 50.0 * 1.496E11 # ~50 а.е. (дальний пояс койпера)

# орбиты спутников
satellite_orbit_radius_min = 3.844E8  # ~орбита луны
satellite_orbit_radius_max = 2.0E9    # 2 млн км

# --- диапазоны для спутников (относительные) ---
satellite_mass_ratio_min = 0.0001 # 0.01% от массы планеты
satellite_mass_ratio_max = 0.01   # 1% от массы планеты (очень крупный спутник)

with open('mega_system.txt', 'w') as f:
    print("Star0 1 black 1E35 0 0 0 0\n", file=f)
    for i in range(1,8):
        angle = random.uniform(0, 2*pi)
        r = star_orbit_radius_min + (i-1) * (star_orbit_radius_max - star_orbit_radius_min)/7 #random.uniform(star_orbit_radius_min, star_orbit_radius_max)
        x = r * math.cos(angle)
        y = r * math.sin(angle)
        m = random.uniform(star_mass_min, star_mass_max)
        velocity = (G*black_hole_mass/r)**0.5
        velocity_x = velocity * -math.sin(angle)
        velocity_y = velocity * math.cos(angle)
        print(f"Star{i} 5 blue {m} {x} {y} {velocity_x} {velocity_y}\n", file=f)
        for j in range(1,(i%2+1)*15+1):
            if j % 2 == 0:
                direction_planet = 1
            else:
                direction_planet = -1
            angle_planet = random.uniform(0, 2*pi)
            r_planet = j * (planet_orbit_radius_max - planet_orbit_radius_min)/30
            x_planet = r_planet * math.cos(angle_planet) + x
            y_planet = r_planet * math.sin(angle_planet) + y
            m_planet = random.uniform(planet_mass_min, planet_mass_max)
            velocity_planet = (G*m/r_planet)**0.5
            velocity_planet_x = velocity_planet * -math.sin(angle_planet) * direction_planet + velocity_x
            velocity_planet_y = velocity_planet * math.cos(angle_planet) * direction_planet + velocity_y
            print(f"Planet{j}_{i} 2 green {m_planet} {x_planet} {y_planet} {velocity_planet_x} {velocity_planet_y} Star{i}\n", file=f)
            direction_sat = -1
            if (j % 5 == 0 and i % 2 == 1 and j in [10, 20, 30]):
                for k in range(1,3):
                    angle_sat = random.uniform(0, 2 * pi)
                    r_sat = random.uniform(satellite_orbit_radius_min, satellite_orbit_radius_max)
                    x_sat = r_sat * math.cos(angle_sat) + x_planet
                    y_sat = r_sat * math.sin(angle_sat) + y_planet
                    m_sat = random.uniform(satellite_mass_ratio_min, satellite_mass_ratio_max) * m_planet
                    velocity_sat = (G * m_planet / r_sat) ** 0.5
                    velocity_sat_x = velocity_sat * -math.sin(angle_sat) * direction_sat + velocity_planet_x
                    velocity_sat_y = velocity_sat * math.cos(angle_sat) * direction_sat + velocity_planet_y
                    print(f"Satellite{k}_{j}_{i} 1 white {m_sat} {x_sat} {y_sat} {velocity_sat_x} {velocity_sat_y} Planet{j}_{i}\n",file=f)
            if (j % 5 == 0 and i % 2 == 0 and j in [5, 10, 15]):
                angle_sat = random.uniform(0, 2*pi)
                r_sat = random.uniform(satellite_orbit_radius_min, satellite_orbit_radius_max)
                x_sat = r_sat * math.cos(angle_sat) + x_planet
                y_sat = r_sat * math.sin(angle_sat) + y_planet
                m_sat = random.uniform(satellite_mass_ratio_min, satellite_mass_ratio_max) * m_planet
                velocity_sat = (G*m_planet/r_sat)**0.5
                velocity_sat_x = velocity_sat * -math.sin(angle_sat) * direction_sat + velocity_planet_x
                velocity_sat_y = velocity_sat * math.cos(angle_sat) * direction_sat + velocity_planet_y
                print(f"Satellite1_{j}_{i} 1 white {m_sat} {x_sat} {y_sat} {velocity_sat_x} {velocity_sat_y} Planet{j}_{i}\n", file=f)
    f.close()
print("Завершено формирование звездной системы")
