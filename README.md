# Polarização de Imagens

Sistema que amplia imagens usando técnicas de polarização para melhorar a qualidade.

## O que faz

Amplia imagens de forma inteligente analisando padrões direcionais, funcionando melhor que métodos convencionais em imagens com bordas nítidas e estruturas geométricas.

## Como instalar

```bash
pip install opencv-python numpy matplotlib
python main.py
```

## Como usar

Execute `python main.py` e escolha uma opção:

1. **Sua imagem**: Carregue uma imagem
2. **Teste específico**: Escolha um exemplo
3. **Ver todos testes**: Demonstração completa
4. **Teste simples**: Exemplo rápido

## Funciona bem em:

- **Arquitetura**: Prédios, janelas, estruturas
- **Padrões geométricos**: Grades, xadrez, linhas
- **Bordas nítidas**: Formas bem definidas
- **Documentos**: Texto, diagramas

## Não funciona bem em:

- **Paisagens naturais**: Céu, água, nuvens
- **Retratos**: Rostos, pessoas
- **Imagens borradas**: Sem bordas definidas
- **Ruído**: Imagens com muito ruído

## Como interpretar resultados

- **+15% ou mais**: Ótima melhoria
- **+5% a +15%**: Boa melhoria
- **0% a +5%**: Pouca diferença
- **Negativo**: Não use esta técnica

## Teste completo

Para análise detalhada:

```bash
python generate_image_test.py
```

Mostra gráficos comparativos e métricas de performance.

## Arquivos

- `main.py` - Programa principal
- `generate_image_test.py` - Testes e análises
- `README.md` - Esta documentação

## Limitações

- Funciona apenas em imagens com estruturas direcionais
- Mais lento que ampliação convencional
- Implementação simulada (não usa dados reais de polarização)

## Dica

Use sempre os testes primeiro para ver se sua imagem é adequada!

## Trabalho acadêmico
Este projeto foi desenvolvido como trabalho da disciplina Processamento Digital de Imagens do curso de Ciência da Computação na Universidade Federal de Alagoas (UFAL).

### Equipe
- Evellyn Rodrigues da Rocha
- Kauã Fellipe Pereira Bispo
- Lara Fernanda Amorim Alves Cavalcante

Todos os integrantes da equipe trabalharam juntos no desenvolvimento deste projeto através de reuniões colaborativas.