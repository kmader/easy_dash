from __future__ import print_function
from __future__ import absolute_import
from __future__ import division
import base64
from io import BytesIO

import numpy as np
from PIL import Image as PImage
from matplotlib import pyplot as plt
from matplotlib.pyplot import cm


def fig_to_uri(
    in_fig,  # type: plt.Figure
    close_all=True,
    dpi=None,
    **save_args
):
    # type: (...) -> str
    """Save a figure as a URI
    :param in_fig: the figure to save
    :param close_all: close all other figures afterwards
    :param dpi: specify the DPI if desired
    :param save_args: arguments to save with
    :return:
    >>> import matplotlib
    >>> matplotlib.use('Agg')
    >>> fig, ax1 = plt.subplots(1, 1, figsize=(4,6))
    >>> lowres_str = fig_to_uri(fig, close_all=True, dpi=50)
    >>> print(lowres_str[:50])
    data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAMgA
    >>> fig, ax1 = plt.subplots(1, 1, figsize=(4,6))
    >>> highres_str = fig_to_uri(fig, close_all = True, dpi=100)
    >>> print(highres_str[:50])
    data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAZAA
    """
    out_img = BytesIO()
    in_fig.savefig(out_img, format="png", dpi=dpi, **save_args)
    if close_all:
        in_fig.clf()
        plt.close("all")
    out_img.seek(0)  # rewind file
    encoded = base64.b64encode(out_img.read()).decode("ascii").replace("\n", "")
    return "data:image/png;base64,{}".format(encoded)


def _np_to_uri(
    in_array,  # type: np.ndarray
    cmap="RdBu",  # type: str
    do_norm=True,  # type: bool
    new_size=(128, 128),  # type: Tuple[int, int]
    img_format="png",  # type: str
    alpha=True,  # type: bool
):
    # type: (...) -> str
    """
    Convert a numpy array to a data URI with an encode image inside
    :param in_array: the image to convert
    :param cmap: the color map to use
    :param do_norm: if the image should be normalized first
    :param new_size: the dimensions of the output images
    :param img_format: the file-format to save as
    :param alpha: if the alpha channel should be included
    :return: the base64 string
    Examples
    ========
    >>> print(_np_to_uri(np.zeros((100,100)))[:50])
    iVBORw0KGgoAAAANSUhEUgAAAIAAAACACAYAAADDPmHLAAABUE
    >>> print(_np_to_uri(np.zeros((5, 10)), img_format = 'jpeg')[:50])
    /9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQ
    >>> len(_np_to_uri(np.zeros((100,100)), alpha = False))
    484
    >>> len(_np_to_uri(np.zeros((100,100)), alpha = True))
    524
    """
    test_img_data = np.array(in_array).astype(np.float32)
    if do_norm:
        test_img_data -= test_img_data.mean()
        test_img_data /= test_img_data.std()
        test_img_data = (test_img_data + 0.5).clip(0, 1)
    test_img_color = cm.get_cmap(cmap)(test_img_data)
    test_img_color *= 255
    pre_array = test_img_color.clip(0, 255).astype(np.uint8)
    max_dim = max(*pre_array.shape[0:2])
    sq_array = force_array_dim(pre_array, (max_dim, max_dim) + pre_array.shape[2:])
    p_data = PImage.fromarray(sq_array)
    rs_p_data = p_data.resize(new_size, resample=PImage.BICUBIC)
    out_img_data = BytesIO()
    if img_format == "jpeg" or not alpha:
        rs_p_data = rs_p_data.convert("RGB")
    rs_p_data.save(out_img_data, format=img_format)
    out_img_data.seek(0)  # rewind
    enc_img = base64.b64encode(out_img_data.read())
    return enc_img.decode("ascii").replace("\n", "")


def _wrap_ur(data_uri):
    return "data:image/png;base64,{0}".format(data_uri)


def force_array_dim(
    in_img,  # type: np.ndarray
    out_shape,  # type: List[Optional[int]]
    pad_mode="reflect",
    crop_mode="center",
    **pad_args
):
    # type: (...) -> np.ndarray
    """
    force the dimensions of an array by using cropping and padding
    :param in_img:
    :param out_shape:
    :param pad_mode:
    :param crop_mode: center or random (default center since it is safer)
    :param pad_args:
    :return:
    >>> np.random.seed(2018)
    >>> force_array_dim(np.eye(3), [7,7], crop_mode = 'random')
    array([[1., 0., 0., 0., 1., 0., 0.],
           [0., 1., 0., 1., 0., 1., 0.],
           [0., 0., 1., 0., 0., 0., 1.],
           [0., 1., 0., 1., 0., 1., 0.],
           [1., 0., 0., 0., 1., 0., 0.],
           [0., 1., 0., 1., 0., 1., 0.],
           [0., 0., 1., 0., 0., 0., 1.]])
    >>> force_array_dim(np.eye(3), [2,2], crop_mode = 'center')
    array([[1., 0.],
           [0., 1.]])
    >>> force_array_dim(np.eye(3), [2,2], crop_mode = 'random')
    array([[1., 0.],
           [0., 1.]])
    >>> force_array_dim(np.eye(3), [2,2], crop_mode = 'random')
    array([[0., 0.],
           [1., 0.]])
    >>> e_args = dict(out_shape = [2,2], crop_mode = 'junk')
    >>> t_mat = np.ones((1, 7, 9, 3))
    >>> f_args = dict(pad_mode = 'constant', constant_values=0)
    >>> o_img = force_array_dim(t_mat, [None, 12, 12, None], **f_args)
    >>> o_img.shape
    (1, 12, 12, 3)
    >>> o_img.mean()
    0.4375
    >>> o_img[0,3,:,0]
    array([0., 1., 1., 1., 1., 1., 1., 1., 1., 1., 0., 0.])
    """
    assert crop_mode in [
        "random",
        "center",
    ], "Crop mode must be random or " "center: {}".format(crop_mode)

    pad_image = pad_nd_image(in_img, out_shape, mode=pad_mode, **pad_args)
    crop_dims = []  # type: List[slice]
    for c_shape, d_shape in zip(pad_image.shape, out_shape):
        cur_slice = slice(0, c_shape)  # default
        if d_shape is not None:
            assert d_shape <= c_shape, "Padding command failed: {}>={} - {},{}".format(
                d_shape, c_shape, pad_image.shape, out_shape
            )
            if d_shape < c_shape:
                if crop_mode == "random":
                    start_idx = np.random.choice(range(0, c_shape - d_shape + 1))
                    cur_slice = slice(start_idx, start_idx + d_shape)
                else:
                    start_idx = (c_shape - d_shape) // 2
                    cur_slice = slice(start_idx, start_idx + d_shape)
        crop_dims += [cur_slice]
    return pad_image.__getitem__(crop_dims)


def pad_nd_image(
    in_img,  # type: np.ndarray
    out_shape,  # type: List[Optional[int]]
    mode="reflect",
    **kwargs
):
    # type: (...) -> np.ndarray
    """
    Pads an array to a specific size
    :param in_img:
    :param out_shape: the desired outputs shape
    :param mode: the mode to use in numpy.pad
    :param kwargs: arguments for numpy.pad
    :return:
    >>> pad_nd_image(np.eye(3), [7,7])
    array([[1., 0., 0., 0., 1., 0., 0.],
           [0., 1., 0., 1., 0., 1., 0.],
           [0., 0., 1., 0., 0., 0., 1.],
           [0., 1., 0., 1., 0., 1., 0.],
           [1., 0., 0., 0., 1., 0., 0.],
           [0., 1., 0., 1., 0., 1., 0.],
           [0., 0., 1., 0., 0., 0., 1.]])
    >>> pad_nd_image(np.eye(3), [2,2]) # should return the same
    array([[1., 0., 0.],
           [0., 1., 0.],
           [0., 0., 1.]])
    >>> t_mat = np.ones((2, 27, 29, 3))
    >>> o_img = pad_nd_image(t_mat, [None, 32, 32, None], mode = 'constant', constant_values=0)
    >>> o_img.shape
    (2, 32, 32, 3)
    >>> o_img.mean()
    0.7646484375
    >>> o_img[0,3,:,0]
    array([0., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1.,
           1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 0., 0.])
    """
    pad_dims = []  # type: List[Tuple[int, int]]
    for c_shape, d_shape in zip(in_img.shape, out_shape):
        pad_before, pad_after = 0, 0
        if d_shape is not None:
            if c_shape < d_shape:
                dim_diff = d_shape - c_shape
                pad_before = dim_diff // 2
                pad_after = dim_diff - pad_before
        pad_dims += [(pad_before, pad_after)]
    return np.pad(in_img, pad_dims, mode=mode, **kwargs)
