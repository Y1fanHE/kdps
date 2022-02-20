<!--
 * @Author: He,Yifan
 * @Date: 2022-02-17 16:13:21
 * @LastEditors: He,Yifan
 * @LastEditTime: 2022-02-20 15:56:57
-->

# Knowledge-Driven Program Synthesis

A convenient tool for experiments on knowledge-driven program synthesis based on
[PyshGP](https://github.com/erp12/pyshgp)

## Installation

1. install pgsyn

    ```bash
    git clone https://github.com/Y1fanHE/kdps.git
    cd kdps
    pip install --editable .
    ```

## Usage

See the following example.

1. Download dataset of PSB1 and put the folder into `example/psb1`.

2. The YAML config files of problems and algorithms are in
   `example/psb1/problem_cfg` and `example/psb1/algorithm_cfg`.

```bash
cd example/psb1
# python -m run [problem] [algorithm]
# the following command runs the algorithm in umad.yml
# to solve the problem in number-io.yml
python -m run number-io umad
```
