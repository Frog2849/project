import sys
import random
import sqlite3
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout,
                             QPushButton, QLabel, QLineEdit,
                             QMessageBox, QComboBox, QHBoxLayout)


# Добавим новый класс для окна с формулами
class FormulasWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Справка: формулы')
        self.setGeometry(200, 200, 300, 200)

        layout = QVBoxLayout()

        formulas = """
        <b>Формула дискриминанта:</b><br>
        D = b² - 4ac<br><br>

        <b>Теорема Безу:</b><br>
        Остаток от деления многочлена P(x) на (x - a)<br>
        равен P(a). Если P(a) = 0, то (x - a) - множитель P(x).
        """

        label = QLabel(formulas)
        label.setStyleSheet("font-size: 14px;")
        layout.addWidget(label)

        self.setLayout(layout)


class EquationSolverApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.create_database()
        self.total_correct_solutions = self.get_total_correct_solutions()
        self.zs = 0
        self.ht = 0

    def initUI(self):
        self.setWindowTitle('Equation Solver+')
        self.setGeometry(100, 100, 400, 350)

        main_layout = QVBoxLayout()

        # Добавим верхнюю панель с кнопкой справки
        top_panel = QHBoxLayout()
        self.formula_button = QPushButton('Показать формулы', self)
        self.formula_button.clicked.connect(self.show_formulas)
        top_panel.addWidget(self.formula_button)

        main_layout.addLayout(top_panel)

        # Остальной интерфейс
        self.degree_label = QLabel('Выберите тип задачи:', self)
        main_layout.addWidget(self.degree_label)

        self.degree_combo = QComboBox(self)
        self.degree_combo.addItems([
            'Линейное (1)',
            'Квадратное (2)',
            'Кубическое (3)',
            'Задачи с параметром (4)'
        ])
        main_layout.addWidget(self.degree_combo)

        self.solve_button = QPushButton('Сгенерировать задачу', self)
        self.solve_button.clicked.connect(self.generate_equation)
        main_layout.addWidget(self.solve_button)

        self.equation_label = QLabel('', self)
        main_layout.addWidget(self.equation_label)

        self.solution_input = QLineEdit(self)
        main_layout.addWidget(self.solution_input)

        self.submit_button = QPushButton('Проверить решение', self)
        self.submit_button.clicked.connect(self.check_solution)
        main_layout.addWidget(self.submit_button)

        self.result_label = QLabel('', self)
        main_layout.addWidget(self.result_label)

        self.setLayout(main_layout)

    # Добавим метод для показа окна с формулами
    def show_formulas(self):
        self.form_window = FormulasWindow()
        self.form_window.show()

    def create_database(self):
        conn = sqlite3.connect('equation_solutions.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stats (
                id INTEGER PRIMARY KEY,
                correct_solutions INTEGER DEFAULT 0
            )
        ''')
        cursor.execute('SELECT * FROM stats')
        if cursor.fetchone() is None:
            cursor.execute('INSERT INTO stats (correct_solutions) VALUES (0)')
        conn.commit()
        conn.close()

    def update_correct_solutions(self, count):
        conn = sqlite3.connect('equation_solutions.db')
        cursor = conn.cursor()
        cursor.execute('UPDATE stats SET correct_solutions = correct_solutions + ?', (count,))
        conn.commit()
        conn.close()

    def get_total_correct_solutions(self):
        conn = sqlite3.connect('equation_solutions.db')
        cursor = conn.cursor()
        cursor.execute('SELECT correct_solutions FROM stats')
        total = cursor.fetchone()[0]
        conn.close()
        return total

    def generate_equation(self):
        task_type = self.degree_combo.currentIndex()
        self.solution_input.clear()

        if task_type == 3:  # Задачи с параметром
            k = random.randint(1, 21)
            c = k ** 2
            self.solutions_list = [2 * k, -2 * k]  # Оба правильных значения
            self.equation_label.setText(
                f"При каких значениях параметра a уравнение\n"
                f"x² + a∙x + {c} = 0 имеет ровно один корень?\n"
                f"Введите все возможные значения a через пробел:"
            )
            return

        degree = task_type + 1

        if degree == 1:
            a = random.randint(2, 10)
            b = random.randint(-20, 20)
            equation = f"{a}x + {b} = 0"
            solutions = [round((-b / a), 2)]

        elif degree == 2:
            a = random.randint(2, 10)
            b = random.randint(-20, 20)
            c = random.randint(-20, 20)
            equation = f"{a}x² + {b}x + {c} = 0"

            D = b ** 2 - 4 * a * c
            if D > 0:
                x1 = round((-b + D ** 0.5) / (2 * a), 2)
                x2 = round((-b - D ** 0.5) / (2 * a), 2)
                solutions = sorted([x1, x2])
            elif D == 0:
                x = round(-b / (2 * a), 2)
                solutions = [x]
            else:
                solutions = ["нет решений"]

        elif degree == 3:
            r = random.randint(-10, 10)
            a = random.randint(1, 10)
            b = random.randint(-20, 20)
            c = random.randint(-20, 20)
            expanded_a = a
            expanded_b = b - a * r
            expanded_c = c - b * r
            expanded_d = -c * r
            equation = f"{expanded_a}x³ + {expanded_b}x² + {expanded_c}x + {expanded_d} = 0"
            solutions = [r]
            D_quad = b**2 - 4 * a * c
            if D_quad >= 0:
                x1 = round((-b + D_quad**0.5) / (2 * a), 2)
                x2 = round((-b - D_quad**0.5) / (2 * a), 2)
                solutions.extend([x1, x2] if D_quad > 0 else [x1])
            solutions = sorted(list(set(solutions)))

        self.equation_label.setText(f"Решите: {equation}")
        self.solutions_list = solutions

    def check_solution(self):
        task_type = self.degree_combo.currentIndex()

        if task_type == 3:
            user_input = self.solution_input.text().strip()
            try:
                user_answers = list(map(float, user_input.split()))
                user_answers = [round(ans, 2) for ans in user_answers]
                correct_answers = [round(ans, 2) for ans in self.solutions_list]
                if sorted(user_answers) == sorted(correct_answers):
                    self.handle_correct_answer()
                else:
                    QMessageBox.warning(self, 'Ошибка', f'Правильные ответы: {", ".join(map(str, self.solutions_list))}')
                    self.reset_streak()
            except ValueError:
                QMessageBox.warning(self, 'Ошибка', 'Введите числа через пробел!')
                self.reset_streak()
            return

        user_input = self.solution_input.text().strip()

        if self.solutions_list == ["нет решений"]:
            if user_input.lower() == "нет решений":
                self.handle_correct_answer()
            else:
                QMessageBox.warning(self, 'Ошибка', 'Правильный ответ: нет решений')
                self.reset_streak()
            return

        try:
            user_solutions = sorted(list(map(float, user_input.split())))
            correct_solutions = sorted([float(sol) for sol in self.solutions_list])
        except ValueError:
            QMessageBox.warning(self, 'Ошибка', 'Некорректный формат ввода')
            self.reset_streak()
            return

        if user_solutions == correct_solutions:
            self.handle_correct_answer()
        else:
            QMessageBox.warning(self, 'Ошибка', f'Правильные ответы: {", ".join(map(str, self.solutions_list))}')
            self.reset_streak()

    def handle_correct_answer(self):
        self.zs += 1
        self.ht += 1
        self.update_correct_solutions(1)
        self.total_correct_solutions += 1
        QMessageBox.information(self, 'Успех', 'Правильно!')
        self.show_stats()

    def reset_streak(self):
        if self.ht > 0:
            self.ht = 0

    def show_stats(self):
        stats = (f"За сессию: {self.zs} правильных ответов\n"
                 f"Текущая серия: {self.ht}\n"
                 f"Всего решено: {self.total_correct_solutions}")
        QMessageBox.information(self, 'Статистика', stats)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = EquationSolverApp()
    ex.show()
    sys.exit(app.exec_())