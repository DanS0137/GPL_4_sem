import fuzzylab as fl # type: ignore
import numpy as np
import pandas as pd # type: ignore
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error
import matplotlib.pyplot as plt

class FuzzyRegulator(fl.mamfis):
    def __init__(self):
        self._input_scaler = MinMaxScaler()
        self._output_scaler = MinMaxScaler()

        super().__init__()
        
        rule_list = [
            [1, 1, 5, 1, 1], #Если отклонение - отрицательное и Скорость изменения - отрицательная, то открывать быстро.
            [1, 2, 5, 1, 1], #Если отклонение - отрицательное и Скорость изменения - околонулевая, то открывать медленно.
            [1, 3, 4, 1, 1], #Если отклонение - отрицательное и Скорость изменения - положительная, то открывать медленно.

            [2, 1, 4, 1, 1], #Если отклонение - околонулевое и Скорость изменения - отрицательная, то открывать медленно.
            [2, 2, 3, 1, 1], #Если отклонение - околонулевое и Скорость изменения - околонулевое, то не трогать.
            [2, 3, 2, 1, 1], #Если отклонение - околонулевое и Скорость изменения - положительная, то закрывать медленно.

            [3, 1, 2, 1, 1], #Если отклонение - положительное и Скорость изменения - отрицательная, то закрывать медленно.
            [3, 2, 2, 1, 1], #Если отклонение - положительное и Скорость изменения - околонулевое, то закрывать медленно.
            [3, 3, 1, 1, 1]  #Если отклонение - положительное и Скорость изменения - положительная, то закрывать быстро.
        ]
        self.addRule(rule_list)

    # В метод передаётся двумерный список списков, в которых
    # хранятся новые параметры для функцияй принадлежности.
    def set_params(self, new_params):
        for input in range(len(self.Inputs)):
            for mf in range(len(self.Inputs[input].MembershipFunctions)):
                self.Inputs[input].MembershipFunctions[mf].Parameters = new_params[input][mf]

    # Возвращает параметры действующих функций принадлежности.
    def get_params(self):
        params = []
        for input in range(len(self.Inputs)):
            for mf in range(len(self.Inputs[input].MembershipFunctions)):
                params.append(self.Inputs[input].MembershipFunctions[mf].Parameters)
        return params

    # Расчитывает управляющее воздействие на основе предоставленных данных.    
    def predict(self, data):
        results = pd.Series()
        scaled_data = pd.DataFrame(columns=data.columns)

        #Нормализуем переданные данные.
        for col in data.columns:
            scaled_data[col] = self.scale(data[col], max(abs(data[col].min()), abs(data[col].max())))
        
        for row in scaled_data.shape[0]:
            #Список, в который будут добавляться значения в ужном порядке.
            values = []
            for i in range(scaled_data.shape[1]):
                #Получаем имя нечёткого множества.
                name = self.Inputs[i].Name
                #По этому имени обращаемся к нужному столбцу датафрэйма
                #и добавляем значение из нужной строки в список значений.
                values.append(scaled_data[name][row])
            #Расчёт.
            results[row] = fl.evalfis(self, values)

        return results
    
    #Добавляет входную нечёткую переменную с некоторым количеством множеств.
    def add_input(self, name, diaposone, sets_parameters):
        if diaposone == "Z-O":
            self.addInput([0, 1], Name=name)
        elif diaposone == "NO-PO":
            self.addInput([-1, 1], Name=name)
        else:
            raise Exception("Недопустимое значение diaposone, допустимые значения: \"Z-O\" и \"NO-PO\".")
        
        for i in range(len(sets_parameters)):
            self.addMF(name, 'gaussmf', sets_parameters[i])

    #Добавляет выходную нечёткую переменную с некоторым количеством множеств.
    def add_output(self, name, diaposone, sets_parameters):
        if diaposone == "Z-O":
            self.addOutput([0, 1], Name=name)
        elif diaposone == "NO-PO":
            self.addOutput([-1, 1], Name=name)
        else:
            raise Exception("Недопустимое значение diaposone, допустимые значения: \"Z-O\" и \"NO-PO\".")
        
        for i in range(len(sets_parameters)):
            self.addMF(name, 'gaussmf', sets_parameters[i])

    #Считает ошибку.
    def score(self, xTest, yTest):
        xResults = self.predict(xTest)
        return mean_absolute_error(xResults, yTest)
    
    #Нормализует переданные данные по указанному диапозону.
    def scale(self, data_series, dev_by_zero):
        self._input_scaler.fit(-dev_by_zero, dev_by_zero)
        scaledData = self._input_scaler.transform(data_series)
        return scaledData

    #Денормализует переданные данные в указанный диапозон.
    def unscale(self, scaled_data, dev_by_zero):
        self._input_scaler.fit(-dev_by_zero, dev_by_zero)
        return self._input_scaler.inverse_transform(scaled_data)
        
fr = FuzzyRegulator(0, 2)
fl.plotmf(fr, 'input', 1)
fl.plotmf(fr, 'input', 2)
fl.plotmf(fr, 'output', 1)
