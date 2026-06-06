import unittest

from image_viewer import ImageViewer


class ImageViewerCoordinateTests(unittest.TestCase):
    def test_canvas_coordinates_are_converted_using_zoom(self):
        self.assertEqual(ImageViewer.canvas_to_image(150, 90, 1.5), (100, 60))

    def test_coordinate_conversion_rejects_invalid_zoom(self):
        with self.assertRaises(ValueError):
            ImageViewer.canvas_to_image(10, 10, 0)


if __name__ == "__main__":
    unittest.main()
