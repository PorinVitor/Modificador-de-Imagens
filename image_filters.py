"""Funções de processamento de imagens usadas pela interface.

Todas as funções recebem e devolvem arrays NumPy no formato usado pelo OpenCV.
As operações não alteram o array recebido.
"""

from __future__ import annotations

from collections.abc import Callable

import cv2
import numpy as np

Image = np.ndarray
FilterFunction = Callable[[Image], Image]


def _validate_image(image: Image) -> None:
    if image is None or not isinstance(image, np.ndarray) or image.size == 0:
        raise ValueError("A imagem fornecida é inválida ou está vazia.")
    if image.ndim not in (2, 3):
        raise ValueError("A imagem deve ter dois ou três eixos.")


def to_grayscale(image: Image) -> Image:
    """Converte BGR/BGRA para tons de cinza; copia imagens já monocromáticas."""
    _validate_image(image)
    if image.ndim == 2:
        return image.copy()
    if image.shape[2] == 4:
        return cv2.cvtColor(image, cv2.COLOR_BGRA2GRAY)
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def show_blue_channel(image: Image) -> Image:
    """Exibe a intensidade do canal azul como uma imagem colorida."""
    _validate_image(image)
    if image.ndim == 2:
        return image.copy()
    blue, _, _ = cv2.split(image[:, :, :3])
    zeros = np.zeros_like(blue)
    return cv2.merge((blue, zeros, zeros))


def show_green_channel(image: Image) -> Image:
    """Exibe a intensidade do canal verde como uma imagem colorida."""
    _validate_image(image)
    if image.ndim == 2:
        return image.copy()
    _, green, _ = cv2.split(image[:, :, :3])
    zeros = np.zeros_like(green)
    return cv2.merge((zeros, green, zeros))


def show_red_channel(image: Image) -> Image:
    """Exibe a intensidade do canal vermelho como uma imagem colorida."""
    _validate_image(image)
    if image.ndim == 2:
        return image.copy()
    _, _, red = cv2.split(image[:, :, :3])
    zeros = np.zeros_like(red)
    return cv2.merge((zeros, zeros, red))


def swap_red_blue(image: Image) -> Image:
    """Demonstra split/merge trocando os canais vermelho e azul."""
    _validate_image(image)
    if image.ndim == 2:
        return image.copy()
    blue, green, red = cv2.split(image[:, :, :3])
    return cv2.merge((red, green, blue))


def median_filter(image: Image, kernel_size: int = 3) -> Image:
    """Reduz ruído impulsivo com filtro de mediana."""
    _validate_image(image)
    if kernel_size <= 1 or kernel_size % 2 == 0:
        raise ValueError("O tamanho do filtro de mediana deve ser ímpar e maior que 1.")
    return cv2.medianBlur(image, kernel_size)


def equalize_histogram(image: Image) -> Image:
    """Equaliza tons de cinza ou apenas a luminância de uma imagem colorida."""
    _validate_image(image)
    if image.ndim == 2:
        return cv2.equalizeHist(image)

    bgr = image[:, :, :3]
    ycrcb = cv2.cvtColor(bgr, cv2.COLOR_BGR2YCrCb)
    ycrcb[:, :, 0] = cv2.equalizeHist(ycrcb[:, :, 0])
    return cv2.cvtColor(ycrcb, cv2.COLOR_YCrCb2BGR)


def _kernel(size: int, shape: int = cv2.MORPH_ELLIPSE) -> Image:
    if size <= 0 or size % 2 == 0:
        raise ValueError("O elemento estruturante deve ter tamanho ímpar e positivo.")
    return cv2.getStructuringElement(shape, (size, size))


def erode(image: Image, size: int = 5, iterations: int = 2) -> Image:
    _validate_image(image)
    return cv2.erode(image, _kernel(size), iterations=iterations)


def dilate(image: Image, size: int = 5, iterations: int = 2) -> Image:
    _validate_image(image)
    return cv2.dilate(image, _kernel(size), iterations=iterations)


def opening(image: Image, size: int = 3) -> Image:
    _validate_image(image)
    return cv2.morphologyEx(image, cv2.MORPH_OPEN, _kernel(size))


def closing(image: Image, size: int = 3) -> Image:
    _validate_image(image)
    return cv2.morphologyEx(image, cv2.MORPH_CLOSE, _kernel(size))


def grayscale_opening_enhancement(image: Image, size: int = 21) -> Image:
    """Realça detalhes claros menores que o elemento estruturante (white top-hat)."""
    gray = to_grayscale(image)
    opened = cv2.morphologyEx(gray, cv2.MORPH_OPEN, _kernel(size, cv2.MORPH_CROSS))
    difference = cv2.subtract(gray, opened)
    return cv2.add(difference, difference)


def grayscale_closing_enhancement(image: Image, size: int = 21) -> Image:
    """Realça detalhes escuros menores que o elemento estruturante (black-hat)."""
    gray = to_grayscale(image)
    closed = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, _kernel(size, cv2.MORPH_CROSS))
    difference = cv2.subtract(closed, gray)
    return cv2.add(difference, difference)


def morphological_gradient(image: Image, size: int = 3) -> Image:
    """Destaca contornos pela diferença entre dilatação e erosão."""
    _validate_image(image)
    return cv2.morphologyEx(image, cv2.MORPH_GRADIENT, _kernel(size))


def top_hat(image: Image, size: int = 25) -> Image:
    """Destaca regiões claras menores que o elemento estruturante."""
    _validate_image(image)
    processed = cv2.morphologyEx(image, cv2.MORPH_TOPHAT, _kernel(size))
    return cv2.add(processed, processed)


def remove_noise(image: Image, size: int = 3) -> Image:
    """Remove pequenos pontos claros por abertura morfológica."""
    _validate_image(image)
    cross = _kernel(size, cv2.MORPH_CROSS)
    return cv2.morphologyEx(image, cv2.MORPH_OPEN, cross)


def sobel_operator(image: Image) -> Image:
    """Destaca bordas combinando os gradientes horizontal e vertical de Sobel."""
    gray = to_grayscale(image)
    grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    abs_x = cv2.convertScaleAbs(grad_x)
    abs_y = cv2.convertScaleAbs(grad_y)
    return cv2.addWeighted(abs_x, 0.5, abs_y, 0.5, 0)


def canny_detector(image: Image, lower_threshold: int = 100, upper_threshold: int = 200) -> Image:
    """Detecta bordas com o algoritmo de Canny."""
    if lower_threshold < 0 or upper_threshold < 0 or lower_threshold >= upper_threshold:
        raise ValueError("Os limiares do Canny devem ser positivos e o primeiro menor que o segundo.")
    gray = to_grayscale(image)
    return cv2.Canny(gray, lower_threshold, upper_threshold)


def calculate_histograms(image: Image) -> dict[str, Image]:
    """Calcula histogramas de 256 níveis para uma imagem cinza ou BGR."""
    _validate_image(image)
    if image.ndim == 2:
        return {"Cinza": cv2.calcHist([image], [0], None, [256], [0, 256]).ravel()}

    labels = ("Azul", "Verde", "Vermelho")
    return {
        label: cv2.calcHist([image], [channel], None, [256], [0, 256]).ravel()
        for channel, label in enumerate(labels)
    }


FILTERS: dict[str, FilterFunction] = {
    "Tons de cinza": to_grayscale,
    "Canal azul": show_blue_channel,
    "Canal verde": show_green_channel,
    "Canal vermelho": show_red_channel,
    "Trocar vermelho/azul": swap_red_blue,
    "Filtro de mediana": median_filter,
    "Equalização": equalize_histogram,
    "Erosão": erode,
    "Dilatação": dilate,
    "Abertura": opening,
    "Fechamento": closing,
    "Abertura em cinza": grayscale_opening_enhancement,
    "Fechamento em cinza": grayscale_closing_enhancement,
    "Gradiente morfológico": morphological_gradient,
    "Top Hat": top_hat,
    "Remoção de ruído": remove_noise,
    "Operador de Sobel": sobel_operator,
    "Detector de Canny": canny_detector,
}
