# Modificador de Imagens com OpenCV

Aplicativo desktop educacional em Python para carregar uma imagem, aplicar operações de processamento com botões e salvar o resultado. A interface usa **Tkinter**, o processamento usa **OpenCV** e as prévias usam **Pillow**.

## Funcionalidades

- abrir imagens PNG, JPEG, BMP, TIFF e WebP;
- visualizar lado a lado a imagem original e o resultado;
- ampliar, reduzir, ajustar à janela e movimentar cada imagem;
- consultar coordenadas e valores BGR/cinza ao passar o cursor sobre um pixel;
- comparar os histogramas da imagem original e do resultado atual;
- aplicar operações sucessivas (o resultado de um botão é a entrada do próximo);
- restaurar a imagem original;
- salvar o resultado em um novo arquivo;
- mensagens amigáveis quando nenhuma imagem foi carregada ou ocorre um erro.

### Operações disponíveis

| Grupo | Operações |
| --- | --- |
| Cores | tons de cinza, canais azul/verde/vermelho e troca vermelho/azul com `split`/`merge` |
| Histograma e suavização | filtro de mediana e equalização de histograma |
| Morfologia | erosão, dilatação, abertura, fechamento, gradiente morfológico e Top Hat |
| Realce em cinza | abertura em cinza e fechamento em cinza |
| Ruído | remoção de pequenos pontos claros por abertura morfológica |

## Instalação passo a passo

### 1. Instale o Python

Use Python 3.10 ou mais recente. No Windows, marque **Add Python to PATH** durante a instalação.

### 2. Abra um terminal na pasta do projeto

```bash
cd Modificador-de-Imagens
```

### 3. Crie um ambiente virtual

Windows (Prompt de Comando):

```bat
python -m venv .venv
.venv\Scripts\activate
```

Linux ou macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Em algumas distribuições Linux, o Tkinter precisa ser instalado pelo sistema:

```bash
sudo apt install python3-tk
```

### 4. Instale as dependências

```bash
python -m pip install -r requirements.txt
```

### 5. Execute o aplicativo

```bash
python app.py
```

## Como usar

1. Clique em **Abrir imagem**.
2. Escolha uma imagem compatível.
3. Clique em uma operação no menu esquerdo.
4. Observe o resultado à direita.
5. Aplique outros filtros se desejar. Eles são **cumulativos**.
6. Use os botões **+**, **−** ou **Ajustar** para controlar o zoom de cada visualização.
7. Arraste uma imagem com o botão esquerdo do mouse para movimentá-la quando estiver ampliada. A roda do mouse também controla o zoom.
8. Passe o cursor sobre a imagem para ver `X`, `Y` e os valores `B`, `G`, `R` ou o nível de cinza do pixel.
9. Clique em **Exibir histogramas** para comparar a distribuição de intensidades da original e do resultado.
10. Use **Restaurar original** para descartar as modificações.
11. Clique em **Salvar resultado** e escolha o nome e o formato do arquivo.

### Como interpretar o histograma

- O eixo horizontal representa as intensidades de `0` (escuro) a `255` (claro).
- O eixo vertical representa a quantidade de pixels em cada intensidade.
- Imagens coloridas exibem curvas separadas para os canais azul, verde e vermelho.
- Imagens em tons de cinza exibem uma única curva.
- A janela possui abas para comparar a imagem original com o resultado atual.

> Os tamanhos dos elementos estruturantes são inicialmente valores didáticos fixos. Uma próxima evolução pode adicionar controles para tamanho, formato e número de iterações.

## Organização do projeto

```text
.
├── app.py                    # Interface Tkinter e integração com os filtros
├── histogram_window.py       # Gráfico de histograma original/resultado
├── image_filters.py          # Funções de processamento OpenCV
├── image_viewer.py           # Zoom, pan e inspeção de pixels
├── requirements.txt          # Dependências Python
└── tests/
    ├── test_image_filters.py # Testes das operações e histogramas
    └── test_image_viewer.py  # Testes da conversão de coordenadas
```

## Análise e correções dos códigos recebidos

Os exemplos enviados continham a ideia correta das operações, mas **não funcionariam todos como estavam escritos**. As principais correções realizadas foram:

1. **Aspas tipográficas:** caracteres como `”` foram substituídos por aspas normais (`"`). Python não reconhece aspas de editor de texto como delimitadores.
2. **Importação incompleta:** vários trechos tinham `mport cv2` em vez de `import cv2`.
3. **Leitura da imagem:** agora a imagem é escolhida na interface e a falha de leitura é verificada. Não dependemos de um nome fixo como `Entrada.bmp`.
4. **Filtro de mediana:** o exemplo criava `imgFiltroMediana`, mas tentava salvar `imagem_filtrada`, variável inexistente. A função agora devolve o resultado correto. O kernel também é validado como ímpar e maior que 1.
5. **Erosão:** faltava uma vírgula em `cv2.erode(imOriginal, eEstruturante, ...)`.
6. **Linhas unidas a comentários:** em vários exemplos, `import`, `imshow`, `waitKey` ou `imwrite` ficaram depois de `#` e, portanto, seriam ignorados pelo Python.
7. **Salvamento:** chamadas como `cv2.imwrite("Imagem processada", imProc)` não informavam extensão. Na interface, o usuário escolhe um nome com extensão válida.
8. **Top Hat:** faltava fechar o parêntese de `cv2.add(imProc, imProc)`.
9. **Abertura/fechamento em cinza:** o nome `Entradabmp` não tinha ponto; o kernel `100 × 100` era par e excessivamente grande para muitas imagens. Foram usados kernels ímpares e menores como padrão.
10. **Gradiente morfológico:** o gradiente já é o resultado de interesse. A subtração adicional do original não é necessária para destacar contornos e poderia produzir um significado diferente.
11. **Eliminação de ruído:** erosão isolada reduz regiões claras, mas também encolhe objetos. A implementação usa **abertura** (erosão seguida de dilatação), normalmente mais adequada para remover pequenos pontos claros preservando melhor os objetos.
12. **Equalização colorida:** `cv2.equalizeHist` aceita apenas um canal. Para imagens coloridas, a implementação converte para YCrCb e equaliza somente a luminância, evitando equalizar B, G e R separadamente e distorcer muito as cores.
13. **Split e merge:** separar e reunir os canais sem alterá-los produz uma imagem igual à original. Por isso, a interface oferece botões para visualizar cada canal e outro exemplo que troca vermelho e azul antes do `merge`.
14. **NumPy:** não era necessário em todos os exemplos, mas é usado na visualização isolada dos canais e nos tipos de imagem.

## Sobre as etapas de processamento de imagens

Os nomes enviados representam um fluxo geral, e não filtros individuais:

1. **Aquisição:** obter a imagem (arquivo, câmera, scanner etc.). Neste projeto, ocorre ao clicar em **Abrir imagem**.
2. **Pré-processamento:** melhorar ou normalizar a imagem, por exemplo com mediana, equalização e remoção de ruído.
3. **Segmentação:** separar regiões ou objetos relevantes. Ainda não foi implementada; exemplos futuros incluem limiarização e detecção de contornos.
4. **Representação e descrição:** transformar regiões segmentadas em medidas, como área, perímetro, centro e descritores.
5. **Reconhecimento:** atribuir uma classe ou identidade ao objeto, geralmente com regras, características ou aprendizado de máquina.

A interface atual cobre aquisição e várias operações de pré-processamento. Segmentação, descrição e reconhecimento podem ser acrescentados como próximas etapas.

## Testes

```bash
python -m unittest discover -s tests -v
```
