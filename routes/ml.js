const express = require('express');
const axios = require('axios');
const router = express.Router();

// URL do serviço Python (ajuste a porta conforme necessário)
const ML_SERVICE_URL = 'http://localhost:8001';

// Rota para recomendações
router.get('/recomendacoes', async (req, res) => {
  try {
    const { id_usuario } = req.query;
    
    if (!id_usuario) {
      return res.status(400).json({ error: 'id_usuario é obrigatório' });
    }

    // Fazer requisição para o serviço Python
    const response = await axios.get(`${ML_SERVICE_URL}/analytics/recomendacoes`, {
      params: { id_usuario },
      timeout: 30000 // 30 segundos de timeout
    });

    res.json(response.data);
  } catch (error) {
    console.error('Erro ao conectar com serviço ML:', error.message);
    
    if (error.code === 'ECONNREFUSED') {
      return res.status(503).json({ 
        error: 'Serviço de ML indisponível',
        detail: 'O serviço de machine learning não está rodando'
      });
    }
    
    res.status(500).json({ 
      error: 'Erro interno',
      detail: error.response?.data?.detail || error.message 
    });
  }
});

// Rota para gráficos
router.get('/grafico-json', async (req, res) => {
  try {
    const { tipo = 'receita' } = req.query;
    
    const response = await axios.get(`${ML_SERVICE_URL}/analytics/grafico-json`, {
      params: { tipo },
      timeout: 30000
    });

    res.json(response.data);
  } catch (error) {
    console.error('Erro ao conectar com serviço ML:', error.message);
    res.status(500).json({ error: 'Erro ao gerar gráfico' });
  }
});

module.exports = router;
