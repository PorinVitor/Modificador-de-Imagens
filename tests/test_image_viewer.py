import unittest

from image_viewer import ImageViewer


class ImageViewerCoordinateTests(unittest.TestCase):
    def test_canvas_coordinates_are_converted_using_zoom(self):
        self.assertEqual(ImageViewer.canvas_to_image(150, 90, 1.5), (100, 60))

    def test_coordinate_conversion_rejects_invalid_zoom(self):
        with self.assertRaises(ValueError):
            ImageViewer.canvas_to_image(10, 10, 0)

    def test_selection_is_normalized_and_clipped(self):
        self.assertEqual(
            ImageViewer.normalize_selection((8, 9, -3, 2), (10, 12, 3)),
            (0, 2, 8, 9),
        )

    def test_zero_area_selection_keeps_one_pixel(self):
        self.assertEqual(ImageViewer.normalize_selection((4, 5, 4, 5), (10, 10)), (4, 5, 5, 6))


if __name__ == "__main__":
    unittest.main()
