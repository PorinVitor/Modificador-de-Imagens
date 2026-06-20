"""Janela Tkinter que desenha histogramas de imagens OpenCV."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

import numpy as np

from image_filters import calculate_histograms


class HistogramPlot(tk.Canvas):
    COLORS = {
        "Cinza": "#222222",
        "Azul": "#1976d2",
        "Verde": "#2e9d50",
        "Vermelho": "#d43f3a",
    }

    def __init__(self, master: tk.Misc, image: np.ndarray) -> None:
        super().__init__(master, background="white", highlightthickness=1, highlightbackground="#b8bec7")
        self.histograms = calculate_histograms(image)
        self.bind("<Configure>", self._draw)

    def _draw(self, _event: tk.Event | None = None) -> None:
        self.delete("all")
        width = self.winfo_width()
        height = self.winfo_height()
        if width < 40 or height < 40:
            return

        left, top, right, bottom = 48, 22, width - 18, height - 38
        self.create_line(left, top, left, bottom, fill="#59616c")
        self.create_line(left, bottom, right, bottom, fill="#59616c")
        self.create_text(left, bottom + 18, text="0", fill="#59616c")
        self.create_text(right, bottom + 18, text="255", fill="#59616c")
        self.create_text((left + right) / 2, height - 8, text="Intensidade", fill="#59616c")
        self.create_text(10, top, text="Pixels", anchor="nw", fill="#59616c")

        maximum = max(float(histogram.max()) for histogram in self.histograms.values()) or 1.0
        plot_width = max(right - left, 1)
        plot_height = max(bottom - top, 1)
        for label, histogram in self.histograms.items():
            points: list[float] = []
            for index, amount in enumerate(histogram):
                x = left + (index / 255) * plot_width
                y = bottom - (float(amount) / maximum) * plot_height
                points.extend((x, y))
            self.create_line(*points, fill=self.COLORS[label], width=2, smooth=True)

        legend_x = left + 8
        for label in self.histograms:
            self.create_line(legend_x, top + 8, legend_x + 22, top + 8, fill=self.COLORS[label], width=3)
            self.create_text(legend_x + 28, top + 8, text=label, anchor="w", fill="#343a40")
            legend_x += 100


class HistogramWindow(tk.Toplevel):
    """Compara os histogramas da imagem original e do resultado."""

    def __init__(self, master: tk.Misc, original: np.ndarray, result: np.ndarray) -> None:
        super().__init__(master)
        self.title("Histogramas — Original e resultado")
        self.geometry("860x560")
        self.minsize(620, 420)
        self.transient(master)

        container = ttk.Frame(self, padding=12)
        container.pack(fill="both", expand=True)
        ttk.Label(
            container,
            text="Distribuição das intensidades de 0 a 255",
            font=("TkDefaultFont", 13, "bold"),
        ).pack(anchor="w", pady=(0, 8))

        notebook = ttk.Notebook(container)
        notebook.pack(fill="both", expand=True)
        for title, image in (("Imagem original", original), ("Resultado atual", result)):
            page = ttk.Frame(notebook, padding=8)
            notebook.add(page, text=title)
            plot = HistogramPlot(page, image)
            plot.pack(fill="both", expand=True)

        ttk.Label(
            container,
            text="Em imagens coloridas, as curvas representam os canais azul, verde e vermelho.",
        ).pack(anchor="w", pady=(8, 0))
