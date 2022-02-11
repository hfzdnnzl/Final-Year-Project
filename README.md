# GAN Video Conferencing

GAN Video Conferencing is my final year project at Universiti Malaya. The purpose is to use GAN to perform facial reenactment that will reduce the bandwidth in video conferencing. The main idea is that only facial landmarks will be transferred in video conferencing instead of a whole video frame. The facial reenactment process is done on the local computer. The GANnotation model is used in this work.

## Software Dependencies

1. Python 3.7
2. Microsoft Visual Studio (Desktop Development with C++ Package)
3. CMake
4. NVIDIA CUDA Toolkit (10.2 or 11.3)
5. NVIDIA cuDNN

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the libraries.

```bash
pip install opencv-python dlib numpy PyQt5 socket struct pickle time
```

To install pyaudio library, click [here](https://stackoverflow.com/questions/52283840/i-cant-install-pyaudio-on-windows-how-to-solve-error-microsoft-visual-c-14) for solution

To install torch library, you need to check your version and follow the documentation [here](https://pytorch.org/)

## Usage

Open command prompt in the working directory and run the code below.

```bash
python main.py
```

## Contributing
All contributions are welcome.

## References
[1] Enrique Sanchez and Michel Valstar (2020). A recurrent cycle consistency loss for progressive face-to-face synthesis. IEEE Int'l Conf. on Automatic Face and Gesture Recognition (FG) 

[Link to paper](https://arxiv.org/pdf/1811.03492.pdf)
