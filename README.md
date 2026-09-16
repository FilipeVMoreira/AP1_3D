# AP1 Animação 3D

Projeto de animação 3D em Python com Pygame, desenvolvido como atividade prática de Computação Gráfica e RA/RV.

O programa cria uma cena de caverna com:
- ambiente 3D em perspectiva;
- chão, paredes e teto simulados;
- estalagmites e estalactites;
- morcego animado com asas em batimento;
- rocha rolando até cair em um buraco;
- alternância de câmera entre visão geral e foco no morcego;
- modo wireframe;
- tela de créditos.

## Requisitos

- Python 3.10 ou superior
- pip
- Sistema operacional: Windows, Linux ou macOS

## Dependências

O projeto utiliza a biblioteca:
- pygame

Instale a dependência com:

```bash
python -m pip install pygame
```

## Estrutura do projeto

```text
AP1_3D/
├── main.py
├── README.md
├── models/
│   ├── Stalagmite_Medium0.obj
│   ├── bat_corpo.obj
│   ├── bat_asa_esquerda.obj
│   ├── bat_asa_direita.obj
│   └── rockmaterial.obj
└── ...
```

A pasta `models/` contém os modelos 3D utilizados na cena. Caso algum arquivo OBJ não seja encontrado, o programa usa uma malha procedural de fallback para evitar erros.

## Como executar

1. Abra o terminal no diretório do projeto.
2. Verifique se o Python está instalado:

```bash
python --version
```

3. Execute o programa:

```bash
python main.py
```

Se o comando `python` não funcionar no seu sistema, tente:

```bash
python3 main.py
```

## Controles

Durante a execução, os principais comandos são:

- Espaço: iniciar/pausar a animação
- R: reiniciar a animação
- C: alternar entre câmera geral e foco no morcego
- M: alternar entre visual sólido e wireframe
- V: abrir/fechar a tela de créditos
- ESC: sair do programa

## Observações importantes

- O projeto precisa da pasta `models/` no diretório raiz.
- Certifique-se de que os arquivos OBJ existem com os nomes esperados.
- O programa foi desenvolvido para execução local e requer uma janela gráfica do sistema.

## Solução de problemas comuns

### Erro: `No module named pygame`

Instale a biblioteca necessária:

```bash
python -m pip install pygame
```

### Erro ao iniciar: modelo OBJ não encontrado

Verifique se a pasta `models/` está presente no projeto e se os arquivos estão com os nomes corretos:

- `Stalagmite_Medium0.obj`
- `bat_corpo.obj`
- `bat_asa_esquerda.obj`
- `bat_asa_direita.obj`
- `rockmaterial.obj`

### O programa abre e fecha imediatamente

Confirme que você está executando o arquivo correto dentro do diretório do projeto:

```bash
python main.py
```

## Licença

Este projeto foi desenvolvido para fins acadêmicos como atividade de avaliação da disciplina de Computação Gráfica e RA/RV.

## Autores

- Guilherme Pinheiro
- Filipe Moreira
- Gabriel Macedo
- Cauan Lemos
