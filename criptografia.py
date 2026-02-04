import os
import random
import time
from operator import xor

# ==============================================================================
# FUNÇÕES AUXILIARES
# ==============================================================================

def xor_listas(a, b):
    return list(map(xor, a, b))

def rotacionar_esquerda(bits, k):
    if not bits:
        return bits
    k %= len(bits)
    return bits[k:] + bits[:k]

def gerar_permutacoes(tamanho):
    perm = [(i * 13 + 5) % tamanho for i in range(tamanho)]
    inv = [0] * tamanho
    for i, p in enumerate(perm):
        inv[p] = i
    return perm, inv

def permutar(bits, perm):
    return [bits[i] for i in perm]

def desmutar(bits, inv):
    return [bits[i] for i in inv]

# ==============================================================================
# S-BOX
# ==============================================================================

SBOX = [
    0xE, 0x4, 0xD, 0x1,
    0x2, 0xF, 0xB, 0x8,
    0x3, 0xA, 0x6, 0xC,
    0x5, 0x9, 0x0, 0x7
]

def aplicar_sbox(bits):
    resultado = []
    for i in range(0, len(bits), 4):
        bloco = bits[i:i+4]
        if len(bloco) < 4:
            resultado.extend(bloco)
            continue
        valor = (bloco[0] << 3) | (bloco[1] << 2) | (bloco[2] << 1) | bloco[3]
        substituido = SBOX[valor]
        resultado.extend([
            (substituido >> 3) & 1,
            (substituido >> 2) & 1,
            (substituido >> 1) & 1,
            substituido & 1
        ])
    return resultado

# ==============================================================================
# GEN
# ==============================================================================

def GEN(seed):
    tamanho_alvo = 4 * len(seed)
    K = list(seed)
    desloc = sum(seed) % len(seed)

    salt_base = rotacionar_esquerda(seed, desloc)
    for i in range(len(seed)):
        salt_base[i] ^= seed[(i * 3) % len(seed)]

    salt = salt_base * (tamanho_alvo // len(seed) + 1)

    while len(K) < tamanho_alvo:
        bloco = xor_listas(K, salt[:len(K)])
        K.extend(rotacionar_esquerda(bloco, 3))

    return K[:tamanho_alvo]

# ==============================================================================
# FEISTEL
# ==============================================================================

def feistel(lado, subchave, perm):
    mistura = xor_listas(lado, subchave)
    for i in range(1, len(mistura)):
        mistura[i] ^= mistura[i - 1]
    mistura = aplicar_sbox(mistura)
    return permutar(mistura, perm)

# ==============================================================================
# ENC / DEC
# ==============================================================================

def ENC(K, M):
    metade = len(M) // 2
    esquerda, direita = M[:metade], M[metade:]
    perm, _ = gerar_permutacoes(metade)

    rounds = 12 + (sum(K[:16]) % 5)

    for i in range(rounds):
        sub_k = rotacionar_esquerda(K, i * 7)[:metade]
        f = feistel(direita, sub_k, perm)
        esquerda, direita = direita, xor_listas(esquerda, f)

    bloco = esquerda + direita
    perm_full, _ = gerar_permutacoes(len(bloco))
    return xor_listas(permutar(bloco, perm_full), K)

def DEC(K, C):
    _, inv_full = gerar_permutacoes(len(C))
    bloco = desmutar(xor_listas(C, K), inv_full)

    metade = len(bloco) // 2
    esquerda, direita = bloco[:metade], bloco[metade:]
    perm, _ = gerar_permutacoes(metade)

    rounds = 12 + (sum(K[:16]) % 5)

    for i in range(rounds - 1, -1, -1):
        sub_k = rotacionar_esquerda(K, i * 7)[:metade]
        f = feistel(esquerda, sub_k, perm)
        direita, esquerda = esquerda, xor_listas(direita, f)

    return esquerda + direita

# ==============================================================================
# FUNÇÕES DE TESTE
# ==============================================================================

def gerar_lista_aleatoria(tamanho):
    num_bytes = (tamanho + 7) // 8
    dados = os.urandom(num_bytes)
    bits = []
    for byte in dados:
        for i in range(8):
            if len(bits) < tamanho:
                bits.append((byte >> i) & 1)
    return bits

def inverter_um_bit(lista):
    nova = list(lista)
    idx = random.randint(0, len(lista) - 1)
    nova[idx] ^= 1
    return nova

def calcular_diferenca(a, b):
    return sum(x != y for x, y in zip(a, b))

def teste_corretude():
    seed = gerar_lista_aleatoria(16)
    K = GEN(seed)
    M = gerar_lista_aleatoria(len(K))
    C = ENC(K, M)
    M_rec = DEC(K, C)
    print("CORRETUDE: [SUCESSO]" if M == M_rec else "RESULTADO: [FALHA]")

def teste_tempo():
    iteracoes = 1000
    seed = gerar_lista_aleatoria(16)
    M = gerar_lista_aleatoria(64)

    print(f"EXECUÇÕES POR TESTE: {iteracoes}")

    # -------- TEMPO GEN --------
    inicio_gen = time.time()
    for _ in range(iteracoes):
        K = GEN(seed)
    fim_gen = time.time()
    tempo_gen = (fim_gen - inicio_gen) / iteracoes

    # -------- TEMPO ENC --------
    K = GEN(seed)
    inicio_enc = time.time()
    for _ in range(iteracoes):
        C = ENC(K, M)
    fim_enc = time.time()
    tempo_enc = (fim_enc - inicio_enc) / iteracoes

    # -------- TEMPO DEC --------
    inicio_dec = time.time()
    for _ in range(iteracoes):
        DEC(K, C)
    fim_dec = time.time()
    tempo_dec = (fim_dec - inicio_dec) / iteracoes

    tempo_medio = (tempo_enc + tempo_dec)/2
    tempo_medio2 = (tempo_gen + tempo_enc + tempo_dec) / 3

    print(f"TEMPO GEN: {tempo_gen:.6f} segundos")
    print(f"TEMPO ENC: {tempo_enc:.6f} segundos")
    print(f"TEMPO DEC: {tempo_dec:.6f} segundos")
    print(f"TEMPO MÉDIO (ENC + DEC): {tempo_medio:.6f} segundos")
    print(f"TEMPO MÉDIO (GEN + ENC + DEC): {tempo_medio2:.6f} segundos")

def teste_chaves_equivalentes():
    quantidade = 500
    M = gerar_lista_aleatoria(64)
    cifras = {}
    colisoes = 0

    for _ in range(quantidade):
        K = tuple(GEN(gerar_lista_aleatoria(16)))
        C = tuple(ENC(list(K), M))
        if C in cifras and cifras[C] != K:
            colisoes += 1
        cifras[C] = K

    print(f"CHAVES EQUIVALENTES: {colisoes}")

def teste_difusao():
    repeticoes = 100
    K = GEN(gerar_lista_aleatoria(16))
    soma = 0

    for _ in range(repeticoes):
        M1 = gerar_lista_aleatoria(64)
        M2 = inverter_um_bit(M1)
        C1, C2 = ENC(K, M1), ENC(K, M2)
        soma += (calcular_diferenca(C1, C2) / 64) * 100

    print(f"DIFUSÃO: {soma / repeticoes:.2f}%")

def teste_confusao():
    repeticoes = 100
    M = gerar_lista_aleatoria(64)
    soma = 0

    for _ in range(repeticoes):
        s1 = gerar_lista_aleatoria(16)
        s2 = inverter_um_bit(s1)
        C1 = ENC(GEN(s1), M)
        C2 = ENC(GEN(s2), M)
        soma += (calcular_diferenca(C1, C2) / 64) * 100

    print(f"CONFUSÃO: {soma / repeticoes:.2f}%")

# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    teste_corretude()
    teste_tempo()
    teste_chaves_equivalentes()
    teste_difusao()
    teste_confusao()
