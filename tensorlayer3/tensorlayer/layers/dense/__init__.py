#! /usr/bin/python
# -*- coding: utf-8 -*-
"""
TensorLayer provides rich layer implementations trailed for
various benchmarks and domain-specific problems. In addition, we also
support transparent access to native TensorFlow parameters.
For example, we provide not only layers for local response normalization, but also
layers that allow user to apply ``tf.ops.lrn`` on ``network.outputs``.
More functions can be found in `TensorFlow API <https://www.tensorflow.org/versions/master/api_docs/index.html>`__.
"""

from .base_dense import *
from .binary_dense import *
from .dorefa_dense import *
from .dropconnect import *
from .quan_dense import *
from .quan_dense_bn import *
from .ternary_dense import *

__all__ = [
    'BinaryDense',
    'Dense',
    'DorefaDense',
    'DropconnectDense',
    'TernaryDense',
    'QuanDense',
    'QuanDenseWithBN',
]
