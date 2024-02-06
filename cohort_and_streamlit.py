import streamlit as st
import numpy as np 
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Configurações Inicias
st.set_option('deprecation.showPyplotGlobalUse', False)
plt.style.use('dark_background')
st.title('Análise de Cohort')
st.header('O que é e como construir em python?')
st.write('A ideia do Cohort é mapear a entrada e saída da sua base, para entender a retenção ao longo do tempo.')
st.image(image='https://lh6.googleusercontent.com/HmZLiwML0ie1GE4MZ1Q7FupxrRBzeSkUZ4dfH8aTz3SJXdKauAHiY3rYlUJioXZDW50ucAygSHg3Qr43rLeyKoscA7cfKCD2EWxc0KcKUh-LEZv5QMzWH0qXhotpFzCEIS5QpiVu0S134FTEu72J6Jo',caption='Cohort')
st.write('Podemos analisar no exemplo acima, que estamos falando de uma lançamento de um aplicativo. No qual 1.098 entraram no dia 25 de Janeiro e, destes 33,9% continuavam no dia seguinte; 23,5% dois dias depois e 18,7% três dias depois e assim em diante. Fazendo isso diariamento ao logos dos dias, registrando a entrada de novos clientes naquele dia e quantos permaneciam nos dias seguintes. Com isso é possível visualizar a retenção de clientes.')
st.subheader('Como construir uma Cohort')

#Carreganento do DataSet
st.write('Vamos começar carregando o nosso dataset, iremos utilizar um data set que tenha um tipo de recorrência de seus clientes. Para isso vamos baixar do Kaagle o "Online Retail Data Set From UCI ML repo"')
st.image(image='https://lh4.googleusercontent.com/8B7Jziotu7Mblb5y2jJ7UUkGpuBnKZBTUSs18w-ZEVIoW76vc9X_lZOCuGDCO2LRjXBxeoMaidKK1qcYoh6fbM1iKjdvXxUXNZ3w47fHcqJK4R9T13_L0PVWSGExEX3Vf6HgAEWsLiTzWB0PtCKMJqo',caption='DataSet')
retail = pd.read_excel(r"https://enviowhatsapp.files.wordpress.com/2024/01/online-retail.xlsx")

#Visualizando Dados Dinâmico
filter_country = st.multiselect('Select Country:', retail['Country'].unique())
retail_filter = retail[retail['Country'].isin(filter_country)]
st.write(retail_filter.head())

#Limpeza de Dados
st.write('Nosso dataset na ordem da primeira à última coluna:  o código numérico que identifica a compra, o código numérico que identifica o item, a descrição do item em texto, a quantidade comprada, a data da compra, o preço unitário, a chave numérica de identificação do consumidor e o país de compra.')
st.write('Sem a retirada de linha', retail.shape)
st.write('Se não conseguimos identificar o cliente, não vamos conseguir acompanhar seu comportamento ao longo do tempo. Por causa disso, vamos excluir linhas que não possuem a variável CustomerID preenchida')
retail.dropna(subset=['CustomerID'], inplace=True)
st.write('Após retirada das linhas:', retail.shape)
st.write('Perdemos uma quantidade razoável de linhas no dataset, cerca de 25%. Caso acontecesse no mundo real, é preocupante. Não temos qualidade nos nossos dados')

# Análise descritiva
st.subheader('Entendendo os dados')
st.write('Antes de começarmos a gerar as cohorts. Vamos tentar entender um pouco os dados, o que passa pela estatística descritiva das colunas:')
st.write(retail.describe())
st.write('Veja que a quantidade média de itens por compra é em torno de 12, enquanto a mediana indica 5. Ou seja, temos uma distribuição bastante assimétrica.')
st.write('Mais importante do que entender a visão geral, precisamos pegar as visões por consumidor. Afinal, se a demanda é de uma análise Cohort, é porque estamos entendendo nossos clientes. Sendo assim, como será que é a distribuição de compras feitas por nossos clientes? Quantas compras cada cliente fez?')
invoice_per_costumer = retail.groupby(['CustomerID'])['InvoiceNo'].nunique()
st.write(invoice_per_costumer.describe())
plt.hist(invoice_per_costumer, bins=50)
st.pyplot()
st.write('Podemos ver claramente uma assimétrica quanto a distribuição de invoices pelo consumidores. Muitos clientes com poucas compras e alguns poucos com muitas compras.')
st.write('Olhando para o histograma, notamos que a concentração de compra fica entre 0 e 5.')

# Análise de cohort
st.subheader('Avançando com a cohort')
st.write('Já sabemos que podemos esperar pouca retenção. Vamos tentar identificar esses clientes que seguem realizando compras, realizando o agrupamento pela chave de identificação do cliente, a chave de identificação da compra e a data da compra')
retail = retail[['CustomerID', 'InvoiceNo', 'InvoiceDate']].drop_duplicates()
retail['InvoiceDate'] = pd.to_datetime(retail['InvoiceDate'])
retail['InvoiceMonth'] = retail['InvoiceDate'].dt.to_period('M')
retail['Cohort'] = retail.groupby('CustomerID')['InvoiceDate'].transform('min').dt.to_period('M')
st.write(retail.head())
st.write('Note que o consumidor com a chave 17850.0 entrou na cohort de dezembro/2010, mas teve duas compras em 01/12/2010. Essas duas compras não nos importam muito, nós precisamos apenas saber que ele estava nessa cohort e identificar em quais outros momentos ele aparecer')
st.write('Resumindo, precisamos contar quantos consumidores aparecem no início de cada cohort e quantos deles estão nos meses seguintes. Que tal agrupamos por cohort e por mês de invoice?')

# Agrupamento por cohort e mês de invoice
retail_cohort = retail.groupby(['Cohort', 'InvoiceMonth']).agg(n_customers=('CustomerID', 'nunique')).reset_index(drop=False)
st.code("""retail.groupby(['Cohort', 'InvoiceMonth']).agg(n_customers=('CustomerID', 'nunique')).reset_index(drop=False)""")
st.write(retail_cohort.head())

# Criação da coluna 'Period'
st.write('Repare que boa parte da análise já está resolvida, temos todas as cohorts e sabemos quantos permaneceram nos meses seguintes as suas entradas. Vamos construir uma matriz para facilitar a visualização, vamos criar uma colna com a numeração de cada período após o ínicio da cohort.')
st.write('Por exemplo, se a cohort se iniciou em dezembro de 2010, o mês de janeiro de 2011 será o número 1, enquanto fevereiro será o 2 e assim em diante')
retail_cohort['Period'] = (retail_cohort.InvoiceMonth - retail_cohort.Cohort).apply(lambda x: x.n)
st.code("""retail_cohort.apply(lambda row: relativedelta(row['InvoiceMonth'], row['Cohort']).months, axis=1)""")
st.write(retail_cohort.head())

# Criação da matriz de cohort
st.write('Se você é do excel ou do Power BI, já o que vamos utilizar a seguir né ? Uma pivot_table, também conhecida como tabela dinâmica')
cohort_pivot = retail_cohort.pivot_table(index='Cohort', columns='Period', values='n_customers')
st.write(cohort_pivot.head())

# Finalização da análise de cohort
st.subheader('Finalizando Cohort')
st.write('Estamos perto de finalizar, o que temos que terminar é: colocar os valores em percentual e criar um mapa de calor com os percentuais obtidos!')

# Cálculos finais e criação do mapa de calor
cohort_size = cohort_pivot.iloc[:,0]
st.write(cohort_size.head())
retention_matrix = cohort_pivot.divide(cohort_size, axis= 0)
st.write(retention_matrix.head())

st.write('Para fechar, vamos construir finalmente no mapa de calor!')
plt.subplots(figsize=(12,8))
sns.heatmap(
    data=retention_matrix,
    mask=retention_matrix.isnull(),
    annot=True,
    fmt='.0%',
    cmap='BuPu_r'
)

plt.title('Matriz de Retenção', size=14)
st.pyplot()

st.subheader('Rastrear e Investigar')
st.write("""A principal função da análise cohort é rastrear e investigar o desempenho de seus usuários ao longo do tempo e obter respostas para perguntas como:

Os novos clientes que você está adquirindo são mais (ou menos) valiosos do que os usuários anteriores?
As alterações que você fez em seu site afetaram positiva ou negativamente a jornada do seu cliente?
Existem diferenças sazonais entre os usuários que você adquire? 
Qual é a sua taxa de retenção?
Quando os usuários começam em churn?
Será que os clientes que você adquiriu no mês passado agem de forma diferente daqueles que se inscreveram no mês anterior? 
Os usuários que responderam a um desconto ou promoção se comportam de maneira semelhante ou não daqueles que compraram pelo preço integral?""")
st.subheader('Desempenho da Análise')
st.write("""Criar o hábito de verificar o desempenho dessa análise te permite conquistar uma variedade de métricas e serve, especialmente, para:

Identificar problemas mais cedo: você pode ver tendências nos cohorts mais recentes sem correr o risco dos resultados serem mascarados pelo restante da base de dados;
Criar previsões mais assertivas: conhecendo os comportamentos sazonais, você pode incorporá-los às suas expectativas de performance futura;
Saber como os comportamentos dos usuários afetam seu negócio: veja como as ações realizadas ou não por seus cohorts se traduzem em mudanças nas métricas da sua empresa, como aquisição e retenção;
Entender o churn do seu cliente: avalie hipóteses para entender quais ações incentivam uma maior rotatividade;
Calcular o valor da vida útil do cliente: veja quanto os seus clientes valem para a empresa ao longo do tempo. Você pode, inclusive, agrupar ainda mais esses cohorts para avaliar quais canais de aquisição levam ao melhor valor de vida útil do cliente (LTV);
Otimizar seu funil de conversão: descubra como a experiência do usuário em todo o funil de marketing digital se traduz em valor para seus clientes;
Criar um relacionamento mais eficaz com o cliente: à medida que você identifica padrões, fica mais fácil se relacionar com os seus usuários.
A análise responde tantas perguntas que permite que uma empresa identifique padrões claros em diferentes grupos de clientes.""")
