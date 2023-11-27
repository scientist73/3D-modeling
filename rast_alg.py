# Юсупов Д.Р. ИУ8-52
#
# В данном модуле в виде функций реализованы некоторые растровые алгоритмы:
#
#   * bresenham_line                - алгоритм Брезенхейма построения прямой
#   * bresenham_circle              - алгоритм Брезенхейма построения окружности
#
#   * cohen_sutherland_clipper      - алгоритм Коэна - Сазерленда отсечения отрезка прямоугольником
#   * liang_barsky_clipper          - алгоритм Лианга - Барски отсечения отрезка прямоугольником
#   * cyrus_beck_clipper            - алгоритм Кируса - Бека отсечения отрезка выпуклым многоугольником
#
#   * sobel_filter                  - фильтр Собеля для выделения контуров изображения
#
#   * line_fill                     - алгоритм рекурсивной заливки отрезками с затравкой
#   * bitmask_fill (not ready)      - алгоритм нерекурсивной заливки по битовой маске
#

from PIL import Image
import array
from math import sqrt
from statistics import mean

def bresenham_line(line : tuple[tuple[int, int], tuple[int, int]], image : Image, color = 255):
# функция рисует на растровой плоскости отрезок по 2м точкам по целочисленному алгоритму Брезенхейма
#
# параметры:
#   line в виде ((x_1, y_1), (x_2, y_2)) - отрезок
#   image - растровая плоскость
#
    # задание переменных
    x_1 = line[0][0]
    y_1 = line[0][1]
    x_2 = line[1][0]
    y_2 = line[1][1]

    # если точка 1 лежит правее точки 2, то поменяем их местами
    if (x_1 > x_2):
        x = x_1; x_1 = x_2; x_2 = x
        y = y_1; y_1 = y_2; y_2 = y
    
    # данная прямая не помещается полностью на нашу плоскость
    if ((x_1 < 0) | (x_2 > image.size[0]) | (min(y_1, y_2) < 0) | (max(y_1, y_2) > image.size[1])):
        return


    dx = (x_2 - x_1); dy = (y_2 - y_1)

    if (dy >= 0):
        if(dx >= dy):
            image.putpixel((x_1, y_1), color)

            x = x_1; y = y_1; var = 0
            while (x < x_2):
                var += dy
                if(2*var > dx):
                    y += 1
                    var -= dx
                x += 1

                image.putpixel((x, y), color)

        else:
            image.putpixel((x_1, y_1), color)

            x = x_1; y = y_1; var = 0
            while (y < y_2):
                var += dx
                if(2*var > dy):
                    x += 1
                    var -= dy
                y += 1

                image.putpixel((x, y), color)
    else:
        if(dx >= -dy):
            image.putpixel((x_1, y_1), color)

            x = x_1; y = y_1; var = 0
            while (x < x_2):
                var += -dy
                if(2*var > dx):
                    y -= 1
                    var -= dx
                x += 1

                image.putpixel((x, y), color)

        else:
            image.putpixel((x_1, y_1), color)

            x = x_1; y = y_1; var = 0
            while (y > y_2):
                var += dx
                if(2*var > -dy):
                    x += 1
                    var -= -dy
                y -= 1
                
                image.putpixel((x, y), color)
def bresenham_circle(xy : tuple[int, int], R : int, image : Image, color = 255):
# функция рисует на растровой плоскости окружность по целочисленному алгоритму Брезенхейма
#
# параметры:
#   xy в виде (x, y) - центр окружности
#   R - радиус окружности    
#   image - растровая плоскость
#
    # задание переменных
    x_0 = xy[0]
    y_0 = xy[1]

    # данная окружность не помещается полностью на нашу плоскость
    if (x_0 - R < 0 | x_0 + R > image.size[0] | y_0 - R < 0 | y_0 + R > image.size[1]):
        return

    dx = 0; dy = R; f = 1 - R
    image.putpixel((x_0 + dx, y_0 + dy), color) # 0
    image.putpixel((y_0 + dy, x_0 + dx), color) # 3
    image.putpixel((x_0 - dx, y_0 - dy), color) # 6
    image.putpixel((y_0 - dy, x_0 - dx), color) # 9


    # данный алгоритм чертит 0 - 1.5 круга от его верхушки (dx, dy) = (0, R)
    # остальные вершины получаются симметрично
    while(dx <= dy):
        if(f > 0):
            dy -= 1
            f += 2 * (dx - dy) + 5
        else:
            f += 2 * dx + 3
        dx += 1

        image.putpixel((x_0 + dx, y_0 + dy), color) # 0 - 1.5
        image.putpixel((x_0 + dy, y_0 + dx), color) # 1.5 - 3
        image.putpixel((x_0 + dy, y_0 - dx), color) # 3 - 4.5
        image.putpixel((x_0 + dx, y_0 - dy), color) # 4.5 - 6
        image.putpixel((x_0 - dx, y_0 - dy), color) # 6 - 7.5
        image.putpixel((x_0 - dy, y_0 - dx), color) # 7.5 - 9
        image.putpixel((x_0 - dy, y_0 + dx), color) # 9 - 10.5
        image.putpixel((x_0 - dx, y_0 + dy), color) # 10.5 - 12
def rectangle(x_min, x_max, y_min, y_max, image : Image):
# функция рисует на растровой плоскости прямоугольник
#
# параметры:
#   x_min - левая грань прямоугольника
#   x_max - правая грань прямоугольника
#   y_min - нижняя грань прямоугольника
#   y_max - верхняя грань прямоугольника   
#   image - растровая плоскость
#
    bresenham_line(((x_min, y_min), (x_min, y_max)), image) # LEFT
    bresenham_line(((x_max, y_min), (x_max, y_max)), image) # RIGHT
    bresenham_line(((x_min, y_min), (x_max, y_min)), image) # BOTTOM
    bresenham_line(((x_min, y_max), (x_max, y_max)), image) # TOP
def polygon(xy, image : Image):
# функция рисует на растровой плоскости произовольный многоугольник
#
# параметры:
#   xy - точки многоугольника в виде ((x_1, y_1), (x_2, y_2), ...)  
#   image - растровая плоскость
#
    for i in range(len(xy)):
        bresenham_line(((xy[i - 1][0], xy[i - 1][1]), (xy[i][0], xy[i][1])), image)
def cohen_sutherland_clipper(line : tuple[tuple[int, int], tuple[int, int]], x_min, x_max, y_min, y_max, image : Image):
# функция отсекает некоторый отрезок прямоугольником на растровой плоскость по алгоритму Коэна - Сазерленда
#
# параметры:
#   line в виде ((x_1, y_1), (x_2, y_2)) - отрезок
#   x_min - левая грань прямоугольника
#   x_max - правая грань прямоугольника
#   y_min - нижняя грань прямоугольника
#   y_max - верхняя грань прямоугольника   
#   image - растровая плоскость
#
    def code(xy : tuple[int, int], x_min, x_max, y_min, y_max):
    # вспомогательная функция, вычисляющая код точки по алгоритму Коэна - Сазерленда, относительно прямоугольника
        x = xy[0]
        y = xy[1]

        code = 0


        code += LEFT if x < x_min else 0
        code += RIGHT if x > x_max else 0
        code += BOTTOM if y < y_min else 0
        code += TOP if y > y_max else 0

        return code
    
    # задаю константы
    LEFT = 1; RIGHT = 2; BOTTOM = 4; TOP = 8

    # задание переменных
    x_1 = line[0][0]
    y_1 = line[0][1]
    x_2 = line[1][0]
    y_2 = line[1][1]

    
    x_a = x_1; y_a = y_1
    x_b = x_2; y_b = y_2

    x_c = x_a; y_c = y_a

    code_a = code(x_a, y_a, x_min, x_max, y_min, y_max)
    code_b = code(x_b, y_b, x_min, x_max, y_min, y_max)
    code_c = code(x_c, y_c, x_min, x_max, y_min, y_max)

    # когда коды обоих точек будут равны 0, тогда они будут в прямоугольнике
    while (code_a | code_b):

        # если обе точки с одной стороны прямоугольника, то отрезок не пересекает прямоугольник
        if (code_a & code_b):
            break

        # выбираем точку c ненулевым кодом
        if (code_a):
            x_c = x_a
            y_c = y_a
            code_c = code_a
        elif (code_b):
            x_c = x_b
            y_c = y_b
            code_c = code_b
    

        # если c левее прямоугольника, то передвигаем c на прямую x = x_min
        if (code_c & LEFT):
            y_c += round((y_a - y_b) * (x_min - x_c) / (x_a - x_b))
            x_c = x_min
        # если c правее прямоугольника, то передвигаем c на прямую x = x_max
        elif (code_c & RIGHT):
            y_c += round((y_a - y_b) * (x_max - x_c) / (x_a - x_b))
            x_c = x_max
        # если c ниже прямоугольника, то передвигаем c на прямую y = y_min
        elif (code_c & BOTTOM):
            x_c += round((x_a - x_b) * (y_min - y_c) / (y_a - y_b))
            y_c = y_min
        # если c выше прямоугольника, то передвигаем c на прямую y = y_max
        elif (code_c & TOP):
            x_c += round((x_a - x_b) * (y_max - y_c) / (y_a - y_b))
            y_c = y_max
    

        # смещаем точку
        if (code_a == code_c):
            x_a = x_c; y_a = y_c
            code_a = code(x_a, y_a, x_min, x_max, y_min, y_max)
        elif (code_b == code_c):
            x_b = x_c; y_b = y_c
            code_b = code(x_b, y_b, x_min, x_max, y_min, y_max)


    rectangle(x_min, x_max, y_min, y_max, image)
    bresenham_line(((x_a, y_a), (x_b, y_b)), image)
def liang_barsky_clipper(line : tuple[tuple[int, int], tuple[int, int]], x_min, x_max, y_min, y_max, image : Image):
# функция отсекает некоторый отрезок прямоугольником на растровой плоскость по алгоритму Лианга - Барски
#
# параметры:
#   line в виде ((x_1, y_1), (x_2, y_2)) - отрезок
#   x_min - левая грань прямоугольника
#   x_max - правая грань прямоугольника
#   y_min - нижняя грань прямоугольника
#   y_max - верхняя грань прямоугольника   
#   image - растровая плоскость
#
    # задание переменных
    x_1 = line[0][0]
    y_1 = line[0][1]
    x_2 = line[1][0]
    y_2 = line[1][1]


    p_1 = - (x_2 - x_1)
    p_2 = - p_1
    p_3 = - (y_2 - y_1)
    p_4 = - p_3

    q_1 = x_1 - x_min
    q_2 = x_max - x_1
    q_3 = y_1 - y_min
    q_4 = y_max - y_1

    neg_arr = array.array('f'); neg_arr.append(0.0) # массив значений t для LEFT и BOTTOM (левой и нижней граней прямоугольника)
    pos_arr = array.array('f'); pos_arr.append(1.0) # массив значений t для RIGHT и TOP (правой и верхней граней прямоугольника)

    # если p_1 == 0 или p_3 == 0, то прямая параллельна вертикальным или горизонтальным сторонам прямоугольника соответственно
    # в данном случае при q_i < 0 прямая проходит вне прямоугольника
    if ((p_1 == 0 & (q_1 < 0 | q_2 < 0)) | (p_3 == 0 & (q_3 < 0 | q_4 < 0))):
        return
    
    # при p_1 != 0 прямая не параллельна вертикальным сторонам, то есть будет их пересекать
    if (p_1 != 0):
        t_1 = q_1 / p_1
        t_2 = q_2 / p_2

        if (p_1 < 0):
            neg_arr.append(t_1)
            pos_arr.append(t_2)
        else:
            neg_arr.append(t_2)
            pos_arr.append(t_1)

    # при p_3 != 0 прямая не параллельна горизонтальным сторонам, то есть будет их пересекать
    if (p_3 != 0):
        t_3 = q_3 / p_3
        t_4 = q_4 / p_4

        if (p_3 < 0):
            neg_arr.append(t_3)
            pos_arr.append(t_4)
        else:
            neg_arr.append(t_4)
            pos_arr.append(t_3)

    t_n_1 = max(neg_arr)
    t_n_2 = min(pos_arr)

    if(t_n_1 > t_n_2):
        return

    x_n_1 = round(x_1 + t_n_1 * p_2)
    y_n_1 = round(y_1 + t_n_1 * p_4)

    x_n_2 = round(x_1 + t_n_2 * p_2)
    y_n_2 = round(y_1 + t_n_2 * p_4)

    rectangle(x_min, x_max, y_min, y_max, image)
    bresenham_line(((x_n_1, y_n_1), (x_n_2, y_n_2)), image)
def cyrus_beck_clipper(line : tuple[tuple[int, int], tuple[int, int]], xy, image):
# функция отсекает некоторый отрезок выпуклым многоугольником на растровой плоскость по алгоритму Кируса - Бека
#
# параметры:
#   line в виде ((x_1, y_1), (x_2, y_2)) - отрезок
#   xy - точки многоугольника в виде ((x_1, y_1), (x_2, y_2), ...)  
#   image - растровая плоскость
#
    def dot(v_xy_1 : (int, int), v_xy_2 : (int, int)):
    # вспомогательная функция вычисления скалярного произведения двух векторов
    #
    # параметры:
    #  v_xy_i в виде (x_i, y_i) - вектор i
    #
        return v_xy_1[0] * v_xy_2[0] + v_xy_1[1] * v_xy_2[1]
    def vec(line : tuple[tuple[int, int], tuple[int, int]]):
    # вспомогательная функция вычисления нормализированного вектора по двум точкам
    #
    # параметры:
    #   line в виде ((x_1, y_1), (x_2, y_2)) - отрезок
    #
        # задание переменных
        x_1 = line[0][0]
        y_1 = line[0][1]
        x_2 = line[1][0]
        y_2 = line[1][1]

        return ((x_2 - x_1) / sqrt((x_1 - x_2) ** 2 + (y_2 - y_1) ** 2), (y_2 - y_1) / sqrt((x_2 - x_1) ** 2 + (y_2 - y_1) ** 2))
    def nor(xy_1 : (int, int), xy_2 : (int, int), xy_0 : (int, int)):
    # вспомогательная функция вычисления нормализированной нормали к отрезку, направленной в сторону точки xy_0
    #
    # параметры:
    #   xy_i в виде (x_i, y_i) - точка i отрезка, i = {1, 2}
    #   xy_0 в виде (x_0, y_0) - точка, в сторону которой ориентирована нормаль
    #
        v_xy = vec((xy_1, xy_2))
        v_nor = (0, 0)
        
        if (v_xy[0] == 0):
            v_nor = (1, 0)
        elif (v_xy[1] == 0):
            v_nor = (0, 1)
        else:
            # при x_2 = 1 :  y_2 = - (x_1/y_1) из уравнения x_1*x_2 + y_1*y_2 = 0
            v_nor = (1, - v_xy[0]/v_xy[1])
            v_nor = tuple(t / sqrt(1 + (- v_xy[0]/v_xy[1]) ** 2) for t in v_nor)
        
        v_nor = v_nor if dot(v_nor, vec((xy_1, xy_0))) > 0 else tuple(-t for t in v_nor)
        
        return v_nor
    def is_point_right_to_vec(xy_1 : (int, int), xy_2 : (int, int), xy : (int, int)):
    # вспомогательная функция, определяющая лежит ли точка правее луча
    #
    # параметры:
    #   xy_i в виде (x_i, y_i) - точки луча, направленного след образом xy_1 -> xy_2
    #   xy в виде (x, y) - точка
    #
        # D = (х - х1) * (у2 - у1) - (у - у1) * (х2 - х1)
        D = (xy[0] - xy_1[0]) * (xy_2[1] - xy_1[1]) - (xy[1] - xy_1[1]) * (xy_2[0] - xy_1[0])

        # если D = 0, то точка лежит на прямой
        # если D > 0, то точка правее луча
        # если D < 0, то точка левее луча
        return True if (D > 0) else False
    def line_cross_point(line_1 : tuple[tuple[int, int], tuple[int, int]] , line_2 : tuple[tuple[int, int], tuple[int, int]]):
    # вспомогательная функция нахождения координаты пересечения двух непараллельных прямых
    #
    # параметры:
    #   line_i в виде ((x_1, y_1), (x_2, y_2)) - линия i, которая строится по двум точкам
    #
        # найду уравнения прямых вида y = kx + b
        # k = (y_2 - y_1) / (x_2 - x_1)
        k_1 = (line_1[1][1] - line_1[0][1]) / (line_1[1][0] - line_1[0][0])
        k_2 = (line_2[1][1] - line_2[0][1]) / (line_2[1][0] - line_2[0][0])
        # b = y - kx (подставляю первую точку)
        b_1 = line_1[0][1] - k_1 * line_1[0][0]
        b_2 = line_2[0][1] - k_2 * line_2[0][0]


        # из y = kx + b получаю k_1*x + b_1 = k_2*x + b_2
        x = (b_2 - b_1) / (k_1 - k_2)
        y = k_1 * x + b_1

        return (x, y)
    def center_point_polygon(xy):
    # вспомогательная функция нахождания геометрического центра многоугольника
    #
    # параметры:
    #   xy - точки многоугольника в виде ((x_1, y_1), (x_2, y_2), ...)
    #
        xy_c = [0, 0]

        for i in range(len(xy)):
            xy_c[0] += xy[i][0]
            xy_c[1] += xy[i][1]
        xy_c = (xy_c[0]/len(xy), xy_c[1]/len(xy))

        return xy_c
    
    # задание переменных
    x_1 = line[0][0]
    y_1 = line[0][1]
    x_2 = line[1][0]
    y_2 = line[1][1]

    # изначальные параметры отрезка в параметрическом виде p = p_0 + t * dp
    t_1 = 0; t_2 = 1
    p_0_x = x_1
    p_0_y = y_1
    dp_x = x_2 - x_1
    dp_y = y_2 - y_1

    # нахожу геометрический центр многоугольника
    xy_c = center_point_polygon(xy)

    # нахожу вектор v_xy по исходному отрезку
    v_xy = vec(line)


    # упорядочиваю вершины против часовой стрелки
    if(is_point_right_to_vec((xy[0][0], xy[0][1]), (xy[1][0], xy[1][1]), xy_c)):
        xy = xy[::-1]

    # обхожу многоугольник против часовой стрелки
    for i in range(len(xy)):

        # нахожу нормаль n_edge ребра, ориентированную вовнутрь
        # и скалярное произведение v_dot
        n_edge = nor((xy[i - 1][0], xy[i - 1][1]), (xy[i][0], xy[i][1]), xy_c)
        v_dot = dot(v_xy, n_edge)

        # если v_dot == 0, то отрезок параллелен стороне многоугольника
        if (v_dot == 0):
            # если любая точка отрезка лежит правее ребра, то отрезок невиден
            if (is_point_right_to_vec((xy[i - 1][0], xy[i - 1][1]), (xy[i][0], xy[i][1]), (xy_1[0], xy_1[1]))):
                return

        # если v_dot < 0, то отрезок направлен с внутренней на внешнюю сторону ребра
        elif (v_dot < 0):
            # найду пересечение отрезка и ребра
            (x, y) = line_cross_point(line, ((xy[i - 1][0], xy[i - 1][1]), (xy[i][0], xy[i][1])))
            # t = (x - x_1) / (x_2 - x_1)
            t = (x - p_0_x) / dp_x

            # изменяю конец отрека, если t < t_2
            if (t < t_2):
                t_2 = t

        # если v_dot > 0, то отрезок направлен с внешней на внутреннюю сторону ребра
        elif (v_dot > 0):
            # найду пересечение отрезка и ребра
            (x, y) = line_cross_point(line, ((xy[i - 1][0], xy[i - 1][1]), (xy[i][0], xy[i][1])))
            # t = (x - x_1) / (x_2 - x_1)
            t = (x - p_0_x) / dp_x

            
            # изменяю начало отрека, если t > t_1
            if (t > t_1):
                t_1 = t

    # если t_1 < t_2, то отрезок видим; иначе отбрасываем
    if (t_1 < t_2):
        polygon(xy, image)
        bresenham_line(((round(p_0_x + t_1 * dp_x), round(p_0_y + t_1 * dp_y)), (round(p_0_x + t_2 * dp_x), round(p_0_y + t_2 * dp_y))), image)
def sobel_filter(image_path, new_image_path):
# функция обрабатывает изображение с помощью фильтра Собеля (выделяет его контуры)
#
# параметры:
#   image_path - путь до изображения
#   new_image_path - путь до нового изображения
#
    def sobel_operator(xy : tuple[int, int], image : Image):
    # вспомогательная функция, вычисляющая значения оператора Собеля в точке
    #
    # параметры:
    #   xy в виде (x, y) - точка 
    #   image - изображение
        x = xy[0]
        y = xy[1]

        # Вычисляем значения яркости пикселей в 3x3 окрестности точки с координатами (x,y)
        z1 = mean(image.getpixel((x-1,y-1)))
        
        z2 = mean(image.getpixel((x,y-1)))
        z3 = mean(image.getpixel((x+1,y-1)))
        z4 = mean(image.getpixel((x-1,y)))
        #z5 = mean(image.getpixel((x,y)))
        z6 = mean(image.getpixel((x+1,y)))
        z7 = mean(image.getpixel((x-1,y+1)))
        z8 = mean(image.getpixel((x,y+1)))
        z9 = mean(image.getpixel((x+1,y+1)))

        # Вычисляем значения частных производных
        G_x = z7 + 2*z8 + z9 - (z1 + 2*z2 + z3)
        G_y = z3 + 2*z6 + z9 - (z1 + 2*z4 + z7)

        # Возвращаем значение градиента в точке с координатами (x,y)
        return sqrt(G_x ** 2 + G_y ** 2)

    image = Image.open(image_path)
    new_image = Image.new('RGB', (image.size[0], image.size[1]))

    for x in range(1, image.size[0] - 1):
        for y in range(1, image.size[1] - 1):
            new_image.putpixel((x, y), round(sobel_operator((x, y), image)))
    new_image.save(new_image_path)
    new_image.show()
def line_fill(image : Image, new_image_path, start_point : tuple[int, int], color):
# функция заливки произвольной области: заливает произвольную одноцветную область начиная с точки start_point
# (алгоритм определяет границы заливки как любой цвет, отличный от исходного цвета стартовой точки)
#
# параметры:
#   image - растровая плоскость
#   new_image_path - путь до нового изображения
#   start_point в виде (x, y) - затравочная точка
#   color - цвет заливки
#
    def fill(left_x, right_x, y, image, start_pixel_value, color):
    # рекурсивная функция, заливающая линию
    #
    # параметры:
    #
    #   left_x, right_x - левая и правая границы заливки соответственно (включая их)
    #   y - ордината прямой заливки
    #   start_point_value - значение пикселей, которые надо залить
    #   color - цвет заливки
    #
        bresenham_line(((left_x, y), (right_x, y)), image, color)
        
        # top
        if (y + 1 < image.size[1]):
            l_x = 0
            for i in range(left_x, 0, -1):
                if (image.getpixel((i, y + 1)) != start_pixel_value):
                    l_x = i + 1
                    break
            if (l_x < left_x):
                fill(l_x, left_x, y + 1, image, start_pixel_value, color)
            
            r_x = image.size[0] - 1
            for i in range(right_x, image.size[0]):
                if (image.getpixel((i, y + 1)) != start_pixel_value):
                    r_x = i - 1
                    break
            if (r_x > right_x):
                fill(right_x, r_x, y + 1, image, start_pixel_value, color)

            for i in range(left_x, right_x + 1):
                if (image.getpixel((i, y + 1)) == start_pixel_value):
                    l_x = i
                    while (image.getpixel((i, y + 1)) == start_pixel_value):
                        r_x = i
                        i += 1

                        if (i > right_x):
                            break

                    fill(l_x, r_x, y + 1, image, start_pixel_value, color)
        # bot
        if (y > 0):
            
            l_x = 0
            for i in range(left_x, 0, -1):
                if (image.getpixel((i, y - 1)) != start_pixel_value):
                    l_x = i + 1
                    break
            if (l_x < left_x):
                fill(l_x, left_x, y - 1, image, start_pixel_value, color)
            
            r_x = image.size[0] - 1
            for i in range(right_x, image.size[0]):
                if (image.getpixel((i, y - 1)) != start_pixel_value):
                    r_x = i - 1
                    break
            if (r_x > right_x):
                fill(right_x, r_x, y - 1, image, start_pixel_value, color)

            for i in range(left_x, right_x + 1):
                if (image.getpixel((i, y - 1)) == start_pixel_value):
                    l_x = i
                    while (image.getpixel((i, y - 1)) == start_pixel_value):
                        r_x = i
                        i += 1

                        if (i > right_x):
                            break

                    fill(l_x, r_x, y - 1, image, start_pixel_value, color)


    new_image = image.copy()
    start_pixel_value = image.getpixel(start_point)

    # если цвет стартового пикселя уже color, то заливка не требуется
    if (start_pixel_value == color):
        return
    
    # нахожу левую и правую границы (границы включаются в заливку)
    left_x = 0
    for i in range(start_point[0], 0, -1):
        if (image.getpixel((i, start_point[1])) != start_pixel_value):
            left_x = i + 1
            break

    right_x = image.size[0] - 1
    for i in range(start_point[0], image.size[0]):
        if (image.getpixel((i, start_point[1])) != start_pixel_value):
            right_x = i - 1
            break
    
    fill(left_x, right_x, start_point[1], new_image, start_pixel_value, color)
    new_image.save(new_image_path)
    new_image.show()
def bitmask_fill(image : Image, new_image_path, bitmask : Image, color):
# функция заливки произвольной замкнутой фигуры, представленной битовой маской
#
# параметры:
#   image_path - путь до изображения
#   new_image_path - путь до нового изображения
#   bitmask - битовая маска (представляет собой картинку с любой замкнутой фигурой, цвет фона - белый, границы фигуры - черный)
#   color - цвет заливки
#
    pass
