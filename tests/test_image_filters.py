import unittest

import cv2
import numpy as np

import image_filters as filters


class ImageFilterTests(unittest.TestCase):
    def setUp(self):
        x = np.linspace(0, 255, 25, dtype=np.uint8)
        gray = np.tile(x, (25, 1))
        self.color = cv2.merge((gray, np.flipud(gray), np.fliplr(gray)))

    def test_all_registered_filters_return_valid_images(self):
        for name, operation in filters.FILTERS.items():
            with self.subTest(filter=name):
                result = operation(self.color)
                self.assertIsInstance(result, np.ndarray)
                self.assertGreater(result.size, 0)
                self.assertEqual(result.shape[:2], self.color.shape[:2])
                self.assertEqual(result.dtype, np.uint8)

    def test_grayscale_has_two_dimensions(self):
        result = filters.to_grayscale(self.color)
        self.assertEqual(result.ndim, 2)

    def test_channel_split_keeps_only_selected_channel(self):
        blue = filters.show_blue_channel(self.color)
        self.assertTrue(np.all(blue[:, :, 1] == 0))
        self.assertTrue(np.all(blue[:, :, 2] == 0))

    def test_equalization_preserves_color_shape(self):
        result = filters.equalize_histogram(self.color)
        self.assertEqual(result.shape, self.color.shape)

    def test_median_rejects_even_kernel(self):
        with self.assertRaises(ValueError):
            filters.median_filter(self.color, 4)

    def test_filters_do_not_modify_source(self):
        source = self.color.copy()
        filters.erode(source)
        np.testing.assert_array_equal(source, self.color)

    def test_color_histograms_have_three_channels_and_256_bins(self):
        histograms = filters.calculate_histograms(self.color)
        self.assertEqual(set(histograms), {"Azul", "Verde", "Vermelho"})
        self.assertTrue(all(histogram.shape == (256,) for histogram in histograms.values()))
        self.assertTrue(all(int(histogram.sum()) == 625 for histogram in histograms.values()))

    def test_grayscale_histogram_has_one_channel(self):
        gray = filters.to_grayscale(self.color)
        histograms = filters.calculate_histograms(gray)
        self.assertEqual(list(histograms), ["Cinza"])
        self.assertEqual(histograms["Cinza"].shape, (256,))


if __name__ == "__main__":
    unittest.main()
