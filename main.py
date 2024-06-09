class Gramatica:
    def __init__(self, variaveis, terminais, simbolo_inicial, transicoes):
        self.variaveis = variaveis
        self.terminais = terminais
        self.simbolo_inicial = simbolo_inicial
        self.transicoes = self.ajustar_transicoes(transicoes)
        self.contador_z = 1

    def ajustar_transicoes(self, transicoes):
        novas_transicoes = {}
        for estado, destinos in transicoes.items():
            novas_transicoes[estado] = []
            for destino in destinos:
                nova_transicao = []
                i = 0
                while i < len(destino):
                    if destino[i] in self.variaveis:
                        nova_transicao.append(destino[i])
                    else:
                        terminal = ''
                        while i < len(destino) and destino[i] not in self.variaveis:
                            terminal += destino[i]
                            i += 1
                        nova_transicao.append(terminal)
                        continue
                    i += 1
                novas_transicoes[estado].append(nova_transicao)
        return novas_transicoes

    def adicionar_transicao(self, estado, destino):
        if estado in self.transicoes:
            self.transicoes[estado].append(destino)
        else:
            self.transicoes[estado] = [destino]

    def remover_transicao(self, estado, destino):
        if estado in self.transicoes:
            self.transicoes[estado].remove(destino)
            if not self.transicoes[estado]:
                del self.transicoes[estado]

    def remover_producoes_vazias(self):
        producoes_vazias = {estado for estado, destinos in self.transicoes.items() if ['eps'] in destinos}

        while producoes_vazias:
            estado_vazio = producoes_vazias.pop()
            self.transicoes[estado_vazio].remove(['eps'])
            if not self.transicoes[estado_vazio]:
                del self.transicoes[estado_vazio]

            for estado, destinos in list(self.transicoes.items()):
                novos_destinos = []
                for destino in destinos:
                    if estado_vazio in destino:
                        novas_producoes = [list(filter(lambda x: x != estado_vazio, destino))]
                        novos_destinos.extend(novas_producoes)
                    novos_destinos.append(destino)
                self.transicoes[estado] = [list(x) for x in set(tuple(x) for x in novos_destinos)]

            for estado in list(self.transicoes.keys()):
                if not self.transicoes[estado]:
                    del self.transicoes[estado]

        for estado in self.transicoes:
            self.transicoes[estado] = [list(x) for x in set(tuple(x) for x in self.transicoes[estado]) if x != []]

    def remover_producoes_unidade(self):
        producoes_unidade = {estado: [destino for destino in destinos if len(destino) == 1 and destino[0] in self.variaveis]
                             for estado, destinos in self.transicoes.items()}

        while any(producoes_unidade.values()):
            for estado, unidades in list(producoes_unidade.items()):
                for unidade in unidades:
                    if unidade[0] in self.transicoes:
                        for destino in self.transicoes[unidade[0]]:
                            if destino not in self.transicoes[estado]:
                                self.adicionar_transicao(estado, destino)
                    self.remover_transicao(estado, unidade)
                producoes_unidade[estado] = [destino for destino in self.transicoes.get(estado, []) if len(destino) == 1 and destino[0] in self.variaveis]

    def remover_transicoes_sem_destino(self):
        transicoes_sem_destino = [estado for estado, destinos in self.transicoes.items() if [] in destinos]

        for estado in transicoes_sem_destino:
            self.transicoes[estado].remove([])
            if not self.transicoes[estado]:
                del self.transicoes[estado]

    def remover_producoes_inuteis(self):
        alcancaveis = {self.simbolo_inicial}
        novos_alcancaveis = {self.simbolo_inicial}

        while novos_alcancaveis:
            estado = novos_alcancaveis.pop()
            for destino in self.transicoes.get(estado, []):
                for simbolo in destino:
                    if simbolo in self.variaveis and simbolo not in alcancaveis:
                        novos_alcancaveis.add(simbolo)
                        alcancaveis.add(simbolo)

        inuteis = set(self.variaveis) - alcancaveis
        for inutil in inuteis:
            if inutil in self.transicoes:
                del self.transicoes[inutil]

        for estado, destinos in list(self.transicoes.items()):
            novos_destinos = [destino for destino in destinos if all(simbolo not in inuteis for simbolo in destino)]
            self.transicoes[estado] = novos_destinos

    def exibir_gramatica(self):
        print(f"Variáveis: {' '.join(self.variaveis)}")
        print(f"Terminais: {' '.join(self.terminais)}")
        print(f"Símbolo inicial: {self.simbolo_inicial}")
        print("Transições:")
        for estado, destinos in self.transicoes.items():
            for destino in destinos:
                print(f"{estado} {''.join(destino)}")

    def renomear_variaveis(self):
        variaveis_ordenadas = sorted(self.variaveis)
        mapa_renomeacao = {var: f'A{i+2}' for i, var in enumerate(variaveis_ordenadas)}

        mapa_renomeacao[self.simbolo_inicial] = 'A1'

        self.variaveis = ['A1'] + [mapa_renomeacao[var] for var in variaveis_ordenadas if var != self.simbolo_inicial]
        self.simbolo_inicial = 'A1'

        novas_transicoes = {}
        for estado, destinos in self.transicoes.items():
            novo_estado = mapa_renomeacao[estado]
            novas_transicoes[novo_estado] = []
            for destino in destinos:
                nova_transicao = [mapa_renomeacao[s] if s in mapa_renomeacao else s for s in destino]
                novas_transicoes[novo_estado].append(nova_transicao)

        self.transicoes = novas_transicoes

    def formatar_producoes(self):
        for estado in self.variaveis:
            novas_producoes = []
            for destino in self.transicoes.get(estado, []):
                while destino and destino[0] in self.variaveis and self.variaveis.index(destino[0]) < self.variaveis.index(estado):
                    prefixo = destino[0]
                    sufixo = destino[1:]
                    self.remover_transicao(estado, destino)
                    for d in self.transicoes[prefixo]:
                        novas_producoes.append(d + sufixo)
                    destino = []
                if destino:
                    novas_producoes.append(destino)
            self.transicoes[estado] = novas_producoes

    def exclusao_recursao_esquerda(self):
        novas_transicoes = {}

        for estado, destinos in list(self.transicoes.items()):

            recursivas = []
            nao_recursivas = []

            for destino in destinos:
                if destino[0] == estado:
                    recursivas.append(destino[1:])
                else:
                    nao_recursivas.append(destino)

            if recursivas:
                br = f'B{self.variaveis.index(estado) + 1}'
                self.variaveis.append(br)

                novas_transicoes[br] = []
                for rec in recursivas:
                    novas_transicoes[br].append(rec)
                    novas_transicoes[br].append(rec + [br])

                novas_transicoes[estado] = nao_recursivas.copy()
                for nr in nao_recursivas:
                    novas_transicoes[estado].append(nr + [br])
            else:
                novas_transicoes[estado] = destinos

        self.transicoes.update(novas_transicoes)

    def terminal_no_inicio(self):
        while True:
            encontrou = False
            novas_transicoes = {}
            for estado, destinos in self.transicoes.items():
                novas_transicoes[estado] = []
                for destino in destinos:
                    if destino[0] in self.variaveis:
                        encontrou = True
                        primeira_var = destino[0]
                        sufixo = destino[1:]
                        for sub_destino in self.transicoes[primeira_var]:
                            novas_transicoes[estado].append(sub_destino + sufixo)
                    else:
                        novas_transicoes[estado].append(destino)
            self.transicoes = novas_transicoes
            if not encontrou:
                break

        for estado in self.transicoes:
            self.transicoes[estado] = [list(x) for x in set(tuple(x) for x in self.transicoes[estado])]

        for estado in self.transicoes:
            self.transicoes[estado] = [destino for destino in self.transicoes[estado] if destino[0] not in self.variaveis]

    def encontrar_transicoes_fora_de_forma(self):
        transicoes_fora_de_forma = {}
        for estado, destinos in self.transicoes.items():
            for destino in destinos:
                if len(destino) > 1 and any(destino[i] in self.terminais for i in range(1, len(destino))):
                    if estado not in transicoes_fora_de_forma:
                        transicoes_fora_de_forma[estado] = []
                    transicoes_fora_de_forma[estado].append(destino)
        return transicoes_fora_de_forma

    def ajeitar_fng(self):
        transicoes_fora_de_forma = self.encontrar_transicoes_fora_de_forma()
        nova_variavel_index = 1
        novo_terminal_map = {}

        for estado, destinos in transicoes_fora_de_forma.items():
            for destino in destinos:
                nova_transicao = []
                for i, simbolo in enumerate(destino):
                    if i == 0 or simbolo in self.variaveis:
                        nova_transicao.append(simbolo)
                    else:
                        if simbolo not in novo_terminal_map:
                            nova_variavel = f'Z{nova_variavel_index}'
                            novo_terminal_map[simbolo] = nova_variavel
                            self.variaveis.append(nova_variavel)
                            self.transicoes[nova_variavel] = [[simbolo]]
                            nova_variavel_index += 1
                        nova_transicao.append(novo_terminal_map[simbolo])

                self.remover_transicao(estado, destino)
                self.adicionar_transicao(estado, nova_transicao)

    def converte_para_greibach(self):
        self.remover_producoes_vazias()
        self.remover_transicoes_sem_destino()
        self.remover_producoes_inuteis()
        print("\nGramatica limpa:")
        self.exibir_gramatica()
        print("\nFNG: ")
        self.renomear_variaveis()
        self.formatar_producoes()
        self.exclusao_recursao_esquerda()
        self.terminal_no_inicio()
        self.ajeitar_fng()


def ler_arquivo_gramatica(caminho):
    with open(caminho, 'r') as arquivo:
        linhas = arquivo.readlines()

    variaveis = []
    terminais = []
    simbolo_inicial = ''
    transicoes = {}

    secao_atual = None
    for linha in linhas:
        linha = linha.strip()
        if linha.startswith("Variaveis:"):
            secao_atual = "variaveis"
            variaveis = linha[len("Variaveis:"):].strip().split()
        elif linha.startswith("Terminais:"):
            secao_atual = "terminais"
            terminais = linha[len("Terminais:"):].strip().split()
        elif linha.startswith("Simbolo inicial:"):
            secao_atual = "simbolo_inicial"
            simbolo_inicial = linha[len("Simbolo inicial:"):].strip()
        elif linha.startswith("Transicoes:"):
            secao_atual = "transicoes"
        elif secao_atual == "transicoes":
            if linha:
                partes = linha.split(maxsplit=1)
                estado = partes[0]
                destino = partes[1] if len(partes) > 1 else ''
                if estado in transicoes:
                    transicoes[estado].append(destino)
                else:
                    transicoes[estado] = [destino]

    return Gramatica(variaveis, terminais, simbolo_inicial, transicoes)


def main(arquivo):
    gramatica = ler_arquivo_gramatica(arquivo)
    gramatica.converte_para_greibach()
    gramatica.exibir_gramatica()


if __name__ == "__main__":
    main('gramatica.txt')
