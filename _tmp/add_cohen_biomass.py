import re

file_path = r"c:\Users\vidal\OneDrive\Documentos\13 - CLONEGIT\artigo-posdoc\2 - HIDRORRETENTOR\3 - MANUSCRITO\1-MARKDOWN\1-MANUSCRITOS\Hidrorretentor_Taboa.md"

# Ler o conteúdo
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Primeira substituição: adicionar Cohen's d para massa fresca (159%)
old1 = r"em aproximadamente 159%, enquanto N2, N3 e N4 permaneceram em faixa intermediária"
new1 = r"em aproximadamente 159% (Cohen's d = 1.217, efeito grande), enquanto N2, N3 e N4 permaneceram em faixa intermediária"

if old1 in content:
    content = content.replace(old1, new1)
    print("✓ Adicionado Cohen's d = 1.217 para massa fresca")
else:
    print("✗ Padrão para massa fresca NÃO ENCONTRADO")

# Escrever de volta
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("\nArquivo atualizado com sucesso!")
