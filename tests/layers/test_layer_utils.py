from neupy import layers, algorithms
from neupy.layers.utils import (create_input_variable, extract_connection,
                                preformat_layer_shape)

from base import BaseTestCase


class CountParametersTestCase(BaseTestCase):
    def test_count_parameters(self):
        connection = layers.join(
            layers.Input(10),
            layers.Sigmoid(5),
            layers.Sigmoid(2),
        )

        n_parameters = layers.count_parameters(connection)
        self.assertEqual(n_parameters, (10 * 5 + 5) + (5 * 2 + 2))

    def test_count_parameters_single_layer(self):
        hidden_layer = layers.Sigmoid(5)
        layers.join(
            layers.Input(10),
            hidden_layer,
            layers.Sigmoid(2),
        )

        n_parameters = layers.count_parameters(hidden_layer)
        self.assertEqual(n_parameters, 10 * 5 + 5)

    def test_join_empty_connection(self):
        self.assertEqual(layers.join(), None)

    def test_create_input_variable_exception(self):
        with self.assertRaises(ValueError):
            create_input_variable((1, 2, 3, 4), name='test')

    def test_connection_extraction(self):
        connection = layers.Input(2) > layers.Sigmoid(3)
        self.assertIs(extract_connection(connection), connection)

        network = algorithms.GradientDescent(connection)
        self.assertIs(extract_connection(network), connection)

        list_of_layers = [layers.Input(2), layers.Sigmoid(3)]
        actual_connection = extract_connection(list_of_layers)
        self.assertEqual(len(actual_connection), 2)
        self.assertEqual(actual_connection.input_shape, (2,))
        self.assertEqual(actual_connection.output_shape, (3,))

        with self.assertRaisesRegexp(TypeError, "Invalid input type"):
            extract_connection(object)

    def test_preformat_layer_shape(self):
        self.assertEqual((2, 3, 1), preformat_layer_shape((2, 3, 1)))
        self.assertEqual(10, preformat_layer_shape((10,)))
