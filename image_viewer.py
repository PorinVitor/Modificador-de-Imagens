"""Componente Tkinter para visualizar imagens com zoom, pan e inspeção de pixels."""

from __future__ import annotations

import tkinter as tk
from collections.abc import Callable
from tkinter import ttk

import cv2
import numpy as np
from PIL import Image, ImageTk

PixelCallback = Callable[[int, int, np.ndarray | np.generic], None]


class ImageViewer(ttk.Frame):
    """Exibe uma imagem OpenCV em um Canvas rolável."""

    MIN_ZOOM = 0.1
    MAX_ZOOM = 8.0
    ZOOM_STEP = 1.25

    def __init__(
        self,
        master: tk.Misc,
        empty_text: str,
        pixel_callback: PixelCallback | None = None,
    ) -> None:
        super().__init__(master)
        self.image: np.ndarray | None = None
        self.photo: ImageTk.PhotoImage | None = None
        self.zoom = 1.0
        self.empty_text = empty_text
        self.pixel_callback = pixel_callback
        self._fit_after_id: str | None = None

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        toolbar = ttk.Frame(self)
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        toolbar.columnconfigure(1, weight=1)
        ttk.Button(toolbar, text="−", width=3, command=self.zoom_out).grid(row=0, column=0)
        self.zoom_text = ttk.Label(toolbar, text="100%", anchor="center")
        self.zoom_text.grid(row=0, column=1, sticky="ew")
        ttk.Button(toolbar, text="+", width=3, command=self.zoom_in).grid(row=0, column=2)
        ttk.Button(toolbar, text="Ajustar", command=self.fit_to_window).grid(
            row=0, column=3, padx=(6, 0)
        )

        canvas_frame = ttk.Frame(self)
        canvas_frame.grid(row=1, column=0, sticky="nsew")
        canvas_frame.columnconfigure(0, weight=1)
        canvas_frame.rowconfigure(0, weight=1)

        self.canvas = tk.Canvas(
            canvas_frame,
            background="#20242b",
            highlightthickness=0,
            cursor="fleur",
        )
        horizontal = ttk.Scrollbar(canvas_frame, orient="horizontal", command=self.canvas.xview)
        vertical = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=horizontal.set, yscrollcommand=vertical.set)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        vertical.grid(row=0, column=1, sticky="ns")
        horizontal.grid(row=1, column=0, sticky="ew")

        self.canvas.bind("<ButtonPress-1>", self._start_pan)
        self.canvas.bind("<B1-Motion>", self._pan)
        self.canvas.bind("<Motion>", self._report_pixel)
        self.canvas.bind("<MouseWheel>", self._mouse_wheel)
        self.canvas.bind("<Button-4>", lambda event: self._zoom_at(event, self.ZOOM_STEP))
        self.canvas.bind("<Button-5>", lambda event: self._zoom_at(event, 1 / self.ZOOM_STEP))
        self.canvas.bind("<Configure>", self._schedule_initial_fit)
        self._draw_empty_message()

    def set_image(self, image: np.ndarray, fit: bool = False) -> None:
        """Atualiza a imagem, preservando o zoom ou ajustando-a à janela."""
        self.image = image.copy()
        if fit:
            self.after_idle(self.fit_to_window)
        else:
            self._render()

    def clear(self) -> None:
        self.image = None
        self.photo = None
        self.zoom = 1.0
        self._draw_empty_message()

    def zoom_in(self) -> None:
        self._set_zoom(self.zoom * self.ZOOM_STEP)

    def zoom_out(self) -> None:
        self._set_zoom(self.zoom / self.ZOOM_STEP)

    def fit_to_window(self) -> None:
        if self.image is None:
            return
        self.update_idletasks()
        image_height, image_width = self.image.shape[:2]
        available_width = max(self.canvas.winfo_width() - 8, 1)
        available_height = max(self.canvas.winfo_height() - 8, 1)
        self.zoom = min(
            available_width / image_width,
            available_height / image_height,
            1.0,
        )
        self._render()
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)

    def _set_zoom(self, value: float) -> None:
        if self.image is None:
            return
        self.zoom = min(max(value, self.MIN_ZOOM), self.MAX_ZOOM)
        self._render()

    def _render(self) -> None:
        if self.image is None:
            self._draw_empty_message()
            return

        image_height, image_width = self.image.shape[:2]
        display_width = max(1, round(image_width * self.zoom))
        display_height = max(1, round(image_height * self.zoom))
        rgb = self._to_rgb(self.image)
        pil_image = Image.fromarray(rgb).resize(
            (display_width, display_height), Image.Resampling.LANCZOS
        )
        self.photo = ImageTk.PhotoImage(pil_image)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.photo, tags="image")
        self.canvas.configure(scrollregion=(0, 0, display_width, display_height))
        self.zoom_text.configure(text=f"{self.zoom * 100:.0f}%")

    def _draw_empty_message(self) -> None:
        self.canvas.delete("all")
        width = max(self.canvas.winfo_width(), 320)
        height = max(self.canvas.winfo_height(), 240)
        self.canvas.create_text(
            width / 2,
            height / 2,
            text=self.empty_text,
            fill="#d7dce2",
            font=("TkDefaultFont", 11),
            tags="empty",
        )
        self.canvas.configure(scrollregion=(0, 0, width, height))
        self.zoom_text.configure(text="—")

    def _start_pan(self, event: tk.Event) -> None:
        self.canvas.scan_mark(event.x, event.y)

    def _pan(self, event: tk.Event) -> None:
        self.canvas.scan_dragto(event.x, event.y, gain=1)
        self._report_pixel(event)

    def _mouse_wheel(self, event: tk.Event) -> str:
        factor = self.ZOOM_STEP if event.delta > 0 else 1 / self.ZOOM_STEP
        return self._zoom_at(event, factor)

    def _zoom_at(self, event: tk.Event, factor: float) -> str:
        if self.image is None:
            return "break"
        source_x = self.canvas.canvasx(event.x) / self.zoom
        source_y = self.canvas.canvasy(event.y) / self.zoom
        self._set_zoom(self.zoom * factor)
        bounds = self.canvas.bbox("all")
        if bounds is not None:
            display_width = max(bounds[2] - bounds[0], 1)
            display_height = max(bounds[3] - bounds[1], 1)
            left = max(source_x * self.zoom - event.x, 0)
            top = max(source_y * self.zoom - event.y, 0)
            self.canvas.xview_moveto(left / display_width)
            self.canvas.yview_moveto(top / display_height)
        return "break"

    def _report_pixel(self, event: tk.Event) -> None:
        if self.image is None or self.pixel_callback is None:
            return
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        x, y = self.canvas_to_image(canvas_x, canvas_y, self.zoom)
        height, width = self.image.shape[:2]
        if 0 <= x < width and 0 <= y < height:
            self.pixel_callback(x, y, self.image[y, x])

    def _schedule_initial_fit(self, _event: tk.Event) -> None:
        if self.image is None:
            self._draw_empty_message()
        elif self._fit_after_id is None:
            self._fit_after_id = self.after(80, self._finish_scheduled_fit)

    def _finish_scheduled_fit(self) -> None:
        self._fit_after_id = None
        if self.image is not None and self.photo is None:
            self.fit_to_window()

    @staticmethod
    def canvas_to_image(canvas_x: float, canvas_y: float, zoom: float) -> tuple[int, int]:
        """Converte coordenadas do Canvas nas coordenadas do pixel original."""
        if zoom <= 0:
            raise ValueError("O zoom deve ser maior que zero.")
        return int(canvas_x / zoom), int(canvas_y / zoom)

    @staticmethod
    def _to_rgb(image: np.ndarray) -> np.ndarray:
        if image.ndim == 2:
            return cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        return cv2.cvtColor(image[:, :, :3], cv2.COLOR_BGR2RGB)
