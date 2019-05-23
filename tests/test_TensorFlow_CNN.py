# Run from home directory with python -m pytest tests
import shutil
import pytest
import torch
import random
import numpy as np
import torch.nn as nn
from nn_builder.tensorflow.CNN import CNN
from tensorflow.keras.layers import Dense, Flatten, Conv2D, Concatenate, BatchNormalization, MaxPool2D, AveragePooling2D


N = 250
X = np.random.random((N, 1, 5, 5))
X[0:125, 0, 3, 3] += 20.0
y = X[:, 0, 3, 3] > 5.0

def test_user_hidden_layers_input_rejections():
    """Tests whether network rejects invalid hidden_layers inputted from user"""
    inputs_that_should_fail = [ ('maxpool', 3, 3, 3) , ['maxpool', 33, 22, 33], [['a']], [[222, 222, 222, 222]], [["conv", 2, 2, -1]], [["conv", 2, 2]], [["conv", 2, 2, 55, 999, 33]],
                                [["maxpool", 33, 33]], [["maxpool", -1, 33]], [["maxpool", 33]], [["maxpoolX", 1, 33]],
                                [["cosnv", 2, 2]], [["avgpool", 33, 33, 333, 99]], [["avgpool", -1, 33]], [["avgpool", 33]], [["avgpoolX", 1, 33]],
                                [["adaptivemaxpool", 33, 33, 333, 33]], [["adaptivemaxpool", 2]], [["adaptivemaxpool", 33]], [["adaptivemaxpoolX"]],
                                [["adaptiveavgpool", 33, 33, 333, 11]], [["adaptiveavgpool", 2]], [["adaptiveavgpool", 33]],
                                [["adaptiveavgpoolX"]], [["linear", 40, -2]], [["lineafr", 40, 2]]]
    for input in inputs_that_should_fail:
        print(input)
        with pytest.raises(AssertionError):
            CNN(layers_info=input, hidden_activations="relu",
                output_activation="relu")

def test_user_hidden_layers_input_acceptances():
    """Tests whether network rejects invalid hidden_layers inputted from user"""
    inputs_that_should_work = [[["conv", 2, 2, 3331, "VALID"]], [["CONV", 2, 2, 3331, "SAME"]], [["ConV", 2, 2, 3331, "valid"]],
                               [["maxpool", 2, 2, "same"]], [["MAXPOOL", 2, 2, "Valid"]], [["MaXpOOL", 2, 2, "SAme"]],
                               [["avgpool", 2, 2, "saME"]], [["AVGPOOL", 2, 2, "vaLID"]], [["avGpOOL", 2, 2, "same"]],
                               [["linear", 40]], [["lineaR", 2]], [["LINEAR", 2]]]

    for ix, input in enumerate(inputs_that_should_work):
        input.append(["linear", 5])
        CNN(layers_info=input, hidden_activations="relu",
            output_activation="relu")

def test_hidden_layers_created_correctly():
    """Tests that create_hidden_layers works correctly"""
    layers = [["conv", 2, 4, 3, "same"], ["maxpool", 3, 4, "vaLID"], ["avgpool", 32, 42, "vaLID"],
               ["linear", 22], ["linear", 2222], ["linear", 5]]

    cnn = CNN(layers_info=layers, hidden_activations="relu",
              output_activation="relu")

    assert type(cnn.hidden_layers[0]) == Conv2D
    assert cnn.hidden_layers[0].filters == 2
    assert cnn.hidden_layers[0].kernel_size == (4, 4)
    assert cnn.hidden_layers[0].strides == (3, 3)
    assert cnn.hidden_layers[0].padding == "same"

    assert type(cnn.hidden_layers[1]) == MaxPool2D
    assert cnn.hidden_layers[1].pool_size == (3, 3)
    assert cnn.hidden_layers[1].strides == (4, 4)
    assert cnn.hidden_layers[1].padding == "valid"

    assert type(cnn.hidden_layers[2]) == AveragePooling2D
    assert cnn.hidden_layers[2].pool_size == (32, 32)
    assert cnn.hidden_layers[2].strides == (42, 42)
    assert cnn.hidden_layers[2].padding == "valid"

    assert type(cnn.hidden_layers[3]) == Dense
    assert cnn.hidden_layers[3].units == 22

    assert type(cnn.hidden_layers[4]) == Dense
    assert cnn.hidden_layers[4].units == 2222

    assert type(cnn.output_layers[0]) == Dense
    assert cnn.output_layers[0].units == 5


def test_output_layers_created_correctly():
    """Tests that create_output_layers works correctly"""
    layers = [["conv", 2, 4, 3, "valid"], ["maxpool", 3, 4, "same"], ["avgpool", 32, 42, "valid"],
              ["linear", 22], ["linear", 2222], ["linear", 2]]

    cnn = CNN(layers_info=layers, hidden_activations="relu", output_activation="relu")

    assert cnn.output_layers[0].units == 2

    layers = [["conv", 2, 4, 3,"valid"], ["maxpool", 3, 4, "same"], ["avgpool", 32, 42, "same"], ["linear", 7]]

    cnn = CNN(layers_info=layers, hidden_activations="relu",
              output_activation="relu")

    assert cnn.output_layers[0].units == 7

    layers = [["conv", 5, 4, 3, "valid"], ["maxpool", 3, 4, "valid"], ["avgpool", 32, 42, "valid"], ["linear", 6]]


    cnn = CNN( layers_info=layers, hidden_activations="relu",
              output_activation="relu")

    assert cnn.output_layers[0].units == 6

    layers = [["conv", 5, 4, 3, "valid"], ["maxpool", 3, 4, "valid"], ["avgpool", 32, 42, "valid"],
              [["linear", 6], ["linear", 22]]]

    cnn = CNN(layers_info=layers, hidden_activations="relu",
              output_activation=["softmax", None])


    assert cnn.output_layers[0].units == 6
    assert cnn.output_layers[1].units == 22

def test_output_dim_user_input():
    """Tests whether network rejects an invalid output_dim input from user"""
    inputs_that_should_fail = [-1, "aa", ["dd"], [2], 0, 2.5, {2}]
    for input_value in inputs_that_should_fail:
        with pytest.raises(AssertionError):
            CNN(layers_info=[2, input_value], hidden_activations="relu",  output_activation="relu")
        with pytest.raises(AssertionError):
            CNN(layers_info=input_value, hidden_activations="relu", output_activation="relu")

def test_activations_user_input():
    """Tests whether network rejects an invalid hidden_activations or output_activation from user"""
    inputs_that_should_fail = [-1, "aa", ["dd"], [2], 0, 2.5, {2}, "Xavier_"]
    for input_value in inputs_that_should_fail:
        with pytest.raises(AssertionError):
            CNN(layers_info=[["conv", 2, 2, 3331, 2]], hidden_activations=input_value,
                output_activation="relu")
            CNN(layers_info=[["conv", 2, 2, 3331, 2]], hidden_activations="relu",
                output_activation=input_value)

def test_initialiser_user_input():
    """Tests whether network rejects an invalid initialiser from user"""
    inputs_that_should_fail = [-1, "aa", ["dd"], [2], 0, 2.5, {2}, "Xavier_"]
    for input_value in inputs_that_should_fail:
        with pytest.raises(AssertionError):
            CNN(layers_info=[["conv", 2, 2, 3331, 2]], hidden_activations="relu",
                output_activation="relu", initialiser=input_value)

        CNN(layers_info=[["conv", 2, 2, 3331, 2], ["linear", 3]], hidden_activations="relu",
            output_activation="relu", initialiser="xavier")

def test_batch_norm_layers():
    """Tests whether batch_norm_layers method works correctly"""
    layers = [["conv", 2, 4, 3, 2], ["maxpool", 3, 4, 2], ["adaptivemaxpool", 3, 34], ["linear", 5]]
    cnn = CNN(layers_info=layers, hidden_activations="relu",
            output_activation="relu", initialiser="xavier", batch_norm=False)

    layers = [["conv", 2, 4, 3, 2], ["maxpool", 3, 4, 2], ["adaptivemaxpool", 3, 34], ["linear", 5]]
    cnn = CNN(layers_info=layers, hidden_activations="relu",
              output_activation="relu", initialiser="xavier", batch_norm=True)
    assert len(cnn.batch_norm_layers) == 1
    assert cnn.batch_norm_layers[0].num_features == 2


    layers = [["conv", 2, 4, 3, 2], ["maxpool", 3, 4, 2], ["conv", 12, 4, 3, 2], ["adaptivemaxpool", 3, 34], ["linear", 22], ["linear", 55]]
    cnn = CNN(layers_info=layers, hidden_activations="relu",
              output_activation="relu", initialiser="xavier", batch_norm=True)
    assert len(cnn.batch_norm_layers) == 3
    assert cnn.batch_norm_layers[0].num_features == 2
    assert cnn.batch_norm_layers[1].num_features == 12
    assert cnn.batch_norm_layers[2].num_features == 22

def test_linear_layers_acceptance():
    """Tests that only accepts linear layers of correct shape"""
    layers_that_shouldnt_work = [[["linear", 2, 5]], [["linear", 2, 5, 5]], [["linear"]], [["linear", 2], ["linear", 5, 4]],
                                 ["linear", 0], ["linear", -5]]
    for layers in layers_that_shouldnt_work:
        with pytest.raises(AssertionError):
            cnn = CNN(layers_info=layers, hidden_activations="relu",
                      output_activation="relu", initialiser="xavier", batch_norm=True)
    layers_that_should_work = [[["linear", 44], ["linear", 2]], [["linear", 22]]]
    for layer in layers_that_should_work:
        assert CNN(layers_info=layer, hidden_activations="relu",
                      output_activation="relu", initialiser="xavier", batch_norm=True)

def test_linear_layers_only_come_at_end():
    """Tests that it throws an error if user tries to provide list of hidden layers that include linear layers where they
    don't only come at the end"""
    layers = [["conv", 2, 4, 3, 2], ["linear", 55], ["maxpool", 3, 4, 2], ["adaptivemaxpool", 3, 34]]
    with pytest.raises(AssertionError):
        cnn = CNN(layers_info=layers, hidden_activations="relu",
                  output_activation="relu", initialiser="xavier", batch_norm=True)

    layers = [["conv", 2, 4, 3, 2], ["linear", 55]]
    assert CNN(layers_info=layers, hidden_activations="relu",
                      output_activation="relu", initialiser="xavier", batch_norm=True)

    layers = [["conv", 2, 4, 3, 2], ["linear", 55], ["linear", 55], ["linear", 55]]
    assert CNN(layers_info=layers, hidden_activations="relu",
               output_activation="relu", initialiser="xavier", batch_norm=True)

def test_output_activation():
    """Tests whether network outputs data that has gone through correct activation function"""
    RANDOM_ITERATIONS = 20
    input_dim = (5, 100, 100)
    for _ in range(RANDOM_ITERATIONS):
        data = torch.randn((1, *input_dim))
        CNN_instance = CNN(layers_info=[["conv", 2, 2, 1, 2], ["adaptivemaxpool", 2, 2], ["linear", 50]],
                           hidden_activations="relu",
                           output_activation="relu", initialiser="xavier")
        out = CNN_instance.forward(data)
        assert all(out.squeeze() >= 0)

        CNN_instance = CNN(layers_info=[["conv", 2, 20, 1, 0], ["linear", 5]],
                           hidden_activations="relu",
                           output_activation="relu", initialiser="xavier")
        out = CNN_instance.forward(data)
        assert all(out.squeeze() >= 0)

        CNN_instance = CNN(layers_info=[["conv", 5, 20, 1, 0], ["linear", 5]],
                           hidden_activations="relu",
                           output_activation="relu", initialiser="xavier")
        out = CNN_instance.forward(data)
        assert all(out.squeeze() >= 0)

        CNN_instance = CNN(layers_info=[["conv", 5, 20, 1, 0], ["linear",  22]],
                           hidden_activations="relu",
                           output_activation="sigmoid", initialiser="xavier")
        out = CNN_instance.forward(data)
        assert all(out.squeeze() >= 0)
        assert all(out.squeeze() <= 1)
        assert round(torch.sum(out.squeeze()).item(), 3) != 1.0

        CNN_instance = CNN(layers_info=[["conv", 2, 2, 1, 2], ["adaptivemaxpool", 2, 2], ["linear", 5]],
                           hidden_activations="relu",
                           output_activation="softmax", initialiser="xavier")
        out = CNN_instance.forward(data)
        assert all(out.squeeze() >= 0)
        assert all(out.squeeze() <= 1)
        assert round(torch.sum(out.squeeze()).item(), 3) == 1.0


        CNN_instance = CNN(layers_info=[["conv", 2, 2, 1, 2], ["adaptivemaxpool", 2, 2], ["linear", 5]],
                           hidden_activations="relu",
                           initialiser="xavier")
        out = CNN_instance.forward(data)
        assert not all(out.squeeze() >= 0)
        assert not round(torch.sum(out.squeeze()).item(), 3) == 1.0

def test_y_range():
    """Tests whether setting a y range works correctly"""
    for _ in range(100):
        val1 = random.random() - 3.0*random.random()
        val2 = random.random() + 2.0*random.random()
        lower_bound = min(val1, val2)
        upper_bound = max(val1, val2)
        CNN_instance = CNN(layers_info=[["conv", 2, 2, 1, 2], ["adaptivemaxpool", 2, 2], ["linear", 5]],
                           hidden_activations="relu", y_range=(lower_bound, upper_bound),
                           initialiser="xavier")
        random_data = torch.randn((10, 1, 20, 20))
        out = CNN_instance.forward(random_data)
        assert torch.sum(out > lower_bound).item() == 10*5, "lower {} vs. {} ".format(lower_bound, out)
        assert torch.sum(out < upper_bound).item() == 10*5, "upper {} vs. {} ".format(upper_bound, out)

def test_deals_with_None_activation():
    """Tests whether is able to handle user inputting None as output activation"""
    assert CNN(layers_info=[["conv", 2, 2, 1, 2], ["adaptivemaxpool", 2, 2], ["linear", 5]],
                           hidden_activations="relu", output_activation=None,
                           initialiser="xavier")

def test_check_input_data_into_forward_once():
    """Tests that check_input_data_into_forward_once method only runs once"""
    CNN_instance = CNN(layers_info=[["conv", 2, 2, 1, 2], ["adaptivemaxpool", 2, 2], ["linear", 6]],
                       hidden_activations="relu",
                       output_activation="relu", initialiser="xavier")

    data_not_to_throw_error = torch.randn((1, 4, 2, 5))
    data_to_throw_error = torch.randn((1, 2, 20, 20))

    with pytest.raises(AssertionError):
        CNN_instance.forward(data_to_throw_error)
    with pytest.raises(RuntimeError):
        CNN_instance.forward(data_not_to_throw_error)
        CNN_instance.forward(data_to_throw_error)

def test_y_range_user_input():
    """Tests whether network rejects invalid y_range inputs"""
    invalid_y_range_inputs = [ (4, 1), (2, 4, 8), [2, 4], (np.array(2.0), 6.9)]
    for y_range_value in invalid_y_range_inputs:
        with pytest.raises(AssertionError):
            print(y_range_value)
            CNN_instance = CNN(layers_info=[["conv", 2, 2, 1, 2], ["adaptivemaxpool", 2, 2]],
                           hidden_activations="relu", y_range=y_range_value,
                           initialiser="xavier")

def test_model_trains():
    """Tests whether a small range of networks can solve a simple task"""
    for output_activation in ["sigmoid", "None"]:
        CNN_instance = CNN(layers_info=[["conv", 25, 5, 1, 0], ["adaptivemaxpool", 1, 1], ["linear", 1]],
                           hidden_activations="relu", output_activation=output_activation,
                           initialiser="xavier")
        assert solves_simple_problem(X, y, CNN_instance)

    z = X[:, 0:1, 3:4, 3:4] > 5.0
    z =  torch.cat([z ==1, z==0], dim=1).float()
    z = z.squeeze(-1).squeeze(-1)
    CNN_instance = CNN(layers_info=[["conv", 25, 5, 1, 0], ["linear", 2]],
                           hidden_activations="relu", output_activation="softmax", dropout=0.01,
                           initialiser="xavier")
    assert solves_simple_problem(X, z, CNN_instance)

    CNN_instance = CNN(layers_info=[["conv", 25, 5, 1, 0], ["linear", 1]],
                       hidden_activations="relu", output_activation=None,
                       initialiser="xavier")
    assert solves_simple_problem(X, y, CNN_instance)

    CNN_instance = CNN(layers_info=[["conv", 25, 5, 1, 0], ["linear", 1]],
                       hidden_activations="relu", output_activation=None,
                       initialiser="xavier", batch_norm=True)
    assert solves_simple_problem(X, y, CNN_instance)

    CNN_instance = CNN(layers_info=[["conv", 25, 5, 1, 0], ["maxpool", 1, 1, 0], ["linear", 1]],
                       hidden_activations="relu", output_activation=None,
                       initialiser="xavier")
    assert solves_simple_problem(X, y, CNN_instance)

    CNN_instance = CNN(layers_info=[["conv", 25, 5, 1, 0], ["avgpool", 1, 1, 0], ["linear", 1]],
                       hidden_activations="relu", output_activation=None,
                       initialiser="xavier")
    assert solves_simple_problem(X, y, CNN_instance)

    CNN_instance = CNN(layers_info=[["conv", 5, 3, 1, 0], ["adaptivemaxpool", 2, 2], ["linear", 1]],
                       hidden_activations="relu", output_activation=None,
                       initialiser="xavier")
    assert solves_simple_problem(X, y, CNN_instance)

    CNN_instance = CNN(layers_info=[["conv", 5, 3, 1, 0], ["adaptiveavgpool", 2, 2], ["linear", 1]],
                       hidden_activations="relu", output_activation=None,
                       initialiser="xavier")
    assert solves_simple_problem(X, y, CNN_instance)

def test_model_trains_linear_layer():
    """Tests whether a small range of networks can solve a simple task"""
    CNN_instance = CNN(layers_info=[["conv", 5, 3, 1, 0], ["linear", 5], ["linear", 5], ["linear", 1]],
                       input_dim=(1, 5, 5),
                       hidden_activations="relu", output_activation="sigmoid",
                       initialiser="xavier")
    assert solves_simple_problem(X, y, CNN_instance)

    CNN_instance = CNN(layers_info=[["linear", 5], ["linear", 5], ["linear", 1]],
                       hidden_activations="relu", output_activation="sigmoid",
                       initialiser="xavier")
    assert solves_simple_problem(X, y, CNN_instance)

def test_max_pool_working():
    """Tests whether max pool layers work properly"""
    N = 250
    X = torch.randn((N, 1, 8, 8))
    X[0:125, 0, 3, 3] = 999.99
    CNN_instance = CNN(layers_info=[["maxpool", 2, 2, 0], ["maxpool", 2, 2, 0], ["maxpool", 2, 2, 0], ["linear", 1]],
                       hidden_activations="relu",
                       initialiser="xavier")
    assert CNN_instance(X).shape == (N, 1)

def test_dropout():
    """Tests whether dropout layer reads in probability correctly"""
    CNN_instance = CNN(layers_info=[["conv", 25, 5, 1, 0], ["adaptivemaxpool", 1, 1], ["linear", 1]],
                           hidden_activations="relu", output_activation="sigmoid", dropout=0.9999,
                           initialiser="xavier")
    assert CNN_instance.dropout_layer.p == 0.9999
    assert not solves_simple_problem(X, y, CNN_instance)
    CNN_instance = CNN(layers_info=[["conv", 25, 5, 1, 0], ["adaptivemaxpool", 1, 1], ["linear", 1]],
                           hidden_activations="relu", output_activation=None, dropout=0.0000001,
                           initialiser="xavier")
    assert CNN_instance.dropout_layer.p == 0.0000001
    assert solves_simple_problem(X, y, CNN_instance)


def solves_simple_problem(X, y, nn_instance):
    """Checks if a given network is able to solve a simple problem"""
    optimizer = optim.Adam(nn_instance.parameters(), lr=0.15)
    for ix in range(800):
        out = nn_instance.forward(X)
        loss = torch.sum((out.squeeze() - y) ** 2) / N
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
    print("LOSS ", loss)
    return loss < 0.1

def test_MNIST_progress():
    """Tests that network made using CNN module can make progress on MNIST"""
    batch_size = 128
    train_loader = torch.utils.data.DataLoader(
        datasets.MNIST(root="input/", train=True, download=True,
                       transform=transforms.Compose([
                           transforms.ToTensor(),
                           transforms.Normalize((0.1307,), (0.3081,))
                       ])),
        batch_size=batch_size, shuffle=True)

    cnn = CNN(layers_info=[["conv", 20, 5, 1, 0],
                                  ["maxpool", 2, 2, 0],
                                  ["conv", 50, 5, 1, 0],
                                  ["maxpool", 2, 2, 0],
                                  ["linear", 500], ["linear", 10]], hidden_activations="relu",
              output_activation="softmax", initialiser="xavier")

    loss_fn = nn.CrossEntropyLoss()
    optimizer = optim.Adam(cnn.parameters(), lr=0.001)

    ix = 0
    accuracies = []
    for data, target in train_loader:
        ix += 1

        output = cnn(data)
        loss = loss_fn(output, target)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        pred = output.argmax(dim=1, keepdim=True)  # get the index of the max log-probability
        correct = pred.eq(target.view_as(pred)).sum().item()
        print("Accuracy {}".format(correct / batch_size))
        accuracies.append(correct / batch_size)

        if ix > 200:
            break

    shutil.rmtree("input/", ignore_errors=False, onerror=None)
    assert accuracies[-1] > 0.7, "Accuracy not good enough {}".format(accuracies[-1])


def test_all_activations_work():
    """Tests that all activations get accepted"""
    nn_instance = CNN(layers_info=[["conv", 25, 5, 1, 0], ["adaptivemaxpool", 1, 1], ["linear", 1]],
                                   dropout=0.0000001,
                                   initialiser="xavier")
    for key in nn_instance.str_to_activations_converter.keys():
        assert CNN(layers_info=[["conv", 25, 5, 1, 0], ["adaptivemaxpool", 1, 1], ["linear", 1]],
                                   hidden_activations=key, output_activation=key, dropout=0.0000001,
                                   initialiser="xavier")

def test_all_initialisers_work():
    """Tests that all initialisers get accepted"""
    nn_instance = CNN(layers_info=[["conv", 25, 5, 1, 0], ["adaptivemaxpool", 1, 1], ["linear", 1]],
                                   dropout=0.0000001,
                                   initialiser="xavier")
    for key in nn_instance.str_to_initialiser_converter.keys():
        assert CNN(layers_info=[["conv", 25, 5, 1, 0], ["adaptivemaxpool", 1, 1], ["linear", 1]],
                                    dropout=0.0000001,
                                   initialiser=key)



#
#
# def test_works_on_MNIST():
#
#     class MyModel(Model):
#         def __init__(self):
#             super(MyModel, self).__init__()
#             self.layers_custom = self.create_layers()
#
#         def create_layers(self):
#             layers = [Dense(128, activation='relu'), Dense(10, activation='softmax')]
#
#             return layers
#
#         def call(self, x):
#             x = tf.keras.layers.Flatten(input_shape=(28, 28))(x)
#             for layer in self.layers_custom:
#                 x = layer(x)
#             return x
#
#     model = MyModel()
#
#     mnist = tf.keras.datasets.mnist
#
#     (x_train, y_train), (x_test, y_test) = mnist.load_data()
#     x_train, x_test = x_train / 255.0, x_test / 255.0
#
#     # model = tf.keras.models.Sequential([
#     #   tf.keras.layers.Flatten(input_shape=(28, 28)),
#     #   tf.keras.layers.Dense(128, activation='relu'),
#     #   tf.keras.layers.Dropout(0.2),
#     #   tf.keras.layers.Dense(10, activation='softmax')
#     # ])
#
#
#     model.compile(optimizer='adam',
#                   loss='sparse_categorical_crossentropy',
#                   metrics=['accuracy'])
#
#     model.fit(x_train, y_train, epochs=5)
#
#     model.evaluate(x_test, y_test)
#
#     results = model.evaluate(x_test, y_test)
#     assert results[1] > 0.9