import unittest
from main import calculate_price, guitar_types, woods

class TestGuitarPriceCalculation(unittest.TestCase):

    def test_valid_data_electric(self):
        result = calculate_price(
            n_clicks=1,
            guitar_type='electric',
            wood_type='mahogany',
            strings_count=6,
            age=5,
            condition=10
        )
        self.assertEqual(result[0], "")  # No error
        self.assertIn("Оціночна вартість", str(result[1]))  # Result is shown
        self.assertFalse(result[2])  # Button is not disabled

    def test_missing_guitar_type(self):
        result = calculate_price(1, None, 'mahogany', 6, 5, 10)
        self.assertEqual(result[0], "Будь ласка, оберіть тип гітари")

    def test_invalid_string_count_ukulele(self):
        result = calculate_price(1, 'ukulele', 'spruce', 4, 2, 10)
        self.assertIn("Оціночна вартість", str(result[1]))

    def test_age_exceeds_limit(self):
        result = calculate_price(1, 'bass', 'oak', 4, 100, 10)
        self.assertIn("максимальний вік", result[0])

    def test_negative_age(self):
        result = calculate_price(1, 'electric', 'maple', 6, -5, 10)
        self.assertEqual(result[0], "Вік не може бути від'ємним")

    def test_price_exact_formula(self):
        # Manual expected price calculation:
        base = 10000  # electric
        wood_multiplier = 1.1  # maple
        bonus = 0.0  # for 6 strings
        age_discount = 0.01 * 10
        condition_penalty = 0.01 * 10
        expected_price = base * wood_multiplier * (1 + bonus) * (1 - age_discount) * (1 - condition_penalty)

        result = calculate_price(1, 'electric', 'maple', 6, 10, 10)
        self.assertIn(f"{expected_price:.2f}", str(result[1]))

if __name__ == '__main__':
    unittest.main()
