import unittest
import platform
import tempfile

import dill
import numpy as np
from sklearn import datasets, preprocessing
from neupy import algorithms

from base import BaseTestCase


class StorageTestCase(BaseTestCase):
    def test_simple_storage(self):
        bpnet = algorithms.GradientDescent((2, 3, 1), step=0.25, verbose=False)
        data, target = datasets.make_regression(n_features=2, n_targets=1)

        data = preprocessing.MinMaxScaler().fit_transform(data)
        target_scaler = preprocessing.MinMaxScaler()
        target = target_scaler.fit_transform(target.reshape(-1, 1))

        with tempfile.NamedTemporaryFile() as temp:
            test_layer_weights = bpnet.input_layer.weight.get_value().copy()
            dill.dump(bpnet, temp)
            temp.file.seek(0)

            restored_bpnet = dill.load(temp)
            temp.file.seek(0)
            layers_sizes = [layer.size for layer in restored_bpnet.all_layers]

            self.assertEqual(0.25, restored_bpnet.step)
            self.assertEqual([2, 3, 1], layers_sizes)
            np.testing.assert_array_equal(
                test_layer_weights,
                restored_bpnet.input_layer.weight.get_value()
            )

            bpnet.train(data, target, epochs=5)
            real_bpnet_error = bpnet.prediction_error(data, target)
            updated_input_weight = bpnet.input_layer.weight.get_value().copy()

            dill.dump(bpnet, temp)
            temp.file.seek(0)

            restored_bpnet2 = dill.load(temp)
            temp.file.seek(0)
            restored_bpnet_error = restored_bpnet2.prediction_error(
                data, target
            )

            np.testing.assert_array_equal(
                updated_input_weight,
                restored_bpnet2.input_layer.weight.get_value()
            )

            # Error must be big, because we didn't normalize data
            self.assertEqual(real_bpnet_error, restored_bpnet_error)

    def test_dynamic_classes(self):
        test_classes = {
            algorithms.GradientDescent: {},
            # algorithms.MinibatchGradientDescent: {'batch_size': 10},
            # algorithms.Momentum: {'momentum': 0.5},
            # algorithms.RPROP: {'maxstep': 1},
            # algorithms.IRPROPPlus: {'maxstep': 1},
            # algorithms.ConjugateGradient: {
            #     'update_function': 'fletcher_reeves'
            # },
            # algorithms.QuasiNewton: {'update_function': 'bfgs'},
            # algorithms.HessianDiagonal: {'min_eigval': 1e-5},
            # algorithms.LevenbergMarquardt: {'mu': 0.01},
        }

        for algorithm_class, algorithm_params in test_classes.items():
            optimization_classes = [algorithms.WeightDecay,
                                    algorithms.SearchThenConverge]

            bpnet = algorithm_class(
                (3, 5, 1),
                addons=optimization_classes,
                verbose=False,
                **algorithm_params
            )
            data, target = datasets.make_regression(n_features=3, n_targets=1)

            data = preprocessing.MinMaxScaler().fit_transform(data)
            target_scaler = preprocessing.MinMaxScaler()
            target = target_scaler.fit_transform(target.reshape(-1, 1))

            with tempfile.NamedTemporaryFile() as temp:
                valid_class_name = bpnet.__class__.__name__
                dill.dump(bpnet, temp)
                temp.file.seek(0)

                restored_bpnet = dill.load(temp)
                restored_class_name = restored_bpnet.__class__.__name__
                temp.file.seek(0)

                self.assertEqual(valid_class_name, restored_class_name)
                self.assertEqual(optimization_classes,
                                 restored_bpnet.addons)

                bpnet.train(data, target, epochs=10)
                real_bpnet_error = bpnet.prediction_error(data, target)
                updated_input_weight = (
                    bpnet.input_layer.weight.get_value().copy()
                )

                dill.dump(bpnet, temp)
                temp.file.seek(0)

                restored_bpnet2 = dill.load(temp)
                temp.file.seek(0)
                restored_bpnet_error = restored_bpnet2.prediction_error(
                    data, target
                )

                np.testing.assert_array_equal(
                    updated_input_weight,
                    restored_bpnet2.input_layer.weight.get_value()
                )
                # Error must be big, because we didn't normalize data
                self.assertEqual(real_bpnet_error, restored_bpnet_error)
