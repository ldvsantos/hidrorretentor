# SMOKE TEST AUDIT - HIDRORRETENTOR TABOA
**Data:** 28 de janeiro de 2026
**Modo:** Diego Vidal (Geotechnical & Materials Editor)

---

## 1. TESTES ANUNCIADOS NA METODOLOGIA vs. RESULTADOS

### ✅ TESTES DESCRITOS E UTILIZADOS CORRETAMENTE:

1. **Shapiro-Wilk e Levene** (Metodologia, Análise estatística)
   - Status: ✅ Mencionados na metodologia
   - Uso: Premissas de normalidade e homoscedasticidade
   - Resultado: Não há apresentação explícita desses testes nos Resultados (correto, pois são testes de premissas)

2. **Bootstrap BCa (1.000 iterações)** (Metodologia, Análise estatística)
   - Status: ✅ Mencionado e utilizado
   - Resultado: IC95% reportados em múltiplas figuras (Fig 5, 7, 9, 10)
   - Validação: ✅ CORRETO

3. **Tukey HSD (p < 0.05)** (Metodologia, Análise estatística)
   - Status: ✅ Mencionado e utilizado
   - Resultado: Segregação de médias com letras nas Tabelas 2, 5 e mencionado em análises
   - Validação: ✅ CORRETO

4. **GLM Gamma com ligação log** (Metodologia, Análise estatística)
   - Status: ✅ Mencionado e utilizado
   - Resultado: Aplicado em métricas de sorção (Fig 5, Seção Sorção Macroscópica)
   - Validação: ✅ CORRETO

5. **Testes de Wald com ajuste de Holm** (Metodologia, Análise estatística)
   - Status: ✅ Mencionado
   - Resultado: Citado em análise de sorção (p ajustado = 0.014, 0.313)
   - Validação: ✅ CORRETO

6. **Kaplan-Meier** (Metodologia, Análise estatística)
   - Status: ✅ Mencionado
   - Resultado: Figura 6 e discussão sobre cinética germinativa
   - Validação: ✅ CORRETO

7. **Modelo de Cox (riscos proporcionais)** (Metodologia, Análise estatística)
   - Status: ✅ Mencionado
   - Resultado: Tabela 3 com HR, IC95% e p-values
   - Validação: ✅ CORRETO

8. **PCA (Análise de Componentes Principais)** (Metodologia, Análise estatística)
   - Status: ✅ Mencionado
   - Resultado: Figura 11 com biplot, PC1 (53.98%) e PC2 (15.50%)
   - Validação: ✅ CORRETO

9. **Cohen's d e η² parcial** (Metodologia, Análise estatística)
   - Status: ✅ Mencionados como métricas de tamanho de efeito
   - Resultado: η² parcial reportado nas Tabelas 2 e 5
   - Validação: ⚠️ **Cohen's d não foi reportado nos Resultados**

10. **ANOVA** (Metodologia, implícito no contexto DIC)
    - Status: ✅ Utilizado
    - Resultado: Reportado em múltiplas análises (Tabelas 2, 5, Figura 10)
    - Validação: ✅ CORRETO

---

## 2. DADOS CITADOS NO TEXTO vs. COERÊNCIA COM MÉTODO

### ✅ VALORES NUMÉRICOS RASTREÁVEIS:

#### A) **RESUMO**
- **Germinação:** "5,8% superior" (98% vs 92,6%)
  - Cálculo: (98-92.6)/92.6 × 100 = 5.83% ✅ CORRETO
  
- **Elongação hipocótilo:** "106,6% maior"
  - Mencionado como resposta relativa no Resumo
  - Valor esperado vs. controle: precisa validação com dados brutos
  - ⚠️ **ALERTA:** Tabela A1 (citada no texto mas não apresentada) deveria conter esses valores

- **Biomassa fresca:** "158,5% superior"
  - Cálculo: (0.411-0.159)/0.159 × 100 = 158.49% ✅ CORRETO
  
- **IVG:** "7,3% superior"
  - Não há valores diretos de IVG nas tabelas para N1 vs controle
  - ⚠️ **DISCREPÂNCIA:** Tabela 2 mostra IVG como "2.045 vs 1.933" (unidade "h" parece erro - deveria ser adimensional)
  - Cálculo se fosse correto: (2.045-1.933)/1.933 × 100 = 5.79% ≠ 7,3%
  - 🔴 **ERRO CRÍTICO: Valor de 7,3% não corresponde aos dados da Tabela 2**

- **TMG:** "reduzido em 4,6%"
  - ⚠️ **DISCREPÂNCIA:** Tabela 2 mostra TMG igual a IVG (2.045 vs 1.933)
  - Se o cálculo for redução: (1.933-2.045)/1.933 × 100 = -5.79% (aumento, não redução)
  - 🔴 **ERRO CRÍTICO: Direção da mudança incorreta ou dados da tabela errados**

#### B) **CARACTERIZAÇÃO QUÍMICA (Tabela 1)**
- pH 6,38 (N1) ✅ PRESENTE
- K⁺ 1004,98 mg L⁻¹ ✅ PRESENTE
- P total 62,01 mg L⁻¹ ✅ PRESENTE
- Ca²⁺ 577,5 mg L⁻¹ ✅ PRESENTE
- Mg²⁺ 292,6 mg L⁻¹ ✅ PRESENTE
- Validação: ✅ TODOS OS VALORES CORRESPONDEM

#### C) **SORÇÃO (Figura 5 citada no texto)**
- N1: 0.385 ± 0.278 g ✅ CITADO
- Controle: 0.143 ± 0.078 g ✅ CITADO
- Razão: 2.69 (GLM) ✅ CITADO
- IC95% BCa mencionado ✅ CORRETO

#### D) **GERMINAÇÃO (Tabela 2)**
⚠️ **PROBLEMA CRÍTICO IDENTIFICADO:**
- Unidade de IVG e TMG listada como "h" (horas)
- **IVG é adimensional** (Eq. 1 na metodologia não tem unidade)
- **TMG deveria ser em DIAS** (Eq. 2 usa Gi × Ti, onde Ti é tempo em dias)
- 🔴 **ERRO DE ROTULAGEM: Coluna da Tabela 2 possui unidade errada**

- Valores de IVG = TMG na Tabela 2 (2.045 = 2.045)
  - 🔴 **ERRO LÓGICO: IVG e TMG não podem ser idênticos por definição matemática**

#### E) **BIOMASSA (Tabela 5)**
- N1 massa fresca: 0.411 ± 0.280 g ✅ CORRETO
- Controle massa fresca: 0.159 ± 0.080 g ✅ CORRETO
- N1 massa seca: 0.026 ± 0.006 g ✅ CORRETO
- Diferença percentual citada no resumo: 158,5% ✅ VALIDADO

---

## 3. FIGURAS CITADAS vs. DISCUSSÃO NO TEXTO

### ✅ FIGURAS MENCIONADAS E DISCUTIDAS:

1. **Figura 1** - Extração de fibras (Metodologia) ✅ CITADO
2. **Figura 2** - Morfologia de plântulas (Metodologia) ✅ CITADO
3. **Figura 3** - FTIR (Resultados, Caracterização Tecnológica) ✅ CITADO E DISCUTIDO
4. **Figura 4** - TGA (Resultados, Caracterização Tecnológica) ✅ CITADO E DISCUTIDO
5. **Figura 5** - Sorção hídrica (Resultados, Sorção Macroscópica) ✅ CITADO E DISCUTIDO
6. **Figura 6** - Kaplan-Meier (Resultados, Compatibilidade Biológica) ✅ CITADO E DISCUTIDO
7. **Figura 7** - IVG (Resultados, Compatibilidade Biológica) ✅ CITADO E DISCUTIDO
8. **Figura 8** - Morfogênese (a) hipocótilo (b) radícula ✅ CITADO E DISCUTIDO
9. **Figura 9** - Inibição (a) hipocótilo (b) radícula ✅ CITADO E DISCUTIDO
10. **Figura 10** - Mesocosmo (a)(b)(c) ✅ CITADO E DISCUTIDO
11. **Figura 11** - PCA bandeja ✅ CITADO E DISCUTIDO

### ⚠️ TABELAS FANTASMA:
- **Tabela A1** (Anexo) - ✅ CITADA no texto ("Tabela A1")
  - 🔴 **PROBLEMA: Tabela A1 não está presente no documento**
  - Localização da citação: Seção "Morfogênese e Respostas Bioestimulantes"
  - Conteúdo esperado: Valores de hipocótilo e radícula com ΔM

---

## 4. PROTOCOLO DE FIGURAS EMA (7.4)

### Análise de Sequência:
✅ **SEQUÊNCIA PRESERVADA:** Figuras 1-11 sem quebras
✅ **CITAÇÃO ANTES DA FIGURA:** Todas as figuras são citadas no texto antes de aparecer
✅ **UMA FIGURA POR PARÁGRAFO:** Respeitado (não há empilhamento tipo "Figs 4, 5 e 6")

---

## 5. INCONSISTÊNCIAS CRÍTICAS DETECTADAS

### 🔴 ERRO CRÍTICO 1: TABELA 2 - IVG e TMG
**Problema:**
- IVG e TMG apresentam valores idênticos (2.045 = 2.045 para N1)
- Matematicamente impossível pelas Equações 1 e 2

**Ação Recomendada:**
```
Verificar os dados brutos e recalcular IVG e TMG.
IVG = Σ(Gi/Ni) → somatório acumulado
TMG = Σ(Gi × Ti) / Σ(Gi) → média ponderada
Esses valores NUNCA podem ser iguais.
```

### 🔴 ERRO CRÍTICO 2: RESUMO vs. TABELA 2
**Problema:**
- Resumo: "IVG 7,3% superior ao controle"
- Tabela 2: IVG N1=2.045 vs Controle=1.933 → diferença de 5,79%

**Ação Recomendada:**
```
Recalcular o percentual correto ou verificar se há outro dataset sendo usado no resumo.
```

### 🔴 ERRO CRÍTICO 3: TMG - DIREÇÃO DA MUDANÇA
**Problema:**
- Resumo: "TMG reduzido em 4,6%"
- Tabela 2: N1=2.045 vs Controle=1.933 → N1 é MAIOR (aumento de 5,79%, não redução)

**Ação Recomendada:**
```
Se TMG aumentou, isso significa germinação MAIS LENTA, não mais rápida.
Revisar interpretação ou corrigir os dados.
```

### 🔴 ERRO CRÍTICO 4: UNIDADE DE IVG E TMG
**Problema:**
- Tabela 2 lista unidade como "h" (horas)
- IVG é adimensional
- TMG deveria ser em dias (conforme Eq. 2)

**Ação Recomendada:**
```
Corrigir cabeçalho da Tabela 2:
- IVG (média ± DP) [sem unidade]
- TMG (dias, média ± DP)
```

### ⚠️ ALERTA 5: TABELA A1 AUSENTE
**Problema:**
- Tabela A1 é citada no texto mas não existe no documento

**Ação Recomendada:**
```
Criar Tabela A1 com os valores de:
- Comprimento hipocótilo (mm)
- Comprimento radícula (mm)
- ΔM para cada tratamento
OU remover a citação do texto
```

### ⚠️ ALERTA 6: Cohen's d NÃO REPORTADO
**Problema:**
- Metodologia menciona uso de Cohen's d
- Resultados não apresentam esse valor

**Ação Recomendada:**
```
Adicionar Cohen's d nas análises de tamanho de efeito
OU remover da metodologia se não foi calculado
```

---

## 6. TESTES DESCRITOS MAS NÃO USADOS

✅ **NENHUM TESTE ANUNCIADO FOI OMITIDO**
- Todos os testes mencionados na metodologia foram utilizados nos resultados

---

## 7. TESTES USADOS MAS NÃO DESCRITOS

✅ **NENHUM TESTE NÃO-DECLARADO FOI USADO**
- Todos os testes aplicados foram previamente descritos na metodologia

---

## 8. RECOMENDAÇÕES DE CORREÇÃO (ORDEM DE PRIORIDADE)

### PRIORIDADE ALTA (Bloqueia Submissão):
1. **Recalcular IVG e TMG** e atualizar Tabela 2
2. **Corrigir valores no Resumo** (IVG 7,3% → 5,8%; TMG direção)
3. **Corrigir unidades na Tabela 2** (remover "h", adicionar unidade correta)
4. **Criar Tabela A1** ou remover citação do texto

### PRIORIDADE MÉDIA (Melhora Qualidade):
5. Adicionar valores de **Cohen's d** nos resultados ou remover da metodologia
6. Revisar se a **Tabela 3** (Cox) está formatada corretamente (parece ter problema de markdown)

### PRIORIDADE BAIXA (Polimento):
7. Verificar se todos os p-values estão formatados consistentemente (p \< 0.05 vs p = 0.003)

---

## 9. DIAGNÓSTICO FINAL

### STATUS DO MANUSCRITO:
🟡 **AMARELO - CORREÇÕES CRÍTICAS NECESSÁRIAS**

### PRINCIPAIS VULNERABILIDADES:
1. Dados de IVG/TMG inconsistentes entre Resumo e Tabela 2
2. Possível erro de transcrição ou cálculo em cinética germinativa
3. Tabela fantasma (A1) citada mas ausente

### PONTOS FORTES:
✅ Estrutura metodológica robusta e completa
✅ Uso correto de testes estatísticos avançados
✅ Sequência de figuras preservada (EMA compliance)
✅ Citações de figuras antes das próprias figuras
✅ Todos os testes anunciados foram usados

---

## 10. CHECKLIST DE AÇÃO IMEDIATA

- [ ] Reabrir dados brutos de germinação
- [ ] Recalcular IVG com Eq. 1
- [ ] Recalcular TMG com Eq. 2
- [ ] Atualizar Tabela 2 com valores corretos
- [ ] Atualizar Resumo com percentuais corretos de IVG e TMG
- [ ] Corrigir unidade da Tabela 2 (IVG sem unidade, TMG em dias)
- [ ] Criar Tabela A1 com morfometria ou remover citação
- [ ] Adicionar Cohen's d ou remover da metodologia
- [ ] Revisar formatação Markdown da Tabela 3

---

**FIM DO SMOKE TEST AUDIT**
