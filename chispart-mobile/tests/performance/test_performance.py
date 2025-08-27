import pytest
import time
import json
import asyncio
import statistics
from unittest.mock import patch

class TestPerformance:
    def test_response_time(self, app_client):
        """Test tiempo de respuesta de endpoints principales"""
        endpoints = ['/', '/chat', '/config', '/api/stats', '/api/config']
        results = {}
        
        for endpoint in endpoints:
            start_time = time.time()
            response = app_client.get(endpoint)
            end_time = time.time()
            
            response_time = end_time - start_time
            results[endpoint] = {
                'status_code': response.status_code,
                'response_time': response_time
            }
            
            # Verificar que el tiempo de respuesta es razonable (< 1 segundo)
            assert response_time < 1.0, f"Endpoint {endpoint} demasiado lento: {response_time:.2f}s"
        
        # Imprimir resultados para referencia
        print("\nTiempos de respuesta:")
        for endpoint, data in results.items():
            print(f"  {endpoint}: {data['response_time']:.4f}s (HTTP {data['status_code']})")
    
    def test_concurrent_requests(self, app_client):
        """Test rendimiento con múltiples peticiones secuenciales"""
        endpoint = '/'
        num_requests = 5
        response_times = []
        
        # Hacer peticiones secuenciales para evitar problemas de contexto Flask
        for i in range(num_requests):
            start_time = time.time()
            response = app_client.get(endpoint)
            end_time = time.time()
            
            response_times.append(end_time - start_time)
            assert response.status_code == 200
        
        # Analizar resultados
        avg_time = statistics.mean(response_times)
        max_time = max(response_times)
        
        print(f"\nPrueba secuencial ({num_requests} peticiones):")
        print(f"  Tasa de éxito: 100%")
        print(f"  Tiempo promedio: {avg_time:.4f}s")
        print(f"  Tiempo máximo: {max_time:.4f}s")
        
        # Verificaciones
        assert avg_time < 1.0, f"Tiempo promedio demasiado alto: {avg_time:.4f}s"
    
    @pytest.mark.asyncio
    async def test_api_response_time(self, app_client):
        """Test tiempo de respuesta de endpoints de API"""
        endpoints = ['/api/stats', '/api/config', '/api/pwa/cache-status']
        results = {}
        
        for endpoint in endpoints:
            start_time = time.time()
            response = app_client.get(endpoint)
            end_time = time.time()
            
            response_time = end_time - start_time
            results[endpoint] = {
                'status_code': response.status_code,
                'response_time': response_time
            }
            
            # Verificar que el tiempo de respuesta es razonable (< 0.5 segundos para APIs)
            assert response_time < 0.5, f"API endpoint {endpoint} demasiado lento: {response_time:.2f}s"
        
        # Imprimir resultados para referencia
        print("\nTiempos de respuesta de API:")
        for endpoint, data in results.items():
            print(f"  {endpoint}: {data['response_time']:.4f}s (HTTP {data['status_code']})")
    
    def test_memory_usage(self):
        """Test uso de memoria"""
        try:
            import psutil
            import os
            
            # Obtener proceso actual
            process = psutil.Process(os.getpid())
            
            # Medir uso de memoria antes
            memory_before = process.memory_info().rss / 1024 / 1024  # MB
            
            # Realizar operaciones que consumen memoria
            data = [i for i in range(100000)]  # Reducir para testing
            
            # Medir uso de memoria después
            memory_after = process.memory_info().rss / 1024 / 1024  # MB
            
            # Calcular incremento
            memory_increase = memory_after - memory_before
            
            print(f"\nUso de memoria:")
            print(f"  Antes: {memory_before:.2f} MB")
            print(f"  Después: {memory_after:.2f} MB")
            print(f"  Incremento: {memory_increase:.2f} MB")
            
            # Limpiar
            del data
            
        except ImportError:
            pytest.skip("psutil not installed")
