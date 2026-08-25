# Installation

## Installing from PyPI

jwpoint requires Python 3.11 or later. Install it from PyPI with:

```console
python -m pip install jwpoint
```

## Installing for development

Clone the repository and enter its directory:

```console
git clone https://github.com/vandalt/jwpoint.git
cd jwpoint
```

Install the package and development dependencies with
[uv](https://docs.astral.sh/uv/):

```console
uv sync
```

## Building the documentation

Build the HTML documentation with:

```console
uv run make -C docs html
```
