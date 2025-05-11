import dash
from dash import Dash, dcc, html, Input, Output, State, callback
import dash_bootstrap_components as dbc
import os

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], prevent_initial_callbacks=True)

# Словники з даними про гітари та деревину
guitar_types = {
    'electric': {'name': 'Електрична', 'base_price': 10000, 'strings': [6, 7, 8], 'max_age': 80},
    'acoustic': {'name': 'Акустична', 'base_price': 6000, 'strings': [6], 'max_age': None},
    'bass': {'name': 'Бас', 'base_price': 8000, 'strings': [4, 5], 'max_age': 80},
    'ukulele': {'name': 'Укулеле', 'base_price': 3000, 'strings': [4], 'max_age': 40}
}

woods = {
    'mahogany': {'name': 'Червоне дерево', 'multiplier': 1.2},
    'maple': {'name': 'Клен', 'multiplier': 1.1},
    'oak': {'name': 'Дуб', 'multiplier': 0.8},
    'cedar': {'name': 'Кедр', 'multiplier': 0.9},
    'rosewood': {'name': 'Палісандр', 'multiplier': 1.05},
    'spruce': {'name': 'Ялина', 'multiplier': 1.15}
}

# Інтерфейс користувача
app.layout = dbc.Container([
    html.H1("Оцінка вартості гітари", className="text-center my-4"),
    
    dbc.Card([
        dbc.CardBody([
            # Рядок з вибором типу гітари та деревини
            dbc.Row([
                dbc.Col([
                    dbc.Label("Тип гітари", html_for="guitar-type"),
                    dcc.Dropdown(
                        id="guitar-type",
                        options=[{'label': v['name'], 'value': k} for k, v in guitar_types.items()],
                        placeholder="Оберіть тип гітари"
                    )
                ], md=6),
                
                dbc.Col([
                    dbc.Label("Деревина", html_for="wood-type"),
                    dcc.Dropdown(
                        id="wood-type",
                        options=[{'label': v['name'], 'value': k} for k, v in woods.items()],
                        placeholder="Оберіть деревину"
                    )
                ], md=6)
            ], className="mb-3"),
            
            # Рядок з характеристиками гітари
            dbc.Row([
                dbc.Col([
                    dbc.Label("Кількість струн", html_for="strings-count"),
                    dcc.Dropdown(
                        id="strings-count",
                        placeholder="Спочатку оберіть тип гітари",
                        disabled=True
                    )
                ], md=4),
                
                dbc.Col([
                    dbc.Label("Вік гітари (років)", html_for="guitar-age"),
                    dcc.Input(
                        id="guitar-age",
                        type="number",
                        min=0,
                        placeholder="Введіть вік",
                        disabled=True
                    )
                ], md=4),
                
                dbc.Col([
                    dbc.Label("Стан (0-50)", html_for="guitar-condition"),
                    dcc.Slider(
                        id="guitar-condition",
                        min=0,
                        max=50,
                        step=1,
                        value=0,
                        marks={
                            0: {'label': 'Нова', 'style': {'color': 'green'}},
                            10: {'label': 'Відмінний'},
                            20: {'label': 'Дуже хороший'},
                            30: {'label': 'Хороший'},
                            40: {'label': 'Задовільний'},
                            50: {'label': 'Поганий', 'style': {'color': 'red'}}
                        }
                    )
                ], md=4)
            ], className="mb-3"),
            
            # Рядок з кнопками
            dbc.Row([
                dbc.Col([
                    dbc.Button("Розрахувати вартість", id="calculate-btn", color="primary", className="w-100", disabled=True)
                ], md=6),
                
                dbc.Col([
                    dbc.Button("Очистити форму", id="reset-btn", color="secondary", className="w-100")
                ], md=6)
            ]),
            
            # Блоки для повідомлень та результатів
            html.Div(id="error-message", className="text-danger mt-3"),
            html.Div(id="result", className="mt-4")
        ])
    ])
], fluid="md")

# Callback для оновлення полів форми при зміні типу гітари
@app.callback(
    Output("strings-count", "options"),
    Output("strings-count", "value"),
    Output("strings-count", "disabled"),
    Output("guitar-age", "disabled"),
    Output("calculate-btn", "disabled"),
    Input("guitar-type", "value"),
    State("wood-type", "value")
)
def update_form_fields(guitar_type, wood_type):
    if not guitar_type:
        return [], None, True, True, True
    
    strings = guitar_types[guitar_type]['strings']
    options = [{'label': str(s), 'value': s} for s in strings]
    
    # Вмикаємо поля тільки якщо вибрано і тип гітари, і деревину
    fields_disabled = not wood_type
    calculate_disabled = not wood_type
    
    return options, strings[0], False, fields_disabled, calculate_disabled

# Callback для скидання форми
@app.callback(
    Output("wood-type", "value"),
    Output("guitar-age", "value"),
    Output("guitar-condition", "value"),
    Output("error-message", "children"),
    Output("result", "children"),
    Output("calculate-btn", "disabled", allow_duplicate=True),
    Input("reset-btn", "n_clicks"),
    prevent_initial_call=True
)
def reset_form(n_clicks):
    if n_clicks:
        return None, None, 0, "", "", True
    return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

# Основний callback для розрахунку вартості
@app.callback(
    Output("error-message", "children", allow_duplicate=True),
    Output("result", "children", allow_duplicate=True),
    Output("calculate-btn", "disabled", allow_duplicate=True),
    Input("calculate-btn", "n_clicks"),
    State("guitar-type", "value"),
    State("wood-type", "value"),
    State("strings-count", "value"),
    State("guitar-age", "value"),
    State("guitar-condition", "value"),
    prevent_initial_call=True
)
def calculate_price(n_clicks, guitar_type, wood_type, strings_count, age, condition):
    if not n_clicks:
        return dash.no_update, dash.no_update, dash.no_update
    
    # Валідація введених даних
    if not guitar_type:
        return "Будь ласка, оберіть тип гітари", "", True
    if not wood_type:
        return "Будь ласка, оберіть деревину", "", True
    if strings_count is None:
        return "Будь ласка, оберіть кількість струн", "", True
    if age is None:
        return "Будь ласка, введіть вік гітари", "", True
    
    max_age = guitar_types[guitar_type]['max_age']
    if max_age is not None and age > max_age:
        return f"Для цього типу гітари максимальний вік {max_age} років", "", True
    
    if age < 0:
        return "Вік не може бути від'ємним", "", True
    
    # Базовий розрахунок ціни
    base_price = guitar_types[guitar_type]['base_price']
    wood_multiplier = woods[wood_type]['multiplier']
    
    # Розрахунок бонусу за струни (з урахуванням випадку, коли min_strings == max_strings)
    min_strings = min(guitar_types[guitar_type]['strings'])
    max_strings = max(guitar_types[guitar_type]['strings'])
    
    if min_strings == max_strings:
        strings_bonus = 0  # Для гітар з фіксованою кількістю струн бонусу немає
    else:
        strings_bonus = 0.5 * (strings_count - min_strings) / (max_strings - min_strings)
    
    # Розрахунок знижок та штрафів
    age_discount = 0.01 * age
    condition_penalty = 0.01 * condition
    
    # Фінальна ціна
    price = base_price * wood_multiplier * (1 + strings_bonus) * (1 - age_discount) * (1 - condition_penalty)
    
    # Визначення текстового опису стану
    condition_name = ""
    if condition <= 10:
        condition_name = "Нова"
    elif 10 < condition <= 20:
        condition_name = "Відмінний"
    elif 20 < condition <= 30:
        condition_name = "Дуже хороший"
    elif 30 < condition <= 40:
        condition_name = "Хороший"
    else:
        condition_name = "Поганий"
    
    # Формування результату
    result = [
        html.H4("Результат оцінки:"),
        dbc.Table([
            html.Tbody([
                html.Tr([html.Td("Тип гітари:"), html.Td(guitar_types[guitar_type]['name'])]),
                html.Tr([html.Td("Деревина:"), html.Td(woods[wood_type]['name'])]),
                html.Tr([html.Td("Кількість струн:"), html.Td(str(strings_count))]),
                html.Tr([html.Td("Вік:"), html.Td(f"{age} років")]),
                html.Tr([html.Td("Стан:"), html.Td(f"{condition_name}")]),
                html.Tr([html.Td("Базова ціна:"), html.Td(f"{base_price:.2f} грн")]),
                html.Tr([html.Td("Множник деревини:"), html.Td(f"{wood_multiplier:.2f}")]),
                html.Tr([html.Td("Бонус за струни:"), html.Td(f"+{strings_bonus*100:.1f}%")]),
                html.Tr([html.Td("Знижка за вік:"), html.Td(f"-{age_discount*100:.1f}%")]),
                html.Tr([html.Td("Штраф за стан:"), html.Td(f"-{condition_penalty*100:.1f}%")]),
                html.Tr([html.Td(html.Strong("Оціночна вартість:")), 
                         html.Td(html.Strong(f"{price:.2f} грн"))], className="table-active")
            ])
        ], bordered=True, hover=True, className="mt-3")
    ]
    
    return "", result, False

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True)