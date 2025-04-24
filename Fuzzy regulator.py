import fuzzylab as fl # type: ignore
import numpy as np
import pandas as pd # type: ignore
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error
import plotly.graph_objects as go

class FuzzyRegulator(fl.mamfis):
    def __init__(self):
        self._scaler = MinMaxScaler()
        self._unscaler = MinMaxScaler()

        super().__init__()

    # В метод передаётся список списков, в которых
    # хранятся новые параметры для функций принадлежности.
    def set_params(self, new_params):
        for input in range(len(self.Inputs)):
            for mf in range(len(self.Inputs[input].MembershipFunctions)):
                self().Inputs[input].MembershipFunctions[mf].Parameters = new_params[input][mf]

    # Возвращает параметры действующих функций принадлежности
    # в виде спсика списков.
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
        '''
        #Нормализуем переданные данные.
        for col in data.columns:
            scaled_data[col] = self.scale(data[col], [[-max(abs(data[col].min()), abs(data[col].max()))],
                                                        [max(abs(data[col].min()), abs(data[col].max()))]])
        '''        
        for row in range(data.shape[0]):
            #Список, в который будут добавляться значения в ужном порядке.
            values = []
            for i in range(data.shape[1]):
                #Получаем имя нечёткого множества.
                name = self.Inputs[i].Name
                #По этому имени обращаемся к нужному столбцу датафрэйма
                #и добавляем значение из нужной строки в список значений.
                values.append(data[name][row])
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
        
        for parameters in sets_parameters:
            self.addMF(name, 'gaussmf', parameters)

    #Добавляет выходную нечёткую переменную с некоторым количеством множеств.
    def add_output(self, name, diaposone, sets_parameters):
        if diaposone == "Z-O":
            self.addOutput([0, 1], Name=name)
        elif diaposone == "NO-PO":
            self.addOutput([-1, 1], Name=name)
        else:
            raise Exception("Недопустимое значение diaposone, допустимые значения: \"Z-O\" и \"NO-PO\".")
        
        for parameters in sets_parameters:
            self.addMF(name, 'trimf', parameters)

    #Добавляет правила для нечёткой системы.
    def add_rules(self, rule_list):
        self.addRule(rule_list)

    #Считает ошибку.
    def score(self, xTest, yTest):
        xResults = self.predict(xTest)
        return mean_absolute_error(xResults, yTest)
    
    #Нормализует переданные данные по указанному диапозону.
    def scale(self, data, range, feature_range="NO-PO"):
        if feature_range=="NO-PO":
            self._scaler.set_params(**{"feature_range":(-1,1)})
        if feature_range=="Z-O":
            self._scaler.set_params(**{"feature_range":(0,1)})
            
        self._scaler.fit(np.array(data).reshape(-1,1))
        scaledData = self._scaler.transform(np.array(data).reshape(-1,1))
        return pd.Series(scaledData.flatten())

    #Денормализует переданные данные в указанный диапозон.
    def unscale(self, scaled_data, range, feature_range="NO-PO"):
        if feature_range=="NO-PO":
            self._unscaler.set_params(**{"feature_range":(-1,1)})
        if feature_range=="Z-O":
            self._unscaler.set_params(**{"feature_range":(0,1)})

        self._unscaler.fit(range)
        return self._unscaler.inverse_transform(scaled_data)
        
fr = FuzzyRegulator()

#Добавляем первую входную переменную.
parameters = [
    [0.3, -1],
    [0.3, 0],
    [0.3, 1]
]
fr.add_input(name='dH', diaposone="NO-PO", sets_parameters=parameters)

#Добавляем вторую входную переменную.
fr.add_input(name='dV', diaposone="NO-PO", sets_parameters=parameters)

#Добавляем выходную переменную.
parameters=[
    [-2, -1, -0.6],
    [-0.8, -0.4, 0.0],
    [-0.4, 0, 0.4],
    [0, 0.4, 0.8],
    [0.6, 1, 2]
]
fr.add_output('Command', 'NO-PO', parameters)

#Добавляем правила.
rule_list=[
    [3, 0, 1, 2, 1],
    [2, 3, 2, 1, 1],
    [2, 0, 3, 1, 1],
    [2, 1, 4, 1, 1],
    [1, 0, 5, 2, 1]
]
fr.add_rules(rule_list)

#Расчитываем.
data = pd.read_excel("C:/Users/Admin/Desktop/GPL_4_sem/data.xlsx")
df = pd.DataFrame(data)
results = fr.predict(df[['dH', 'dV']])
print(fr.score(df[['dH','dV']], df['Command']))

#Отрисовываем.
X = fl.arange(0, 1, 200)
Y = fl.arange(0, 1, 200)
Z = np.zeros([201, 201])
for x in X:
  for y in Y:
    Z[int(x), int(y)] = (fl.evalfis(fr, [x/100 - 1, y/100 - 1]))*100
fig = go.Figure(data=[go.Surface(x=X, y=Y, z=Z)])

fig.show()