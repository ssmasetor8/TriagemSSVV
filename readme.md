# 🩺 SSVV - Sistema de Triagem SSMA (Setor 8)

> Sistema de gestão de triagem e sinais vitais para voluntários e profissionais de saúde.

![Status](https://img.shields.io/badge/Status-Concluído-brightgreen)
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-red)
![Supabase](https://img.shields.io/badge/Backend-Supabase-green)
![Android](https://img.shields.io/badge/Mobile-Kotlin-orange)

## 📖 Sobre o Projeto

O **SSVV Setor 8** é uma solução completa desenvolvida para auxiliar a equipe de saúde e segurança (SSMA). O sistema permite o cadastro rápido de voluntários, registro detalhado de sinais vitais (Pressão, FC, SpO2, Dextro) e emissão de pareceres de aptidão.

O projeto consiste em três camadas:
1.  **Web App:** Interface responsiva feita em Streamlit.
2.  **Backend:** Banco de dados PostgreSQL gerenciado pelo Supabase com políticas de segurança (RLS).
3.  **Mobile App:** Aplicativo Android nativo (WebView) para uso facilitado em smartphones.

---

## 🚀 Funcionalidades

* **Autenticação:** Login seguro para profissionais cadastrados.
* **Gestão de Pessoas:** Cadastro de novos Voluntários e Profissionais.
* **Triagem Completa:** Formulário otimizado para coleta de sinais vitais.
* **Relatórios:** Exportação de dados em CSV para análise administrativa.
* **Mobile-First:** Interface adaptada para telas verticais com CSS injetado.
* **Alta Disponibilidade:** Monitoramento via UptimeRobot para evitar hibernação do servidor.

---

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python
* **Framework Web:** Streamlit
* **Banco de Dados:** Supabase (PostgreSQL)
* **Cliente DB:** `supabase-py`
* **Android Wrapper:** Kotlin (WebView + Android Studio)

---

## ⚙️ Configuração do Banco de Dados (Supabase)

O projeto utiliza 3 tabelas principais.

Nota de Segurança: Todas as tabelas possuem Row Level Security (RLS) ativado para garantir que apenas usuários autenticados (ou anon via API Key segura) possam inserir dados.

## 💻 Instalação e Execução Local
Clone o repositório:
Bash
git clone
cd ssvv-setor8

crie um ambiente virtual e instale as dependências:

Bash

python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

pip install -r requirements.txt
Configure as Credenciais: Crie uma pasta .streamlit e um arquivo secrets.toml dentro dela:

Ini, TOML

# .streamlit/secrets.toml
SUPABASE_URL = "URL_DO_SUPABASE"

SUPABASE_KEY = "CHAVE_ANON_OU_SERVICE_ROLE"
Execute o App:

Bash

streamlit run app.py

## 📱 Compilação Android (APK)
O aplicativo Android funciona como um wrapper que carrega a aplicação web.

Configurações Chave no Android Studio:

Template: Empty Views Activity.

Permissões (AndroidManifest.xml):

XML

<uses-permission android:name="android.permission.INTERNET" />
Orientação de Tela: Travada em Portrait.

WebView: Configurado no MainActivity.kt com JavaScript ativado.

Kotlin

myWebView.settings.javaScriptEnabled = true

myWebView.loadUrl("")

## 📄 Licença
Este projeto foi desenvolvido para uso interno do setor SSMA.

 Irmão Edson