def center_func(input_dict):
    x_val = input_dict['x_val']
    scaling_x = input_dict['x_scale']
    scaling_y = input_dict['y_scale']


    image_dimension = (1024, 768)
    five_cm_in_pixel = scaling_y * image_dimension[1]

    five_cm_in_x_scaling = five_cm_in_pixel / image_dimension[0]
    four_cm_in_x_scaling = (4/5) * five_cm_in_x_scaling
    diff = abs((0.5 - four_cm_in_x_scaling) - x_val)

    if diff > 0.05:
        direction = 'S' if x_val < 0.5 else 'W'
        distance = round((diff / five_cm_in_x_scaling) * 6)
        return f"{direction}{distance}|"

    return ""
