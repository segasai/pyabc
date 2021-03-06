import pytest
from pyabc.populationstrategy import (AdaptivePopulationStrategy,
                                      ConstantPopulationStrategy,
                                      PopulationStrategy)
from pyabc.transition import MultivariateNormalTransition
import pandas as pd
import scipy as sp


def Adaptive():
    return AdaptivePopulationStrategy(100)


def Constant():
    return ConstantPopulationStrategy(100)


@pytest.fixture(params=[Adaptive, Constant],
                ids=["Adaptive", "Constant"])
def population_strategy(request):
    return request.param()


def test_adapt_single_model(population_strategy: PopulationStrategy):
    n = 10
    df = pd.DataFrame([{"s": sp.rand()} for _ in range(n)])
    w = sp.ones(n) / n
    kernel = MultivariateNormalTransition()
    kernel.fit(df, w)

    population_strategy.adapt_population_size([kernel], sp.array([1.]))
    assert population_strategy.nr_particles > 0


def test_adapt_two_models(population_strategy: PopulationStrategy):
    n = 10
    kernels = []
    for _ in range(2):
        df = pd.DataFrame([{"s": sp.rand()} for _ in range(n)])
        w = sp.ones(n) / n
        kernel = MultivariateNormalTransition()
        kernel.fit(df, w)
        kernels.append(kernel)

    population_strategy.adapt_population_size(kernels, sp.array([.7, .2]))
    assert population_strategy.nr_particles > 0


def test_no_parameters(population_strategy: PopulationStrategy):
    n = 10
    df = pd.DataFrame(index=list(range(n)))
    w = sp.ones(n) / n

    kernels = []
    for _ in range(2):
        kernel = MultivariateNormalTransition()
        kernel.fit(df, w)
        kernels.append(kernel)

    population_strategy.adapt_population_size(kernels, sp.array([.7, .3]))
    assert population_strategy.nr_particles > 0


def test_one_with_one_without_parameters(population_strategy:
                                         PopulationStrategy):
    n = 10
    kernels = []

    df_without = pd.DataFrame(index=list(range(n)))
    w_without = sp.ones(n) / n
    kernel_without = MultivariateNormalTransition()
    kernel_without.fit(df_without, w_without)
    kernels.append(kernel_without)

    df_with = pd.DataFrame([{"s": sp.rand()} for _ in range(n)])
    w_with = sp.ones(n) / n
    kernel_with = MultivariateNormalTransition()
    kernel_with.fit(df_with, w_with)
    kernels.append(kernel_with)

    population_strategy.adapt_population_size(kernels, sp.array([.7, .3]))
    assert population_strategy.nr_particles > 0


def test_transitions_not_modified(population_strategy: PopulationStrategy):
    n = 10
    kernels = []
    test_points = pd.DataFrame([{"s": sp.rand()} for _ in range(n)])

    for _ in range(2):
        df = pd.DataFrame([{"s": sp.rand()} for _ in range(n)])
        w = sp.ones(n) / n
        kernel = MultivariateNormalTransition()
        kernel.fit(df, w)
        kernels.append(kernel)

    test_weights = [k.pdf(test_points) for k in kernels]

    population_strategy.adapt_population_size(kernels, sp.array([.7, .2]))

    after_adaptation_weights = [k.pdf(test_points) for k in kernels]

    same = all([(k1 == k2).all()
                for k1, k2 in zip(test_weights, after_adaptation_weights)])
    err_msg = (f"Population strategy {population_strategy}"
               " modified the transitions")

    assert same, err_msg
