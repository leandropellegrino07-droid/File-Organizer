import os
import shutil
from pathlib import Path
from datetime import datetime
import json

# Pasta a organizar
PASTA = r"d:\\"

# Extensões de arquivo
TIPOS = {
    "Imagens": (".jpg", ".jpeg", ".png", ".gif", ".bmp"),
    "Documentos": (".pdf", ".doc", ".docx", ".txt", ".xlsx"),
    "Videos": (".mp4", ".avi", ".mkv", ".mov"),
    "Musicas": (".mp3", ".wav", ".flac", ".m4a"),
    "Compactados": (".zip", ".rar", ".7z", ".tar"),
}

ARQUIVO_LOG = "historico_organizacao.json"


class OrganizadorArquivos:
    """Organiza arquivos em pastas por tipo"""
    
    def __init__(self, caminho_pasta):
        self.pasta = caminho_pasta
        self.historico = self._carregar_historico()
        self.movidos = []
        self.erros = []
    
    def _carregar_historico(self):
        """Carrega o histórico de movimentos anteriores"""
        if os.path.exists(ARQUIVO_LOG):
            try:
                with open(ARQUIVO_LOG, "r") as arquivo:
                    return json.load(arquivo)
            except:
                return []
        return []
    
    def _salvar_historico(self):
        """Salva o histórico em JSON"""
        with open(ARQUIVO_LOG, "w") as arquivo:
            json.dump(self.historico, arquivo, indent=2)
    
    def _obter_tipo_arquivo(self, extensao):
        """Retorna a categoria do arquivo pela extensão"""
        extensao_lower = extensao.lower()
        for tipo, extensoes in TIPOS.items():
            if extensao_lower in extensoes:
                return tipo
        return None
    
    def _evitar_duplicatas(self, caminho_destino):
        """Se arquivo existe, adiciona número no final"""
        if not os.path.exists(caminho_destino):
            return caminho_destino
        
        arquivo = Path(caminho_destino)
        contador = 1
        
        while True:
            novo_nome = f"{arquivo.stem}_{contador}{arquivo.suffix}"
            novo_caminho = arquivo.parent / novo_nome
            if not os.path.exists(novo_caminho):
                return str(novo_caminho)
            contador += 1
    
    def organizar(self):
        """Organiza todos os arquivos da pasta"""
        
        if not os.path.exists(self.pasta):
            print(f"Pasta nao encontrada: {self.pasta}")
            return False
        
        print(f"Organizando arquivos em: {self.pasta}\n")
        
        try:
            arquivos = [f for f in os.listdir(self.pasta) 
                       if os.path.isfile(os.path.join(self.pasta, f))]
            
            if not arquivos:
                print("Nenhum arquivo encontrado.\n")
                return False
            
            for arquivo in arquivos:
                try:
                    caminho_completo = os.path.join(self.pasta, arquivo)
                    extensao = Path(arquivo).suffix
                    tipo = self._obter_tipo_arquivo(extensao)
                    
                    if not tipo:
                        print(f"Ignorado: {arquivo}")
                        continue
                    
                    pasta_tipo = os.path.join(self.pasta, tipo)
                    if not os.path.exists(pasta_tipo):
                        os.makedirs(pasta_tipo)
                    
                    caminho_destino = os.path.join(pasta_tipo, arquivo)
                    caminho_destino = self._evitar_duplicatas(caminho_destino)
                    
                    shutil.move(caminho_completo, caminho_destino)
                    
                    movimento = {
                        "arquivo": arquivo,
                        "tipo": tipo,
                        "origem": caminho_completo,
                        "destino": caminho_destino,
                        "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                    }
                    self.movidos.append(movimento)
                    
                    print(f"Movido: {arquivo} -> {tipo}/")
                
                except PermissionError:
                    print(f"Erro: Sem permissao para mover {arquivo}")
                    self.erros.append(arquivo)
                except Exception as erro:
                    print(f"Erro ao mover {arquivo}: {str(erro)}")
                    self.erros.append(arquivo)
            
            if self.movidos:
                self.historico.append({
                    "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                    "arquivos_movidos": len(self.movidos),
                    "detalhes": self.movidos
                })
                self._salvar_historico()
            
            print(f"\nResumo:")
            print(f"Movidos: {len(self.movidos)}")
            print(f"Erros: {len(self.erros)}\n")
            
            return len(self.movidos) > 0
        
        except Exception as erro:
            print(f"Erro geral: {erro}\n")
            return False
    
    def desfazer_ultima_acao(self):
        """Desfaz a ultima organizacao realizada"""
        
        if not self.historico:
            print("Nao ha historico para desfazer.\n")
            return False
        
        ultima_acao = self.historico[-1]
        detalhes = ultima_acao["detalhes"]
        
        print(f"Desfazendo organizacao de {ultima_acao['data']}\n")
        
        erros = 0
        for movimento in detalhes:
            try:
                destino = movimento["destino"]
                origem = movimento["origem"]
                
                if os.path.exists(destino):
                    shutil.move(destino, origem)
                    print(f"Restaurado: {movimento['arquivo']}")
                else:
                    print(f"Arquivo nao encontrado: {movimento['arquivo']}")
                    erros += 1
            
            except Exception as erro:
                print(f"Erro ao restaurar {movimento['arquivo']}: {str(erro)}")
                erros += 1
        
        self.historico.pop()
        self._salvar_historico()
        
        print(f"\nRestaurados: {len(detalhes) - erros}")
        print(f"Erros: {erros}\n")
        
        return erros == 0


def menu_principal():
    """Menu de opcoes"""
    organizador = OrganizadorArquivos(PASTA)
    
    while True:
        print("=== Organizador de Arquivos ===")
        print("1 - Organizar arquivos")
        print("2 - Desfazer ultima acao")
        print("3 - Sair")
        
        opcao = input("\nEscolha uma opcao: ").strip()
        print()
        
        if opcao == "1":
            organizador.organizar()
        elif opcao == "2":
            organizador.desfazer_ultima_acao()
        elif opcao == "3":
            print("Saindo...")
            break
        else:
            print("Opcao invalida!\n")


if __name__ == "__main__":
    menu_principal()