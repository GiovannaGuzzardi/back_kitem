# 🚀 Swagger/OpenAPI Documentation para Kitem API

## 📋 **O que foi implementado:**

### **1. DRF Spectacular**
- ✅ Instalado e configurado
- ✅ Schema automático da API
- ✅ Documentação interativa
- ✅ Exemplos de uso

### **2. Endpoints de Documentação:**
```
GET /api/schema/     → Schema OpenAPI em JSON
GET /api/docs/       → Interface Swagger UI
GET /api/redoc/      → Interface ReDoc
```

### **3. Views Documentadas:**
- ✅ **Favoritos**: Listar, criar, deletar, toggle
- ✅ **Parâmetros**: Documentados com tipos e exemplos
- ✅ **Respostas**: Códigos HTTP e estruturas JSON
- ✅ **Tags**: Organização por categoria

## 🎯 **Como usar:**

### **1. Acessar a Documentação:**
```
http://localhost:8000/api/docs/          # Swagger UI (recomendado)
http://localhost:8000/api/redoc/         # ReDoc (alternativa)
http://localhost:8000/api/schema/        # Schema JSON
```

### **2. Testar Endpoints:**
- 🔐 **Autenticação**: Configure o token JWT
- 📝 **Parâmetros**: Preencha os campos obrigatórios
- 🚀 **Execute**: Teste diretamente na interface

### **3. Exemplos de Uso:**

#### **Criar Favorito:**
```json
POST /api/favoritos/
{
    "id_usuario": 1,
    "id_receita": 1
}
```

#### **Deletar Favorito Seguro:**
```
DELETE /api/usuarios/1/favoritos/1/
```

#### **Toggle de Favorito:**
```
POST /api/usuarios/1/favoritos/1/toggle/
```

## 🔧 **Configurações Implementadas:**

### **Settings.py:**
```python
INSTALLED_APPS = [
    # ... outros apps
    'drf_spectacular',
]

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Kitem API',
    'VERSION': '1.0.0',
    'TAGS': ['auth', 'usuarios', 'ingredientes', 'receitas', 'favoritos', 'listas'],
    'SECURITY': [{'Bearer': []}],
}
```

### **URLs:**
```python
# Swagger/OpenAPI Documentation
path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
```

## 📚 **Benefícios:**

1. **Documentação Automática**: Atualiza com mudanças no código
2. **Interface Interativa**: Teste endpoints diretamente
3. **Exemplos Práticos**: Códigos de exemplo para cada endpoint
4. **Validação**: Verifica tipos de dados e parâmetros
5. **Organização**: Tags para agrupar endpoints por categoria

## 🚀 **Próximos Passos:**

1. **Instalar dependências**: `pip install -r requirements.txt`
2. **Iniciar servidor**: `python manage.py runserver`
3. **Acessar**: `http://localhost:8000/api/docs/`
4. **Testar**: Usar a interface para testar endpoints

## 🎉 **Resultado:**

Agora você tem uma **documentação profissional e interativa** da sua API, similar ao que grandes empresas oferecem! 🚀
