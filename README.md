# Implementação de Esquema Criptográfico Simplificado

Implementação em Python de uma cifra de bloco simétrica baseada em **rede de Feistel**.

## Estrutura do Algoritmo

### Componentes Principais

| Componente | Descrição |
|------------|-----------|
| **GEN** | Expansão de chave - transforma uma seed de 16 bits em uma chave expandida de 64 bits |
| **ENC** | Criptografa uma mensagem usando a rede de Feistel |
| **DEC** | Descriptografa o texto cifrado, revertendo as operações de ENC |
| **S-Box** | Substituição não-linear de 4 bits para aumentar a confusão |

### Funções Auxiliares

- `xor_listas`: Operação XOR entre duas listas de bits
- `rotacionar_esquerda`: Rotação circular à esquerda
- `gerar_permutacoes`: Gera permutação e sua inversa para difusão
- `permutar` / `desmutar`: Aplica e reverte permutações

## Como Funciona

### 1. Geração de Chave (GEN)

A função `GEN` expande uma seed de 16 bits para uma chave de 64 bits através de:
- Rotação baseada na soma dos bits da seed
- Aplicação de XOR com salt derivado
- Expansão iterativa até atingir o tamanho alvo

### 2. Criptografia (ENC)

A rede de Feistel executa entre **12 a 16 rounds** (variável conforme a chave):

1. Divide a mensagem em metades (esquerda e direita)
2. Em cada round:
   - Aplica a função Feistel na metade direita
   - Faz XOR do resultado com a metade esquerda
   - Troca as metades
3. Aplica permutação e XOR final com a chave

### 3. Descriptografia (DEC)

A função `DEC` reverte as operações de `ENC` na ordem inversa:

1. Reverte o XOR final com a chave
2. Desfaz a permutação usando a permutação inversa (`desmutar`)
3. Divide o bloco em metades (esquerda e direita)
4. Executa os rounds em **ordem reversa** (do último ao primeiro):
   - Aplica a função Feistel na metade esquerda
   - Faz XOR do resultado com a metade direita
   - Troca as metades
5. Concatena as metades para recuperar a mensagem original

A propriedade da rede de Feistel garante que a mesma função `feistel` usada na criptografia pode ser usada na descriptografia, apenas invertendo a ordem dos rounds.

### 4. Função Feistel

Combina múltiplas operações para máxima difusão:
- XOR com subchave do round
- Encadeamento de bits (cada bit depende do anterior)
- Substituição via S-Box
- Permutação de bits

## Uso

```python
from criptografia import GEN, ENC, DEC, gerar_lista_aleatoria

# Gerar seed aleatória de 16 bits
seed = gerar_lista_aleatoria(16)

# Expandir para chave de 64 bits
K = GEN(seed)

# Mensagem como lista de bits (mesmo tamanho da chave)
M = gerar_lista_aleatoria(64)

# Criptografar
C = ENC(K, M)

# Descriptografar
M_recuperada = DEC(K, C)

assert M == M_recuperada  # Verifica corretude
```

## Testes Incluídos

Execute o arquivo diretamente para rodar a suíte de testes:

```bash
python criptografia.py
```

| Teste | Descrição |
|-------|-----------|
| **Corretude** | Verifica se `DEC(K, ENC(K, M)) == M` |
| **Tempo** | Mede performance de GEN, ENC e DEC |
| **Chaves Equivalentes** | Detecta colisões entre chaves diferentes |
| **Difusão** | Mede quantos bits do cifrado mudam ao alterar 1 bit da mensagem |
| **Confusão** | Mede quantos bits do cifrado mudam ao alterar 1 bit da chave |

### Métricas Esperadas

- **Difusão**: ~50% (ideal para efeito avalanche)
- **Confusão**: ~50% (indica boa sensibilidade à chave)
- **Chaves Equivalentes**: 0 (nenhuma colisão)

## S-Box

A substituição não-linear usa uma S-Box de 4 bits:

```
Entrada:  0  1  2  3  4  5  6  7  8  9  A  B  C  D  E  F
Saída:    E  4  D  1  2  F  B  8  3  A  6  C  5  9  0  7
```

## Requisitos

- Python 3.10.13
- Apenas bibliotecas padrão (`os`, `random`, `time`, `operator`)

