"""Aplicativo desktop para aplicar filtros OpenCV e inspecionar imagens."""

from __future__ import annotations

import tkinter as tk
from collections.abc import Callable
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import cv2
import numpy as np

from histogram_window import HistogramWindow
from image_filters import FILTERS
from image_viewer import ImageViewer

SUPPORTED_FILES = [
    ("Imagens", "*.png *.jpg *.jpeg *.bmp *.tif *.tiff *.webp"),
    ("Todos os arquivos", "*.*"),
]


class ImageModifierApp:
    """Janela principal e estado da edição."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Modificador de Imagens — OpenCV")
        self.root.geometry("1320x800")
        self.root.minsize(980, 650)

        self.original_image: np.ndarray | None = None
        self.current_image: np.ndarray | None = None
        self.current_path: Path | None = None

        self.status = tk.StringVar(value="Carregue uma imagem para começar.")
        self.pixel_info = tk.StringVar(
            value="Passe o cursor sobre uma imagem para consultar a posição e o valor do pixel."
        )
        self._configure_style()
        self._build_interface()

    def _configure_style(self) -> None:
        style = ttk.Style()
        if "clam" in style.theme_names():
            style.theme_use("clam")
        style.configure("Title.TLabel", font=("TkDefaultFont", 18, "bold"))
        style.configure("Subtitle.TLabel", font=("TkDefaultFont", 11))
        style.configure("Filter.TButton", padding=(10, 7))
        style.configure("Action.TButton", padding=(12, 8), font=("TkDefaultFont", 10, "bold"))
        style.configure("Pixel.TLabel", padding=(8, 5), background="#e9eef5")

    def _build_interface(self) -> None:
        container = ttk.Frame(self.root, padding=16)
        container.pack(fill="both", expand=True)
        container.columnconfigure(1, weight=1)
        container.rowconfigure(1, weight=1)

        header = ttk.Frame(container)
        header.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 14))
        header.columnconfigure(0, weight=1)
        ttk.Label(header, text="Modificador de Imagens", style="Title.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        ttk.Label(
            header,
            text="Tratamentos OpenCV com zoom, inspeção de pixels e histograma.",
            style="Subtitle.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(3, 0))
        ttk.Button(header, text="Abrir imagem", command=self.open_image, style="Action.TButton").grid(
            row=0, column=1, rowspan=2, padx=(12, 0)
        )

        menu = ttk.LabelFrame(container, text="Operações", padding=10)
        menu.grid(row=1, column=0, sticky="ns", padx=(0, 14))
        canvas = tk.Canvas(menu, width=220, highlightthickness=0)
        scrollbar = ttk.Scrollbar(menu, orient="vertical", command=canvas.yview)
        buttons_frame = ttk.Frame(canvas)
        buttons_frame.bind(
            "<Configure>", lambda _event: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=buttons_frame, anchor="nw", width=210)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="y")
        scrollbar.pack(side="right", fill="y")

        for row, (name, operation) in enumerate(FILTERS.items()):
            ttk.Button(
                buttons_frame,
                text=name,
                command=lambda label=name, function=operation: self.apply_filter(label, function),
                style="Filter.TButton",
            ).grid(row=row, column=0, sticky="ew", pady=3)
        buttons_frame.columnconfigure(0, weight=1)

        workspace = ttk.Frame(container)
        workspace.grid(row=1, column=1, sticky="nsew")
        workspace.columnconfigure((0, 1), weight=1, uniform="preview")
        workspace.rowconfigure(0, weight=1)

        original_frame = ttk.LabelFrame(workspace, text="Imagem original", padding=8)
        original_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        result_frame = ttk.LabelFrame(workspace, text="Resultado", padding=8)
        result_frame.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
        original_frame.rowconfigure(0, weight=1)
        original_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)
        result_frame.columnconfigure(0, weight=1)

        self.original_viewer = ImageViewer(
            original_frame,
            "Nenhuma imagem carregada",
            lambda x, y, value: self._show_pixel("Original", x, y, value),
        )
        self.original_viewer.grid(row=0, column=0, sticky="nsew")
        self.result_viewer = ImageViewer(
            result_frame,
            "O resultado aparecerá aqui",
            lambda x, y, value: self._show_pixel("Resultado", x, y, value),
        )
        self.result_viewer.grid(row=0, column=0, sticky="nsew")

        actions = ttk.Frame(workspace)
        actions.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(12, 0))
        ttk.Button(actions, text="Restaurar original", command=self.restore_original).pack(side="left")
        ttk.Button(actions, text="Exibir histogramas", command=self.show_histograms).pack(
            side="left", padx=(8, 0)
        )
        ttk.Button(actions, text="Salvar resultado", command=self.save_image).pack(side="right")

        ttk.Label(container, textvariable=self.pixel_info, style="Pixel.TLabel").grid(
            row=2, column=0, columnspan=2, sticky="ew", pady=(12, 6)
        )
        ttk.Label(container, textvariable=self.status).grid(
            row=3, column=0, columnspan=2, sticky="w"
        )

    def open_image(self) -> None:
        filename = filedialog.askopenfilename(title="Escolha uma imagem", filetypes=SUPPORTED_FILES)
        if not filename:
            return
        image = cv2.imread(filename, cv2.IMREAD_COLOR)
        if image is None:
            messagebox.showerror("Erro", "O OpenCV não conseguiu abrir o arquivo selecionado.")
            return

        self.current_path = Path(filename)
        self.original_image = image
        self.current_image = image.copy()
        self.original_viewer.set_image(self.original_image, fit=True)
        self.result_viewer.set_image(self.current_image, fit=True)
        height, width = image.shape[:2]
        self.status.set(f"{self.current_path.name} — {width} × {height} pixels")

    def apply_filter(self, name: str, operation: Callable[[np.ndarray], np.ndarray]) -> None:
        if self.current_image is None:
            messagebox.showwarning("Imagem necessária", "Carregue uma imagem antes de aplicar um filtro.")
            return
        try:
            self.current_image = operation(self.current_image)
            self.result_viewer.set_image(self.current_image)
            self.status.set(f"Operação aplicada: {name}. As alterações são cumulativas.")
        except (cv2.error, ValueError) as error:
            messagebox.showerror("Erro no processamento", str(error))

    def restore_original(self) -> None:
        if self.original_image is None:
            messagebox.showwarning("Imagem necessária", "Ainda não há uma imagem para restaurar.")
            return
        self.current_image = self.original_image.copy()
        self.result_viewer.set_image(self.current_image, fit=True)
        self.status.set("A imagem original foi restaurada.")

    def show_histograms(self) -> None:
        if self.original_image is None or self.current_image is None:
            messagebox.showwarning("Imagem necessária", "Carregue uma imagem para exibir o histograma.")
            return
        HistogramWindow(self.root, self.original_image, self.current_image)

    def save_image(self) -> None:
        if self.current_image is None:
            messagebox.showwarning("Imagem necessária", "Não há resultado para salvar.")
            return
        default_name = f"{self.current_path.stem}_modificada.png" if self.current_path else "resultado.png"
        filename = filedialog.asksaveasfilename(
            title="Salvar imagem modificada",
            defaultextension=".png",
            initialfile=default_name,
            filetypes=SUPPORTED_FILES,
        )
        if not filename:
            return
        if not cv2.imwrite(filename, self.current_image):
            messagebox.showerror("Erro", "Não foi possível salvar a imagem no caminho escolhido.")
            return
        self.status.set(f"Imagem salva em: {filename}")

    def _show_pixel(self, source: str, x: int, y: int, value: np.ndarray | np.generic) -> None:
        if np.ndim(value) == 0:
            description = f"Cinza={int(value)}"
        else:
            blue, green, red = (int(channel) for channel in value[:3])
            description = f"B={blue}  G={green}  R={red}"
        self.pixel_info.set(f"{source} — X={x}  Y={y}  |  {description}")


def main() -> None:
    root = tk.Tk()
    ImageModifierApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
