import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(layout = 'wide')

def formata_numero(valor, prefixo = ''):
    for i in ['', 'mil']:
        if valor <1000:
            return f'{prefixo} {valor:.2f} {i}'
        valor /=1000
    return f'{prefixo} {valor:.2f} milhões'

st.title('DASHBOARD DE VENDAS 🛒')

url = 'https://labdados.com/produtos'
regioes = ['Brasil', 'Centro-Oeste', 'Nordeste', 'Norte', 'Sudeste', 'Sul']

st.sidebar.title('Filtros')
regiao = st.sidebar.selectbox('Região', regioes)

if regiao == 'Brasil':
    regiao = ''

todos_anos = st.sidebar.checkbox('Dados de todo o período', value = True)
if todos_anos:
    ano =''
else:
    ano = st.sidebar.slider('Ano', 2020, 2023)


query_string = {'regiao':regiao.lower(), 'ano': ano}
response = requests.get(url, params= query_string)
dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format='%d/%m/%Y')

filtro_vendedores = st.sidebar.multiselect('Vendedores', dados['Vendedor'].unique())
if filtro_vendedores:
    dados = dados[dados['Vendedor'].isin(filtro_vendedores)]

## Tabelas
### Tabelas de receita
receita_estados = dados.groupby('Local da compra')[['Preço']].sum()
receita_estados = dados.drop_duplicates(subset = 'Local da compra')[['Local da compra', 'lat', 'lon']].merge(receita_estados, left_on = 'Local da compra', right_index = True).sort_values('Preço', ascending=False)

receita_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq= 'ME'))['Preço'].sum().reset_index()
receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
receita_mensal['Mes'] = receita_mensal['Data da Compra'].dt.month_name()

receita_categoria = dados.groupby('Categoria do Produto')[['Preço']].sum().sort_values('Preço', ascending=False).reset_index()

### Tabelas de quantidade de vendas
vendas_estado = dados.groupby('Local da compra')[['Preço']].count()
vendas_estado = dados.drop_duplicates(subset = 'Local da compra')[['Local da compra', 'lat', 'lon']].merge(vendas_estado, left_on = 'Local da compra', right_index = True).sort_values('Preço', ascending = False)

vendas_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq= 'ME'))['Preço'].count().reset_index()
vendas_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
vendas_mensal['Mes'] = receita_mensal['Data da Compra'].dt.month_name()

vendas_categoria = dados.groupby('Categoria do Produto')[['Preço']].count().sort_values('Preço', ascending=False).reset_index()

### Tabelas de vendedores
vendedores = pd.DataFrame(dados.groupby('Vendedor')['Preço'].agg(['sum', 'count']))

## Gráficos
fig_mapa_receita = px.scatter_geo(receita_estados, 
                                  lat = 'lat',
                                  lon = 'lon',
                                  scope = 'south america',
                                  fitbounds = 'locations',
                                  size = 'Preço',
                                  template = 'seaborn',
                                  hover_name = 'Local da compra',
                                  hover_data = {'lat': False, 'lon':False},
                                  title = 'Receita por estado')

fig_receita_mensal = px.line(receita_mensal,
                             x = 'Mes',
                             y = 'Preço',
                             markers = True,
                             range_y = (0,receita_mensal.max()), 
                             color= 'Ano',
                             line_dash = 'Ano',
                             title= 'Receita mensal')
fig_receita_mensal.update_layout(yaxis_title = 'Receita')

fig_receita_estados = px.bar(receita_estados.head(), 
                             x = 'Local da compra', 
                             y = 'Preço',
                             text_auto = True,
                             title = 'Top estados (receita)',
                             color = 'Local da compra')
fig_receita_estados.update_layout(yaxis_title = 'Receita')
fig_receita_estados.update_traces(texttemplate="<b><span style='color:black'>R$ %{y:,.2f}</span></b>",
                                  textposition='outside')

fig_receita_categorias = px.bar(receita_categoria,
                                x = 'Categoria do Produto',
                                y = 'Preço',
                                text_auto = True,
                                title = 'Receita por categoria',
                                color = 'Categoria do Produto')
fig_receita_categorias.update_layout(yaxis_title = 'Receita')


fig_mapa_vendas = px.scatter_geo(vendas_estado, 
                                  lat = 'lat',
                                  lon = 'lon',
                                  scope = 'south america',
                                  fitbounds = 'locations',
                                  size = 'Preço',
                                  template = 'seaborn',
                                  hover_name = 'Local da compra',
                                  hover_data = {'lat': False, 'lon':False},
                                  title = 'Vendas por estado')


fig_vendas_mensal = px.line(vendas_mensal,
                             x = 'Mes',
                             y = 'Preço',
                             markers = True,
                             range_y = (0,vendas_mensal.max()), 
                             color= 'Ano',
                             line_dash = 'Ano',
                             title= 'Vendas mensal')
fig_vendas_mensal.update_layout(yaxis_title = 'Quantidade de Vendas')

fig_vendas_estados = px.bar(vendas_estado.head(), 
                             x = 'Local da compra', 
                             y = 'Preço',
                             text_auto = True,
                             title = 'Top estados (Quantidade de vendas)',
                             color = 'Local da compra')
fig_vendas_estados.update_layout(yaxis_title = 'Vendas')
fig_vendas_estados.update_traces(texttemplate="<b><span style='color:black'>%{y:.0f}</span></b>",
                                  textposition='outside')

fig_vendas_categoria = px.bar(vendas_categoria,
                                x = 'Categoria do Produto',
                                y = 'Preço',
                                text_auto = True,
                                title = 'Vendas por categoria',
                                color = 'Categoria do Produto')
fig_vendas_categoria.update_layout(yaxis_title = 'Vendas', showlegend=False)

## visualizaçao no streamlit
aba1, aba2, aba3 = st.tabs(['Receita', 'Quantidade de vendas', 'Vendedores'])

with aba1:
    col1, col2 = st.columns(2)
    with col1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'), border=True)
        st.plotly_chart(fig_mapa_receita, use_container_width = True)
        st.plotly_chart(fig_receita_estados, use_container_width = True)
    with col2:
        st.metric('Quantidade de vendas', formata_numero(dados.shape[0]), border=True)
        st.plotly_chart(fig_receita_mensal, use_container_width = True)
        st.plotly_chart(fig_receita_categorias, use_container_width = True)

with aba2:
    col1, col2 = st.columns(2)
    with col1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'), border=True)
        st.plotly_chart(fig_mapa_vendas, use_container_width = True)
        st.plotly_chart(fig_vendas_estados, use_container_width = True)

    with col2:
        st.metric('Quantidade de vendas', formata_numero(dados.shape[0]), border=True)
        st.plotly_chart(fig_vendas_mensal, use_container_width =True)
        st.plotly_chart(fig_vendas_categoria, use_container_width = True)

with aba3:
    qtd_vendedores = st.number_input('Quantidade de vendedores', 2, 10, 5)
    col1, col2 = st.columns(2)
    with col1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'), border=True)
        fig_receita_vendedores = px.bar(vendedores[['sum']].sort_values('sum', ascending = False).head(qtd_vendedores),
                                        x = 'sum',
                                        y = vendedores[['sum']].sort_values('sum', ascending=False).head(qtd_vendedores).index,
                                        text_auto = True,
                                        title = f'Top {qtd_vendedores} vendedores (receita)')
        st.plotly_chart(fig_receita_vendedores)
    with col2:
        st.metric('Quantidade de vendas', formata_numero(dados.shape[0]), border=True)
        fig_vendas_vendedores = px.bar(vendedores[['count']].sort_values('count', ascending=False).head(qtd_vendedores),
                                        x = 'count',
                                        y = vendedores[['count']].sort_values('count', ascending=False).head(qtd_vendedores).index,
                                        text_auto = True,
                                        title = f'Top {qtd_vendedores} vendedores (quantidade de vendas)')
        st.plotly_chart(fig_vendas_vendedores)
