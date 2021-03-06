#! /usr/bin/python
# -*- coding: utf-8 -*-

import paddle as pd
import paddle.nn.functional as F
import numpy as np
import paddle.fluid as fluid
from paddle.nn import initializer as I
from paddle.fluid.layers.utils import map_structure, flatten, pack_sequence_as
from paddle.fluid.data_feeder import convert_dtype
from paddle.fluid.dygraph import Layer


def padding_format(padding):
    """
    Checks that the padding format correspond format.

    Parameters
    ----------
    padding : str
        Must be one of the following:"same", "SAME", "VALID", "valid"

    Returns
    -------
        str "SAME" or "VALID"
    """

    if padding in ["SAME", "same"]:
        padding = "SAME"
    elif padding in ["VALID", "valid"]:
        padding = "VALID"
    elif padding == None:
        padding = None
    else:
        raise Exception("Unsupported padding: " + str(padding))
    return padding


def preprocess_1d_format(data_format, padding):
    """
    Checks that the 1-D dataformat format correspond format.

    Parameters
    ----------
    data_format : str
        Must be one of the following:"channels_last","NWC","NCW","channels_first"
    padding : str
        Must be one of the following:"same","valid","SAME","VALID"

    Returns
    -------
        str "NWC" or "NCW" and "SAME" or "VALID"
    """

    if data_format in ["channels_last", "NWC", "NLC"]:
        data_format = "NLC"
    elif data_format in ["channels_first", "NCW", "NCL"]:
        data_format = "NCL"
    elif data_format == None:
        data_format = None
    else:
        raise Exception("Unsupported data format: " + str(data_format))
    padding = padding_format(padding)
    return data_format, padding


def preprocess_2d_format(data_format, padding):
    """
    Checks that the 2-D dataformat format correspond format.

    Parameters
    ----------
    data_format : str
        Must be one of the following:"channels_last","NHWC","NCHW","channels_first"
    padding : str
        Must be one of the following:"same","valid","SAME","VALID"

    Returns
    -------
        str "NHWC" or "NCHW" and "SAME" or "VALID"
    """

    if data_format in ["channels_last", "NHWC", "nhwc"]:
        data_format = "NHWC"
    elif data_format in ["channels_first", "NCHW", "nchw"]:
        data_format = "NCHW"
    elif data_format == None:
        data_format = None
    else:
        raise Exception("Unsupported data format: " + str(data_format))
    padding = padding_format(padding)
    return data_format, padding


def preprocess_3d_format(data_format, padding):
    """
    Checks that the 3-D dataformat format correspond format.

    Parameters
    ----------
    data_format : str
        Must be one of the following:"channels_last","NDHWC","NCDHW","channels_first"
    padding : str
        Must be one of the following:"same","valid","SAME","VALID"

    Returns
    -------
        str "NDHWC" or "NCDHW" and "SAME" or "VALID"
    """

    if data_format in ['channels_last', 'NDHWC']:
        data_format = 'NDHWC'
    elif data_format in ['channels_first', 'NCDHW']:
        data_format = 'NCDHW'
    elif data_format == None:
        data_format = None
    else:
        raise Exception("Unsupported data format: " + str(data_format))
    padding = padding_format(padding)
    return data_format, padding


def nchw_to_nhwc(x):
    """
    Channels first to channels last

    Parameters
    ----------
    x : tensor
        channels first tensor data

    Returns
    -------
        channels last tensor data
    """

    if len(x.shape) == 3:
        x = pd.transpose(x, (0, 2, 1))
    elif len(x.shape) == 4:
        x = pd.transpose(x, (0, 2, 3, 1))
    elif len(x.shape) == 5:
        x = pd.transpose(x, (0, 2, 3, 4, 1))
    else:
        raise Exception("Unsupported dimensions")
    return x


def nhwc_to_nchw(x):
    """
    Channles last to channels first

    Parameters
    ----------
    x : tensor
        channels last tensor data

    Returns
    -------
        channels first tensor data
    """

    if len(x.shape) == 3:
        x = pd.transpose(x, (0, 2, 1))
    elif len(x.shape) == 4:
        x = pd.transpose(x, (0, 3, 1, 2))
    elif len(x.shape) == 5:
        x = pd.transpose(x, (0, 4, 1, 2, 3))
    else:
        raise Exception("Unsupported dimensions")
    return x


class ReLU(object):

    def __init__(self):
        pass

    def __call__(self, x):
        return F.relu(x)


def relu(x):
    """
    Computes rectified linear: max(features, 0).

    Parameters
    ----------
    x : tensor
        Must be one of the following types: float32, float64, int32, uint8, int16,
        int8, int64, bfloat16, uint16, half, uint32, uint64, qint8.

    Returns
    -------
        A Tensor. Has the same type as features.
    """
    return F.relu(x)


class ReLU6(object):

    def __init__(self):
        pass

    def __call__(self, x):
        return F.relu6(x)


def relu6(x):
    """
    Computes Rectified Linear 6: min(max(features, 0), 6).

    Parameters
    ----------
    x : tensor
        Must be one of the following types: float32, float64, int32, uint8, int16,
        int8, int64, bfloat16, uint16, half, uint32, uint64, qint8.

    Returns
    -------
        A Tensor with the same type as features.
    """
    return F.relu6(x)


class LeakyReLU(object):

    def __init__(self, alpha=0.2):
        self.alpha = alpha

    def __call__(self, x):
        return F.leaky_relu(x, negative_slope=self.alpha)


def leaky_relu(x):
    """
    Compute the Leaky ReLU activation function.

    Parameters
    ----------
    x : tensor
        representing preactivation values. Must be one of the following types:
        float16, float32, float64, int32, int64.

    Returns
    -------
        The activation value.
    """

    return F.leaky_relu(x)


class Softplus(object):

    def __init__(self):
        pass

    def __call__(self, x):
        return F.softplus(x)


def softplus(x):
    """
    Computes softplus: log(exp(features) + 1).

    Parameters
    ----------
    x : tensor
        Must be one of the following types: half, bfloat16, float32, float64.

    Returns
    -------
        A Tensor. Has the same type as features.
    """

    return F.softplus(x)


class Tanh(object):

    def __init__(self):
        pass

    def __call__(self, x):
        return F.tanh(x)


def tanh(x):
    """
    Computes hyperbolic tangent of x element-wise.

    Parameters
    ----------
    x : tensor
        Must be one of the following types: bfloat16, half, float32, float64, complex64, complex128.

    Returns
    -------
        A Tensor. Has the same type as x.
    """

    return F.tanh(x)


class Sigmoid(object):

    def __init__(self):
        pass

    def __call__(self, x):
        return F.sigmoid(x)


def sigmoid(x):
    """
    Computes sigmoid of x element-wise.

    Parameters
    ----------
    x : tensor
        A Tensor with type float16, float32, float64, complex64, or complex128.

    Returns
    -------
        A Tensor with the same type as x.
    """
    return F.sigmoid(x)


class Softmax(object):

    def __init__(self):
        pass

    def __call__(self, x):
        return F.softmax(x)


def softmax(logits, axis=-1):
    """
    Computes softmax activations.

    Parameters
    ----------
    logits : tensor
        Must be one of the following types: half, float32, float64.
    axis : int
        The dimension softmax would be performed on. The default is -1 which indicates the last dimension.

    Returns
    -------
        A Tensor. Has the same type and shape as logits.
    """
    return F.softmax(logits, axis=axis)


class Dropout(object):

    def __init__(self, keep, seed=1):
        self.keep = 1 - keep
        self.seed = seed

    def __call__(self, inputs):
        output = F.dropout(inputs, p=self.keep, mode='upscale_in_train')
        return output


class BiasAdd(object):
    """
    Adds bias to value.

    Parameters
    ----------
    x : tensor
        A Tensor with type float, double, int64, int32, uint8, int16, int8, complex64, or complex128.
    bias : tensor
        Must be the same type as value unless value is a quantized type,
        in which case a different quantized type may be used.
    Returns
    -------
        A Tensor with the same type as value.
    """

    def __init__(self, data_format='channels_last'):
        super(BiasAdd, self).__init__()
        if data_format in ['channels_first', 'NCL', 'NCHW', 'NCDHW']:
            self.data_format = 'channels_first'
        elif data_format in ['channels_last', 'NLC', 'NHWC', 'NDHWC']:
            self.data_format = 'channels_last'
        else:
            raise ("Unsupported data format: " + str(data_format))

    def __call__(self, x, bias):
        if len(x.shape) > 2 and self.data_format == 'channels_first':
            x = nchw_to_nhwc(x)
        outputs = pd.add(x, bias)
        if len(x.shape) > 2 and self.data_format == 'channels_first':
            outputs = nhwc_to_nchw(outputs)
        return outputs


def bias_add(x, bias):
    """
    Adds bias to value.

    Parameters
    ----------
    x : tensor
        A Tensor with type float, double, int64, int32, uint8, int16, int8, complex64, or complex128.
    bias : tensor
        Must be the same type as value unless value is a quantized type,
        in which case a different quantized type may be used.
    data_format : A string.
        'N...C' and 'NC...' are supported.
    name : str
        A name for the operation (optional).
    Returns
    -------
        A Tensor with the same type as value.
    """

    #TODO the bias_add only supports channels_last
    outputs = pd.add(x, bias)
    return outputs


class Conv1D(object):

    def __init__(self, stride, padding, data_format='NWC', dilations=None, out_channel=None, k_size=None):
        super(Conv1D, self).__init__()
        self.data_format, self.padding = preprocess_1d_format(padding=padding, data_format=data_format)
        self.stride = stride
        self.dilations = dilations

    def __call__(self, input, filters):
        output = F.conv1d(
            x=input, weight=filters, stride=self.stride, dilation=self.dilations, data_format=self.data_format,
            padding=self.padding
        )
        return output


def conv1d(input, filters, stride, padding, data_format='NWC', dilations=None, name=None):
    """
    Computes a 1-D convolution given 3-D input and filter tensors.

    Parameters
    ----------
    input : tensor
        A 3D Tensor. Must be of type float16, float32, or float64
    filters : tensor
        A 3D Tensor. Must have the same type as input.
    stride : int of list
         An int or list of ints that has length 1 or 3. The number of entries by which the filter is moved right at each step.
    padding : string
         'SAME' or 'VALID'
    data_format : string
        An optional string from "NWC", "NCW". Defaults to "NWC", the data is stored in the order of
        [batch, in_width, in_channels]. The "NCW" format stores data as [batch, in_channels, in_width].
    dilations : int or list
        An int or list of ints that has length 1 or 3 which defaults to 1.
        The dilation factor for each dimension of input. If set to k > 1,
        there will be k-1 skipped cells between each filter element on that dimension.
        Dilations in the batch and depth dimensions must be 1.
    name : string
        A name for the operation (optional).
    Returns
    -------
        A Tensor. Has the same type as input.
    """

    outputs = F.conv1d(
        x=input, weight=filters, stride=stride, padding=padding, data_format=data_format, dilation=dilations, name=name
    )
    return outputs


class Conv2D(object):

    def __init__(self, strides, padding, data_format='NHWC', dilations=None, out_channel=None, k_size=None):
        self.data_format, self.padding = preprocess_2d_format(data_format, padding)
        if self.data_format is 'NHWC':
            self._stride = (strides[1], strides[2])
            self._dilation = (dilations[1], dilations[2])
        elif self.data_format is 'NCHW':
            self._stride = (strides[2], strides[3])
            self._dilation = (dilations[2], dilations[3])

    def __call__(self, inputs, filters):
        outputs = F.conv2d(
            x=inputs, weight=filters, stride=self._stride, dilation=self._dilation, padding=self.padding,
            data_format=self.data_format
        )
        return outputs


def conv2d(input, filters, strides, padding, data_format='NCHW', dilations=None):
    """
    Computes a 2-D convolution given 4-D input and filters tensors.

    Parameters
    ----------
    input : tensor
        Must be one of the following types: half, bfloat16, float32, float64. A 4-D tensor.
        The dimension order is interpreted according to the value of data_format, see below for details.
    filters : tensor
         Must have the same type as input. A 4-D tensor of shape [filter_height, filter_width, in_channels, out_channels]
    strides : int of list
        The stride of the sliding window for each dimension of input. If a single value is given it is replicated in the H and W dimension.
        By default the N and C dimensions are set to 1. The dimension order is determined by the value of data_format, see below for details.
    padding : string
        "SAME" or "VALID"
    data_format : string
        "NHWC", "NCHW". Defaults to "NCHW".
    dilations : list or ints
        list of ints that has length 1, 2 or 4, defaults to 1. The dilation factor for each dimension ofinput.

    Returns
    -------
        A Tensor. Has the same type as input.
    """
    data_format, padding = preprocess_2d_format(data_format, padding)
    if data_format is 'NHWC':
        _stride = (strides[1], strides[2])
        _dilation = (dilations[1], dilations[2])
    elif data_format is 'NCHW':
        _stride = (strides[2], strides[3])
        _dilation = (dilations[2], dilations[3])
    outputs = F.conv2d(
        x=input, weight=filters, stride=_stride, dilation=_dilation, padding=padding, data_format=data_format
    )
    return outputs


class Conv3D(object):

    def __init__(self, strides, padding, data_format='NDHWC', dilations=None, out_channel=None, k_size=None):
        self.data_format, self.padding = preprocess_3d_format(data_format, padding)
        if data_format is 'NDHWC':
            self._strides = (strides[1], strides[2], strides[3])
            self._dilations = (dilations[1], dilations[2], dilations[3])
        elif data_format is 'NCDHW':
            self._strides = (strides[2], strides[3], strides[4])
            self._dilations = (dilations[2], dilations[3], dilations[4])

    def __call__(self, input, filters):
        outputs = F.conv3d(
            x=input, weight=filters, stride=self._strides, dilation=self._dilations, data_format=self.data_format,
            padding=self.padding
        )
        return outputs


def conv3d(input, filters, strides, padding, data_format='NDHWC', dilations=None, name=None):
    """
    Computes a 3-D convolution given 5-D input and filters tensors.

    Parameters
    ----------
    input : tensor
        Must be one of the following types: half, bfloat16, float32, float64.
        Shape [batch, in_depth, in_height, in_width, in_channels].
    filters : tensor
        Must have the same type as input. Shape [filter_depth, filter_height, filter_width, in_channels, out_channels].
        in_channels must match between input and filters.
    strides : tuple of ints
        A list of ints that has length >= 5. 1-D tensor of length 5.
        The stride of the sliding window for each dimension of input.
        Must have strides[0] = strides[4] = 1.
    padding : string
        A string from: "SAME", "VALID". The type of padding algorithm to use.
    data_format : string
        An optional string from: "NDHWC", "NCDHW". Defaults to "NDHWC". The data format of the input and output data.
        With the default format "NDHWC", the data is stored in the order of: [batch, in_depth, in_height, in_width, in_channels].
        Alternatively, the format could be "NCDHW", the data storage order is: [batch, in_channels, in_depth, in_height, in_width].
    dilations : touple of ints
        Defaults to [1, 1, 1, 1, 1]. 1-D tensor of length 5. The dilation factor for each dimension of input.
        If set to k > 1, there will be k-1 skipped cells between each filter element on that dimension.
        The dimension order is determined by the value of data_format, see above for details.
        Dilations in the batch and depth dimensions must be 1.
    name : string
        A name for the operation (optional).

    Returns
    -------
        A Tensor. Has the same type as input.
    """
    data_format, padding = preprocess_3d_format(data_format, padding)
    if data_format is 'NDHWC':
        _strides = (strides[1], strides[2], strides[3])
        _dilations = (dilations[1], dilations[2], dilations[3])
    elif data_format is 'NCDHW':
        _strides = (strides[2], strides[3], strides[4])
        _dilations = (dilations[2], dilations[3], dilations[4])
    outputs = F.conv3d(
        x=input, weight=filters, stride=_strides, dilation=_dilations, data_format=data_format, padding=padding,
        name=name
    )
    return outputs


def lrn(inputs, depth_radius, bias, alpha, beta):
    """
    Local Response Normalization.

    Parameters
    ----------
    inputs : tensor
        Must be one of the following types: half, bfloat16, float32. 4-D.
    depth_radius : int
        Defaults to 5. 0-D. Half-width of the 1-D normalization window.
    bias : float
        Defaults to 1. An offset (usually positive to avoid dividing by 0).
    alpha : float
        Defaults to 1. A scale factor, usually positive.
    beta : float
         Defaults to 0.5. An exponent.

    Returns
    -------
        A Tensor. Has the same type as input.
    """
    pass


def moments(x, axes, shift=None, keepdims=False):
    """
    Calculates the mean and variance of x.

    Parameters
    ----------
    x : tensor
        A Tensor
    axes : ints
        Axes along which to compute mean and variance.
    shift : int
        Not used in the current implementation.
    keepdims : bool
        produce moments with the same dimensionality as the input.

    Returns
    -------
        Two Tensor objects: mean and variance.
    """

    pass


class MaxPool1d(object):

    def __init__(self, ksize, strides, padding, data_format=None):
        self.data_format, self.padding = preprocess_1d_format(data_format=data_format, padding=padding)
        self.ksize = ksize
        self.strides = strides

    def __call__(self, inputs):
        if self.data_format == 'NLC':
            inputs = nhwc_to_nchw(inputs)
        outputs = F.max_pool1d(inputs, self.ksize, self.strides, self.padding)
        if self.data_format == 'NLC':
            outputs = nchw_to_nhwc(outputs)
        return outputs


class MaxPool(object):

    def __init__(self, ksize, strides, padding, data_format=None):
        self.data_format, self.padding = preprocess_2d_format(data_format, padding)
        self.ksize = ksize
        if self.data_format is 'NHWC':
            self._stride = (strides[1], strides[2])
        elif self.data_format is 'NCHW':
            self._stride = (strides[2], strides[3])

    def __call__(self, inputs):
        outputs = F.max_pool2d(
            x=inputs, kernel_size=self.ksize, stride=self._stride, padding=self.padding, data_format=self.data_format
        )
        return outputs


def max_pool(input, ksize, strides, padding, data_format=None):
    """
    Performs the max pooling on the input.

    Parameters
    ----------
    input : tensor
        Tensor of rank N+2, of shape [batch_size] + input_spatial_shape + [num_channels] if data_format does not start
        with "NC" (default), or [batch_size, num_channels] + input_spatial_shape if data_format starts with "NC".
        Pooling happens over the spatial dimensions only.
    ksize : int or list of ints
        An int or list of ints that has length 1, N or N+2.
        The size of the window for each dimension of the input tensor.
    strides : int or list of ints
        An int or list of ints that has length 1, N or N+2.
        The stride of the sliding window for each dimension of the input tensor.
    padding : string
        'VALID' or 'SAME'. The padding algorithm. See the "returns" section of tf.ops.convolution for details.

    Returns
    -------
        A Tensor of format specified by data_format. The max pooled output tensor.
    """
    pass


class AvgPool1d(object):

    def __init__(self, ksize, strides, padding, data_format=None):
        self.data_format, self.padding = preprocess_1d_format(data_format=data_format, padding=padding)
        self.ksize = ksize
        self.strides = strides

    def __call__(self, inputs):
        if self.data_format == 'NLC':
            inputs = nhwc_to_nchw(inputs)
        outputs = F.avg_pool1d(inputs, self.ksize, self.strides, self.padding)
        if self.data_format == 'NLC':
            outputs = nchw_to_nhwc(outputs)
        return outputs


class AvgPool(object):

    def __init__(self, ksize, strides, padding, data_format=None):
        self.data_format, self.padding = preprocess_2d_format(data_format, padding)
        self.filter_size = ksize
        if self.data_format is 'NHWC':
            self._stride = (strides[1], strides[2])
        elif self.data_format is 'NCHW':
            self._stride = (strides[2], strides[3])

    def __call__(self, inputs):
        outputs = F.avg_pool2d(
            inputs, kernel_size=self.filter_size, stride=self._stride, padding=self.padding,
            data_format=self.data_format
        )
        return outputs


def avg_pool(input, ksize, strides, padding):
    """
    Performs the avg pooling on the input.

    Parameters
    ----------
    input : tensor
        Tensor of rank N+2, of shape [batch_size] + input_spatial_shape + [num_channels]
        if data_format does not start with "NC" (default), or [batch_size, num_channels] + input_spatial_shape
        if data_format starts with "NC". Pooling happens over the spatial dimensions only.
    ksize : int or list of ints
        An int or list of ints that has length 1, N or N+2.
        The size of the window for each dimension of the input tensor.
    strides : int or list of ints
        An int or list of ints that has length 1, N or N+2.
        The stride of the sliding window for each dimension of the input tensor.
    padding : string
        'VALID' or 'SAME'. The padding algorithm. See the "returns" section of tf.ops.convolution for details.

    Returns
    -------
        A Tensor of format specified by data_format. The average pooled output tensor.
    """
    pass


class MaxPool3d(object):

    def __init__(self, ksize, strides, padding, data_format=None):
        self.data_format, self.padding = preprocess_3d_format(data_format, padding)
        self.ksize = ksize
        if self.data_format == 'NCDHW':
            self.strides = (strides[2], strides[3], strides[4])
        if self.data_format == 'NDHWC':
            self.strides = (strides[1], strides[2], strides[3])

    def __call__(self, inputs):
        outputs = F.max_pool3d(
            inputs, kernel_size=self.ksize, stride=self.strides, padding=self.padding, data_format=self.data_format
        )
        return outputs


def max_pool3d(input, ksize, strides, padding, data_format=None, name=None):
    """
    Performs the max pooling on the input.

    Parameters
    ----------
    input : tensor
         A 5-D Tensor of the format specified by data_format.
    ksize : int or list of ints
        An int or list of ints that has length 1, 3 or 5.
        The size of the window for each dimension of the input tensor.
    strides : int or list of ints
        An int or list of ints that has length 1, 3 or 5.
        The stride of the sliding window for each dimension of the input tensor.
    padding : string
        'VALID' or 'SAME'. The padding algorithm. See the "returns" section of tf.ops.convolution for details.
    data_format : string
         "NDHWC", "NCDHW". Defaults to "NDHWC". The data format of the input and output data.
         With the default format "NDHWC", the data is stored in the order of: [batch, in_depth, in_height, in_width, in_channels].
         Alternatively, the format could be "NCDHW", the data storage order is: [batch, in_channels, in_depth, in_height, in_width].
    name : string
         A name for the operation (optional).

    Returns
    -------
        A Tensor of format specified by data_format. The max pooled output tensor.
    """
    pass


class AvgPool3d(object):

    def __init__(self, ksize, strides, padding, data_format=None):
        self.data_format, self.padding = preprocess_3d_format(data_format, padding)
        self.ksize = ksize
        if self.data_format == 'NCDHW':
            self.strides = (strides[2], strides[3], strides[4])
        if self.data_format == 'NDHWC':
            self.strides = (strides[1], strides[2], strides[3])

    def __call__(self, inputs):
        outputs = F.avg_pool3d(
            inputs, kernel_size=self.ksize, stride=self.strides, padding=self.padding, data_format=self.data_format
        )
        return outputs


def avg_pool3d(input, ksize, strides, padding, data_format=None, name=None):
    """
    Performs the average pooling on the input.

    Parameters
    ----------
    input : tensor
        A 5-D Tensor of shape [batch, height, width, channels] and type float32, float64, qint8, quint8, or qint32.
    ksize : int or list of ints
        An int or list of ints that has length 1, 3 or 5. The size of the window for each dimension of the input tensor.
    strides : int or list of ints
        An int or list of ints that has length 1, 3 or 5.
        The stride of the sliding window for each dimension of the input tensor.
    padding : string
        'VALID' or 'SAME'. The padding algorithm. See the "returns" section of tf.ops.convolution for details.
    data_format : string
        'NDHWC' and 'NCDHW' are supported.
    name : string
        Optional name for the operation.

    Returns
    -------
        A Tensor with the same type as value. The average pooled output tensor.
    """
    pass


def pool(input, window_shape, pooling_type, strides=None, padding='VALID', data_format=None, dilations=None, name=None):
    """
    Performs an N-D pooling operation.

    Parameters
    ----------
    input : tensor
        Tensor of rank N+2, of shape [batch_size] + input_spatial_shape + [num_channels]
        if data_format does not start with "NC" (default), or [batch_size, num_channels] + input_spatial_shape
        if data_format starts with "NC". Pooling happens over the spatial dimensions only.
    window_shape : int
        Sequence of N ints >= 1.
    pooling_type : string
        Specifies pooling operation, must be "AVG" or "MAX".
    strides : ints
        Sequence of N ints >= 1. Defaults to [1]*N. If any value of strides is > 1, then all values of dilation_rate must be 1.
    padding : string
        The padding algorithm, must be "SAME" or "VALID". Defaults to "SAME".
        See the "returns" section of tf.ops.convolution for details.
    data_format : string
        Specifies whether the channel dimension of the input and output is the last dimension (default, or if data_format does not start with "NC"),
        or the second dimension (if data_format starts with "NC").
        For N=1, the valid values are "NWC" (default) and "NCW". For N=2, the valid values are "NHWC" (default) and "NCHW".
        For N=3, the valid values are "NDHWC" (default) and "NCDHW".
    dilations : list of ints
        Dilation rate. List of N ints >= 1. Defaults to [1]*N. If any value of dilation_rate is > 1, then all values of strides must be 1.
    name : string
        Optional. Name of the op.

    Returns
    -------
        Tensor of rank N+2, of shape [batch_size] + output_spatial_shape + [num_channels]
    """
    pass


class DepthwiseConv2d(object):

    def __init__(self, strides, padding, data_format=None, dilations=None, ksize=None, channel_multiplier=1):
        self.data_format, self.padding = preprocess_2d_format(data_format, padding)
        self.stride = strides
        self.dilations = dilations

    def __call__(self, input, filter):
        raise NotImplementedError("Not implemented depthwiseconv2d")


def depthwise_conv2d(input, filter, strides, padding, data_format=None, dilations=None, name=None):
    """
    Depthwise 2-D convolution.

    Parameters
    ----------
    input : tensor
        4-D with shape according to data_format.
    filter : tensor
        4-D with shape [filter_height, filter_width, in_channels, channel_multiplier].
    strides : list
        1-D of size 4. The stride of the sliding window for each dimension of input.
    padding : string
        'VALID' or 'SAME'. The padding algorithm. See the "returns" section of tf.ops.convolution for details.
    data_format : string
        The data format for input. Either "NHWC" (default) or "NCHW".
    dilations : list
        1-D of size 2. The dilation rate in which we sample input values across the height and width dimensions in atrous convolution.
        If it is greater than 1, then all values of strides must be 1.
    name : string
        A name for this operation (optional).

    Returns
    -------
        A 4-D Tensor with shape according to data_format.
        E.g., for "NHWC" format, shape is [batch, out_height, out_width, in_channels * channel_multiplier].
    """

    pass


class Conv1d_transpose(object):

    def __init__(
        self, stride, padding, data_format='NWC', dilations=None, out_channel=None, k_size=None, in_channels=None
    ):
        self.stride = stride
        self.dilations = dilations
        self.data_format, self.padding = preprocess_1d_format(data_format, padding)

    def __call__(self, input, filters):
        out = F.conv1d_transpose(
            x=input,
            weight=filters,
            padding=self.padding,
            stride=self.stride,
            dilation=self.dilations,
            data_format=self.data_format,
        )
        return out


def conv1d_transpose(
    input, filters, output_shape, stride, padding='SAME', data_format='NWC', dilations=None, name=None
):
    """
    The transpose of conv1d.

    Parameters
    ----------
    input : tensor
        A 3-D Tensor of type float and shape [batch, in_width, in_channels]
        for NWC data format or [batch, in_channels, in_width] for NCW data format.
    filters : tensor
        A 3-D Tensor with the same type as value and shape [filter_width, output_channels, in_channels].
        filter's in_channels dimension must match that of value.
    output_shape : tensor
        A 1-D Tensor, containing three elements, representing the output shape of the deconvolution op.
    strides : list
        An int or list of ints that has length 1 or 3. The number of entries by which the filter is moved right at each step.
    padding : string
        'VALID' or 'SAME'. The padding algorithm. See the "returns" section of tf.ops.convolution for details.
    data_format : string
        'NWC' and 'NCW' are supported.
    dilations : list
         An int or list of ints that has length 1 or 3 which defaults to 1.
         The dilation factor for each dimension of input. If set to k > 1,
         there will be k-1 skipped cells between each filter element on that dimension.
         Dilations in the batch and depth dimensions must be 1.
    name : string
        Optional name for the returned tensor.

    Returns
    -------
        A Tensor with the same type as value.
    """
    data_format, padding = preprocess_1d_format(data_format, padding)
    output = F.conv1d_transpose(
        x=input,
        weight=filters,
        stride=stride,
        padding=padding,
        dilation=dilations,
        data_format=data_format,
        output_size=output_shape,
    )
    return output


class Conv2d_transpose(object):

    def __init__(
        self, strides, padding, data_format='NHWC', dilations=None, name=None, out_channel=None, k_size=None,
        in_channels=None
    ):
        self.strides = strides
        self.dilations = dilations
        self.data_format, self.padding = preprocess_2d_format(data_format, padding)

    def __call__(self, input, filters):
        output = F.conv2d_transpose(
            x=input, weight=filters, stride=self.strides, padding=self.padding, dilation=self.dilations,
            data_format=self.data_format
        )
        return output


def conv2d_transpose(
    input, filters, output_shape, strides, padding='SAME', data_format='NHWC', dilations=None, name=None
):
    """
    The transpose of conv2d.

    Parameters
    ----------
    input : tensor
        A 4-D Tensor of type float and shape [batch, height, width, in_channels]
        for NHWC data format or [batch, in_channels, height, width] for NCHW data format.
    filters : tensor
        A 4-D Tensor with the same type as input and shape [height, width,
        output_channels, in_channels]. filter's in_channels dimension must match that of input.
    output_shape : tensor
        A 1-D Tensor representing the output shape of the deconvolution op.
    strides : list
        An int or list of ints that has length 1, 2 or 4. The stride of the sliding window for each dimension of input.
        If a single value is given it is replicated in the H and W dimension.
        By default the N and C dimensions are set to 0.
        The dimension order is determined by the value of data_format, see below for details.
    padding : string
        'VALID' or 'SAME'. The padding algorithm. See the "returns" section of tf.ops.convolution for details.
    data_format : string
         'NHWC' and 'NCHW' are supported.
    dilations : list
        An int or list of ints that has length 1, 2 or 4, defaults to 1.
    name : string
        Optional name for the returned tensor.

    Returns
    -------
        A Tensor with the same type as input.
    """
    data_format, padding = preprocess_2d_format(data_format, padding)
    output = F.conv2d_transpose(
        x=input,
        weight=filters,
        output_size=output_shape,
        stride=strides,
        padding=padding,
        dilation=dilations,
        data_format=data_format,
    )
    return output


class Conv3d_transpose(object):

    def __init__(
        self, strides, padding, data_format='NDHWC', dilations=None, name=None, out_channel=None, k_size=None,
        in_channels=None
    ):
        self.strides = strides
        self.dilations = dilations
        self.data_format, self.padding = preprocess_3d_format(data_format, padding)

    def __call__(self, input, filters):

        output = F.conv3d_transpose(
            x=input, weight=filters, stride=self.strides, padding=self.padding, dilation=self.dilations,
            data_format=self.data_format
        )


def conv3d_transpose(
    input, filters, output_shape, strides, padding='SAME', data_format='NDHWC', dilations=None, name=None
):
    """
    The transpose of conv3d.

    Parameters
    ----------
    input : tensor
         A 5-D Tensor of type float and shape [batch, height, width, in_channels] for
         NHWC data format or [batch, in_channels, height, width] for NCHW data format.
    filters : tensor
        A 5-D Tensor with the same type as value and shape [height, width, output_channels, in_channels].
        filter's in_channels dimension must match that of value.
    output_shape : tensor
        A 1-D Tensor representing the output shape of the deconvolution op.
    strides : list
        An int or list of ints that has length 1, 3 or 5.
    padding : string
        'VALID' or 'SAME'. The padding algorithm. See the "returns" section of tf.ops.convolution for details.
    data_format : string
        'NDHWC' and 'NCDHW' are supported.
    dilations : list of ints
        An int or list of ints that has length 1, 3 or 5, defaults to 1.
    name : string
        Optional name for the returned tensor.

    Returns
    -------
        A Tensor with the same type as value.
    """
    data_format, padding = preprocess_3d_format(data_format, padding)
    output = F.conv3d_transpose(
        x=input,
        weight=filters,
        output_size=output_shape,
        stride=strides,
        padding=padding,
        dilation=dilations,
        data_format=data_format,
    )
    return output


class BatchNorm(object):

    def __init__(
        self, decay=0.9, epsilon=0.00001, beta=None, gamma=None, moving_mean=None, moving_var=None, num_features=None,
        data_format='channels_last', is_train=False
    ):
        self.decay = decay
        self.epsilon = epsilon
        self.data_format = data_format
        self.beta = beta
        self.gamma = gamma
        self.moving_mean = moving_mean
        self.moving_var = moving_var
        self.num_features = num_features
        self.is_train = is_train
        self.axes = None

    def __call__(self, inputs):
        data_format = self.channel_format(inputs)
        outputs = pd.nn.functional.batch_norm(
            inputs, self.moving_mean, self.moving_var, weight=self.gamma, bias=self.beta, training=self.is_train,
            momentum=self.decay, epsilon=self.epsilon, data_format=data_format
        )
        return outputs

    def channel_format(self, inputs):
        """ return "NC", "NCL", "NCHW", "NCDHW", "NLC", "NHWC" or "NDHWC". """
        len_in_shape = len(inputs.shape)
        if len_in_shape == 2:
            return 'NC'
        if self.data_format == 'channels_last':
            if len_in_shape == 3:
                return 'NLC'
            if len_in_shape == 4:
                return 'NHWC'
            if len_in_shape == 5:
                return 'NDHWC'
        if self.data_format == 'channels_first':
            if len_in_shape == 3:
                return 'NCL'
            if len_in_shape == 4:
                return 'NCHW'
            if len_in_shape == 5:
                return 'NCDHW'


class GroupConv2D(object):

    def __init__(self, strides, padding, data_format, dilations, out_channel, k_size, groups):
        pass

    def __call__(self, input, filters):
        raise NotImplementedError


class SeparableConv1D(object):

    def __init__(self, stride, padding, data_format, dilations, out_channel, k_size, in_channel, depth_multiplier):
        pass

    def __call__(self, inputs, depthwise_filters, pointwise_filters):
        raise NotImplementedError


class SeparableConv2D(object):

    def __init__(self, strides, padding, data_format, dilations, out_channel, k_size, in_channel, depth_multiplier):
        pass

    def __call__(self, inputs, depthwise_filters, pointwise_filters):
        raise NotImplementedError


class AdaptiveMeanPool1D(object):

    def __init__(self, output_size, data_format):
        self.data_format, _ = preprocess_1d_format(data_format, None)
        self.output_size = output_size

    def __call__(self, input):

        if self.data_format == 'NLC':
            input = nhwc_to_nchw(input)

        output = F.adaptive_avg_pool1d(input, self.output_size)

        if self.data_format == 'NLC':
            output = nchw_to_nhwc(output)

        return output


class AdaptiveMeanPool2D(object):

    def __init__(self, output_size, data_format):
        self.data_format, _ = preprocess_2d_format(data_format, None)
        self.output_size = output_size

    def __call__(self, inputs):

        return F.adaptive_avg_pool2d(inputs, output_size=self.output_size, data_format=self.data_format)


class AdaptiveMeanPool3D(object):

    def __init__(self, output_size, data_format):
        self.data_format, _ = preprocess_3d_format(data_format, None)
        self.output_size = output_size

    def __call__(self, inputs):

        return F.adaptive_avg_pool3d(inputs, output_size=self.output_size, data_format=self.data_format)


class AdaptiveMaxPool1D(object):

    def __init__(self, output_size, data_format):

        self.data_format, _ = preprocess_1d_format(data_format, None)
        self.output_size = output_size

    def __call__(self, input):

        if self.data_format == 'NLC':
            input = nhwc_to_nchw(input)

        output = F.adaptive_max_pool1d(input, self.output_size)

        if self.data_format == 'NLC':
            output = nchw_to_nhwc(output)

        return output


class AdaptiveMaxPool2D(object):

    def __init__(self, output_size, data_format):
        self.data_format, _ = preprocess_2d_format(data_format, None)
        self.output_size = output_size

    def __call__(self, inputs):
        if self.data_format == 'NHWC':
            inputs = nhwc_to_nchw(inputs)

        output = F.adaptive_max_pool2d(inputs, self.output_size)

        if self.data_format == 'NHWC':
            output = nchw_to_nhwc(output)

        return output


class AdaptiveMaxPool3D(object):

    def __init__(self, output_size, data_format):
        self.data_format, _ = preprocess_3d_format(data_format, None)
        self.output_size = output_size

    def __call__(self, inputs):
        if self.data_format == 'NDHWC':
            inputs = nhwc_to_nchw(inputs)

        output = F.adaptive_max_pool3d(inputs, self.output_size)

        if self.data_format == 'NDHWC':
            output = nchw_to_nhwc(output)

        return output


class BinaryConv2D(object):

    def __init__(self, strides, padding, data_format, dilations, out_channel, k_size, in_channel):
        pass

    def __call__(self, inputs, filters):
        raise NotImplementedError


class DorefaConv2D(object):

    def __init__(self, bitW, bitA, strides, padding, data_format, dilations, out_channel, k_size, in_channel):
        pass

    def __call__(self, inputs, filters):
        raise NotImplementedError


class rnncell(object):

    def __init__(self, weight_ih, weight_hh, bias_ih, bias_hh, bias, act):
        self.weight_ih = weight_ih
        self.weight_hh = weight_hh
        self.bias_ih = bias_ih
        self.bias_hh = bias_hh
        self.bias = bias
        self.act_fn = F.relu if act == 'relu' else F.tanh

    def __call__(self, input, h):

        i2h = pd.matmul(input, self.weight_ih, transpose_y=True)
        if self.bias_ih is not None:
            i2h += self.bias_ih
        h2h = pd.matmul(h, self.weight_hh, transpose_y=True)
        if self.bias_hh is not None:
            h2h += self.bias_hh
        h = self.act_fn(i2h + h2h)
        return h, h


class lstmcell(object):

    def __init__(self, weight_ih, weight_hh, bias_ih, bias_hh, bias):
        self.weight_ih = weight_ih
        self.weight_hh = weight_hh
        self.bias_ih = bias_ih
        self.bias_hh = bias_hh
        self.bias = bias
        self.gate_act_fn = F.sigmoid
        self.act_fn = F.tanh

    def __call__(self, inputs, h, c):

        gates = pd.matmul(inputs, self.weight_ih, transpose_y=True)
        if self.bias_ih is not None:
            gates += self.bias_ih
        gates += pd.matmul(h, self.weight_hh, transpose_y=True)
        if self.bias_hh is not None:
            gates += self.bias_hh

        gates_slices = pd.split(gates, num_or_sections=4, axis=-1)

        i = self.gate_act_fn(gates_slices[0])
        f = self.gate_act_fn(gates_slices[1])
        o = self.gate_act_fn(gates_slices[3])
        c = f * c + i * self.act_fn(gates_slices[2])
        h = o * self.act_fn(c)

        return h, h, c


class grucell(object):

    def __init__(self, weight_ih, weight_hh, bias_ih, bias_hh, bias):
        self.weight_ih = weight_ih
        self.weight_hh = weight_hh
        self.bias_ih = bias_ih
        self.bias_hh = bias_hh
        self.bias = bias
        self.gate_act_fn = F.sigmoid
        self.act_fn = F.tanh

    def __call__(self, input, h):

        x_gates = pd.matmul(input, self.weight_ih, transpose_y=True)
        if self.bias_ih is not None:
            x_gates = x_gates + self.bias_ih
        h_gates = pd.matmul(h, self.weight_hh, transpose_y=True)
        if self.bias_hh is not None:
            h_gates = h_gates + self.bias_hh

        x_r, x_z, x_c = pd.split(x_gates, num_or_sections=3, axis=-1)
        h_r, h_z, h_c = pd.split(h_gates, num_or_sections=3, axis=-1)

        r = self.gate_act_fn(x_r + h_r)
        z = self.gate_act_fn(x_z + h_z)
        c = self.act_fn(x_c + r * h_c)  # apply reset gate after mm
        h = (h - c) * z + c

        return h, h


def split_states(states, bidirectional=False, state_components=1):
    r"""
    Split states of RNN network into possibly nested list or tuple of
    states of each RNN cells of the RNN network.

    Parameters:
        states (Tensor|tuple|list): the concatenated states for RNN network.
            When `state_components` is 1, states in a Tensor with shape
            `(L*D, N, C)` where `L` is the number of layers of the RNN
            network, `D` is the number of directions of the RNN network(1
            for unidirectional RNNs and 2 for bidirectional RNNs), `N` is
            the batch size of the input to the RNN network, `C` is the
            hidden size of the RNN network.

            When `state_components` is larger than 1, `states` is a tuple of
            `state_components` Tensors that meet the requirements described
            above.

            For SimpleRNNs and GRUs, `state_components` is 1, and for LSTMs,
            `state_components` is 2.
        bidirectional (bool): whether the state is of a bidirectional RNN
            network. Defaults to False.
        state_components (int): the number of the components of the states. see
            `states` above. Defaults to 1.

    Returns:
        A nested list or tuple of RNN cell states.
        If `bidirectional` is True, it can be indexed twice to get an RNN
        cell state. The first index indicates the layer, the second index
        indicates the direction.
        If `bidirectional` is False, it can be indexed once to get an RNN
        cell state. The index indicates the layer.
        Note that if `state_components` is larger than 1, an RNN cell state
        can be indexed one more time to get a tensor of shape(N, C), where
        `N` is the batch size of the input to the RNN cell, and `C` is the
        hidden size of the RNN cell.
    """
    if state_components == 1:
        states = pd.unstack(states)
        if not bidirectional:
            return states
        else:
            return list(zip(states[::2], states[1::2]))
    else:
        assert len(states) == state_components
        states = tuple([pd.unstack(item) for item in states])
        if not bidirectional:
            return list(zip(*states))
        else:
            states = list(zip(*states))
            return list(zip(states[::2], states[1::2]))


def concat_states(states, bidirectional=False, state_components=1):
    r"""
    Concatenate a possibly nested list or tuple of RNN cell states into a
    compact form.

    Parameters:
        states (list|tuple): a possibly nested list or tuple of RNN cell
            states.
            If `bidirectional` is True, it can be indexed twice to get an
            RNN cell state. The first index indicates the layer, the second
            index indicates the direction.
            If `bidirectional` is False, it can be indexed once to get an RNN
            cell state. The index indicates the layer.
            Note that if `state_components` is larger than 1, an RNN cell
            state can be indexed one more time to get a tensor of shape(N, C),
            where `N` is the batch size of the input to the RNN cell, and
            `C` is the hidden size of the RNN cell.
        bidirectional (bool): whether the state is of a bidirectional RNN
            network. Defaults to False.
        state_components (int): the number of the components of the states. see
            `states` above. Defaults to 1.

    Returns:
        Concatenated states for RNN network.
        When `state_components` is 1, states in a Tensor with shape
        `(L\*D, N, C)` where `L` is the number of layers of the RNN
        network, `D` is the number of directions of the RNN network(1 for
        unidirectional RNNs and 2 for bidirectional RNNs), `N` is the batch
        size of the input to the RNN network, `C` is the hidden size of the
        RNN network.

    """
    if state_components == 1:
        return pd.stack(flatten(states))
    else:
        states = flatten(states)
        componnets = []
        for i in range(state_components):
            componnets.append(states[i::state_components])
        return tuple([pd.stack(item) for item in componnets])


class rnnbase(Layer):

    def __init__(
        self,
        mode,
        input_size,
        hidden_size,
        num_layers,
        bias,
        batch_first,
        dropout,
        bidirectional,
        is_train,
    ):
        super(rnnbase, self).__init__()
        self.mode = mode
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.time_major = False if batch_first else True
        self.dropout = dropout
        self.bidirect = 2 if bidirectional else 1
        self.state_components = 2 if mode == 'LSTM' else 1
        self.rnn = pd.nn.LayerList()
        RNN = pd.nn.RNN
        BiRNN = pd.nn.BiRNN
        weight_ih_attr = None
        weight_hh_attr = None
        if bias:
            bias_ih_attr = None
            bias_hh_attr = None
        else:
            bias_ih_attr = False
            bias_hh_attr = False

        kwargs = {
            "weight_ih_attr": weight_ih_attr,
            "weight_hh_attr": weight_hh_attr,
            "bias_ih_attr": bias_ih_attr,
            "bias_hh_attr": bias_hh_attr
        }

        if mode == "LSTM":
            rnn_cls = pd.nn.LSTMCell
        elif mode == "GRU":
            rnn_cls = pd.nn.GRUCell
        elif mode == 'RNN_TANH':
            rnn_cls = pd.nn.SimpleRNNCell
            kwargs["activation"] = 'tanh'
        elif mode == 'RNN_RELU':
            rnn_cls = pd.nn.SimpleRNNCell
            kwargs["activation"] = 'relu'

        if not bidirectional:
            is_reverse = False
            cell = rnn_cls(input_size, hidden_size, **kwargs)
            self.rnn.append(RNN(cell, is_reverse, self.time_major))
            for i in range(1, num_layers):
                cell = rnn_cls(hidden_size, hidden_size, **kwargs)
                self.rnn.append(RNN(cell, is_reverse, self.time_major))
        else:
            cell_fw = rnn_cls(input_size, hidden_size, **kwargs)
            cell_bw = rnn_cls(input_size, hidden_size, **kwargs)
            self.rnn.append(BiRNN(cell_fw, cell_bw, self.time_major))
            for i in range(1, num_layers):
                cell_fw = rnn_cls(2 * hidden_size, hidden_size, **kwargs)
                cell_bw = rnn_cls(2 * hidden_size, hidden_size, **kwargs)
                self.rnn.append(BiRNN(cell_fw, cell_bw, self.time_major))

        self.could_use_cudnn = True
        self.could_use_cudnn &= len(self.rnn.parameters()) == num_layers * 4 * self.bidirect

        param_names = []
        for layer in range(self.num_layers):
            for direction in range(self.bidirect):
                suffix = '_reverse' if direction == 1 else ''
                param_names.extend(['weight_ih_l{}{}', 'weight_hh_l{}{}'])
                if bias_ih_attr != False: param_names.append('bias_ih_l{}{}')
                if bias_hh_attr != False: param_names.append('bias_hh_l{}{}')
                param_names = [x.format(layer, suffix) for x in param_names]
        for name, param in zip(param_names, self.rnn.parameters()):
            setattr(self.rnn, name, param)

        self.flatten_parameters()

    def flatten_parameters(self):
        """
        Resets parameter data pointer to address in continuous memory block for
        cudnn usage.
        """
        if self.could_use_cudnn:
            # layer.parameters() is depth first and ordered
            # for i in layer: for j in direct: w_ih, w_hh, b_ih, b_hh
            # need to reorganize to cudnn param layout:
            # all bias following all weights
            params = self.rnn.parameters(include_sublayers=False)
            shape = [np.prod(param.shape) for param in params]
            self._all_weights = [None] * len(params)
            for i, param in enumerate(params):
                offset = 0 if i % 4 < 2 else (2 * self.num_layers * self.bidirect)
                layer_idx = i // 4
                self._all_weights[offset + layer_idx * 2 + i % 2] = param

            # Wrap using a list to avoid registed into params and saving, maybe
            # need a better way to handle this later. Use `create_parameter` to
            # add both to main_program and startup_program for static-graph.
            # Use Constant initializer to avoid make effect on random generator.
            self._flat_weight = [
                self.rnn.create_parameter(
                    shape=[np.sum(shape)], dtype=params[0].dtype, default_initializer=I.Constant(0.0)
                )
            ]

            # dropout state may also can be hided and avoid saving
            # should dropout state be persistable for static-graph
            self._dropout_state = self.rnn.create_variable(dtype=fluid.core.VarDesc.VarType.UINT8)
            # for static-graph, append coalesce_tensor into startup program
            with fluid.program_guard(fluid.default_startup_program(), fluid.default_startup_program()):
                with pd.framework.no_grad():
                    self.rnn._helper.append_op(
                        type="coalesce_tensor", inputs={"Input": self._all_weights}, outputs={
                            "Output": self._all_weights,
                            "FusedOutput": self._flat_weight
                        }, attrs={
                            "copy_data": True,
                            "use_align": False,
                            "dtype": params[0].dtype
                        }
                    )

    def _cudnn_impl(self, inputs, initial_states, sequence_length):
        if not self.time_major:
            inputs = pd.tensor.transpose(inputs, [1, 0, 2])
        out = self.rnn._helper.create_variable_for_type_inference(inputs.dtype)
        state = [
            self.rnn._helper.create_variable_for_type_inference(inputs.dtype) for i in range(self.state_components)
        ]
        reserve = self.rnn._helper.create_variable_for_type_inference(
            dtype=fluid.core.VarDesc.VarType.UINT8, stop_gradient=True
        )

        inputs = {
            'Input': inputs,
            'WeightList': self._all_weights,
            'PreState': initial_states,
            'SequenceLength': sequence_length
        }
        attrs = {
            'dropout_prob': self.dropout,
            'is_bidirec': self.bidirect == 2,
            'input_size': self.input_size,
            'hidden_size': self.hidden_size,
            'num_layers': self.num_layers,
            'mode': self.mode,
            'is_test': not self.rnn.training
        }

        outputs = {
            'Out': out,
            'State': state,
            'Reserve': reserve,
            'DropoutState': self._dropout_state,
        }

        self.rnn._helper.append_op(type="rnn", inputs=inputs, outputs=outputs, attrs=attrs)
        out = pd.tensor.transpose(out, [1, 0, 2]) if not self.time_major else out
        return out, tuple(state) if len(state) > 1 else state[0]

    def forward(self, inputs, initial_states=None, sequence_length=None):
        batch_index = 1 if self.time_major else 0
        dtype = inputs.dtype
        if initial_states is None:
            state_shape = [self.num_layers * self.bidirect, -1, self.hidden_size]
            if self.state_components == 1:
                initial_states = fluid.layers.fill_constant_batch_size_like(
                    inputs, state_shape, dtype, 0, batch_index, 1
                )
            else:
                initial_states = tuple(
                    [
                        fluid.layers.fill_constant_batch_size_like(inputs, state_shape, dtype, 0, batch_index, 1)
                        for _ in range(self.state_components)
                    ]
                )

        if self.could_use_cudnn:
            # Add CPU kernel and dispatch in backend later
            return self._cudnn_impl(inputs, initial_states, sequence_length)

        states = split_states(initial_states, self.bidirect == 2, self.state_components)

        final_states = []

        for i, rnn_layer in enumerate(self.rnn):
            if i > 0:
                inputs = F.dropout(inputs, self.dropout, training=self.rnn.training, mode="upscale_in_train")
            outputs, final_state = rnn_layer(inputs, states[i], sequence_length)
            final_states.append(final_state)
            inputs = outputs

        final_states = concat_states(final_states, self.bidirect == 2, self.state_components)
        return outputs, final_states
