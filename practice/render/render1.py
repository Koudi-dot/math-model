# Импортируем модуль NumPy, реализующий быстрые операции с массивами
import numpy as np

# Загружаем VisPy упрощающий работу с OpenGL
from vispy import gloo
from vispy import app

# Это исходник вершинного шейдера, он будет вызывается для каждой вершины (точки)
# в отрисовываемой сцене. 
# Шейдеры пишутся на языке GLSL, который представляет собой C++ с рядом ограничений 
# и расширений.
vert = ("""
#version 120
"""
# Данные в шейдер передаются в атрибутах.
# Атрибутов может быть много, но все они соответствуют одной точке.
# Тип vec2 определен в GLSL и позволяет хранить вектор с двумя вещественными кооринатами.
# Также определены трехмерные vec3 и четырехмерные vec4 вектора.
"""
attribute vec2 a_position;
"""
# Это точка входа в шейдер, вызывается для каждой вершины один раз.
"""
void main (void) {
"""
    # Вершинный шейдер должен как минимум установить значение 
    # переменной gl_Position, сообщая OpenGL, где расположить вершину.
    # Координаты точек внутри OpenGL четырехмерные, последнюю координату всегда
    # нужно установить в 1.
    # Все координаты можно установить одним вызовом конструктора типа vec4.
    # К координатами вектора можно обращаться как полям структуры, с именами x, y, z и t.
    # Более того, можно обратиться к нескольктим полям сразу,
    # например, вызов a.xy возвращает вектор с двумя первыми компонентами вектора a.
"""
    gl_Position = vec4(a_position.xy,1,1);
}
""")

# Это исходный текст шейдера фрагменов, он отвечает за определение цвета
# отображаемых на экране пикселя (чуть сложнее, если разрешить смешивание цветов).
frag = ("""
#version 120
"""
# Это точка входа в шейдер.
# Аргументы в функцию не передаются, однако она видит атрибуты,
# определенные в шейдере вершин.
"""
void main() {
"""
    # Шейдер фрагментов должен вернуть цвет точки в переменной gl_FragColor.
    # Цвет задается четырехмерным вектором,
    # первые три координаты задают RGB компоненты цвета,
    # последняя (альфа канал) определяет прозрачность: 
    # 1 - полностью непрозрачный,
    # 0 - полностью прозрачный.
    # Просто установить значение альфы недостаточно, чтобы точка стала прозрачной.
    # Здесь мы просто установили постоянное значение цвета всех точек.
"""
    gl_FragColor = vec4(0.5,0.5,1,1); 
}
""")

# Этот класс представляет окно нашего приложения.
# Вызовы OpenGL будут отрисовывать элементы в это окно.
class Canvas(app.Canvas):
    # Это конструктор обьекта окна.
    def __init__(self):
        # Вызываем конструктор предка, который создаст окно размера size 
        # с заголовком title используя GLFW, QT 4, QT 5 и другие библиотеки, 
        # в зависимости от того, что имеется в системе.
        app.Canvas.__init__(self, size=(600, 600), title="Water surface simulator 1")
        # Устанавливаем настройкт OpenGL:
        # фоновый цвет clear_color черный,
        # запрещаем текст глубины depth_test (все точки будут отрисовываться),
        # запрещает смещивание цветов blend - цвет пикселя на экране равен gl_fragColor.
        gloo.set_state(clear_color=(0,0,0,1), depth_test=False, blend=False)
        # Компилируем и собираем программу из шейдеров вершин и фрагментов.
        # При ошибке в исходниках компиляция сорвется с выбросом исключения.
        self.program = gloo.Program(vert, frag)
        # Устанавливаем атрибут, заданные в вершинном шейдере, обращаеся по имени атрибута.
        # Атрибут можно проинициализировать массивом NumPy.
        # Первый индекс массива означает номер вершины, 
        # остальные должны совпадать с размером атрибута.
        # Тип vec2 имеет две координаты типа плавающей запятой одинарной точности (float32),
        # тотже тип выберем и для массива NumPy.
        # Мы передаем одну точку с координатами (0, 0), соответствующими центру экрана.
        # Коордианты (x,y) точек экрана меняются в диапазоне [-1,1].
        self.program["a_position"]=np.array([[0,0]],dtype=np.float32)
        # Считываем размер окна и сообщаем OpenGL
        self.activate_zoom()
        # Выводим окно
        self.show()

    # Эта функция вызывается при установке размера окна
    def activate_zoom(self):
        # Читаем размер окна
        self.width, self.height = self.size
        # Передаем размер окна в OpenGL
        gloo.set_viewport(0, 0, *self.physical_size)

    # app.Canvas содержит много обработчиков событий.
    # Этот метод будет вызываться каждый раз, когда окно нужно перерисовать.
    def on_draw(self, event):
        # Очищаем окно. 
        # Все пиксели устанавливаются в значение clear_color,
        # переданное в gloo.set_state.
        gloo.clear()
        # Запускаем шейдеры для отрисовки точек.
        # Шейдеры можно вызывть много раз, шейдеров может быть много.
        # Аргументы шейдера уже должны быть установлены,
        # атрибут a_position был установлен ранее.
        # Число элементов для отрисовки определяется длиной массивов, 
        # ассоциированных с аотрибутом.
        # Метод draw получает один аргумент, указывающий тип отрисовываемых элементов.
        # Сейчас мы хотим нарисовать точки.
        self.program.draw('points')
        # В результате мы увидим черное окно и голубое пятнышко
        # (https://ru.wikipedia.org/wiki/Pale_Blue_Dot)

# Этот скрипт можно запусть из командой строки
#     python3 render1.py,
# в это случае выполнится код ниже.
# Или может запусть интеракиивный сеанс
#     python3 
# и из питона импортировать скрипт для экспериментов:
#     import render1 as render
if __name__ == '__main__':
    # Создаем обьект приложения
    c = Canvas()
    # Запускаем обработчик событий.
    app.run()
