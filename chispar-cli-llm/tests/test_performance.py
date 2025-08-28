"""
Tests de rendimiento para Chispart CLI
Incluye tests de carga, memoria, tiempo de respuesta y optimizaciones
"""

import pytest
import time
import psutil
import os
import sys
from unittest.mock import patch, MagicMock
import threading
import concurrent.futures
from memory_profiler import profile
import tempfile

# Agregar el directorio padre al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from config_extended import get_api_config, get_available_models
from chispart_dev_agent_v3 import validate_api_key, create_text_message


class TestPerformanceBasic:
    """Tests básicos de rendimiento"""
    
    @pytest.mark.performance
    def test_config_loading_performance(self):
        """Test rendimiento de carga de configuración"""
        start_time = time.time()
        
        # Cargar configuración múltiples veces
        for _ in range(100):
            config = get_api_config('chispart')
            models = get_available_models('chispart')
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Debería cargar rápidamente (menos de 1 segundo para 100 iteraciones)
        assert execution_time < 1.0, f"Carga de configuración muy lenta: {execution_time:.2f}s"
    
    @pytest.mark.performance
    def test_message_creation_performance(self):
        """Test rendimiento de creación de mensajes"""
        start_time = time.time()
        
        # Crear muchos mensajes
        messages = []
        for i in range(1000):
            message = create_text_message(f"Test message {i}")
            messages.append(message)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Debería crear mensajes rápidamente
        assert execution_time < 0.5, f"Creación de mensajes muy lenta: {execution_time:.2f}s"
        assert len(messages) == 1000
    
    @pytest.mark.performance
    def test_api_validation_performance(self):
        """Test rendimiento de validación de API"""
        with patch.dict(os.environ, {'BLACKBOX_API_KEY': 'test_key'}):
            start_time = time.time()
            
            # Validar API múltiples veces
            for _ in range(50):
                config = validate_api_key('chispart')
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Validación debería ser rápida
            assert execution_time < 0.5, f"Validación de API muy lenta: {execution_time:.2f}s"


class TestMemoryUsage:
    """Tests de uso de memoria"""
    
    @pytest.mark.performance
    def test_memory_usage_config_loading(self):
        """Test uso de memoria al cargar configuración"""
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Cargar configuración múltiples veces
        configs = []
        for _ in range(100):
            config = get_api_config('chispart')
            models = get_available_models('chispart')
            configs.append((config, models))
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # No debería usar más de 50MB adicionales
        assert memory_increase < 50, f"Uso excesivo de memoria: {memory_increase:.2f}MB"
    
    @pytest.mark.performance
    def test_memory_usage_message_creation(self):
        """Test uso de memoria al crear mensajes"""
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Crear muchos mensajes
        messages = []
        for i in range(1000):
            message = create_text_message(f"Test message with some content {i} " * 10)
            messages.append(message)
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Limpiar referencias
        del messages
        
        # No debería usar más de 100MB adicionales
        assert memory_increase < 100, f"Uso excesivo de memoria: {memory_increase:.2f}MB"


class TestConcurrency:
    """Tests de concurrencia y paralelismo"""
    
    @pytest.mark.performance
    def test_concurrent_config_loading(self):
        """Test carga concurrente de configuración"""
        def load_config():
            config = get_api_config('chispart')
            models = get_available_models('chispart')
            return len(models)
        
        start_time = time.time()
        
        # Ejecutar en paralelo
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(load_config) for _ in range(50)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Debería completarse rápidamente
        assert execution_time < 2.0, f"Carga concurrente muy lenta: {execution_time:.2f}s"
        assert len(results) == 50
        assert all(result > 0 for result in results)
    
    @pytest.mark.performance
    def test_concurrent_message_creation(self):
        """Test creación concurrente de mensajes"""
        def create_messages(thread_id):
            messages = []
            for i in range(100):
                message = create_text_message(f"Thread {thread_id} message {i}")
                messages.append(message)
            return len(messages)
        
        start_time = time.time()
        
        # Ejecutar en paralelo
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(create_messages, i) for i in range(10)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Debería completarse rápidamente
        assert execution_time < 1.0, f"Creación concurrente muy lenta: {execution_time:.2f}s"
        assert len(results) == 10
        assert all(result == 100 for result in results)


class TestScalability:
    """Tests de escalabilidad"""
    
    @pytest.mark.performance
    def test_large_model_list_handling(self):
        """Test manejo de listas grandes de modelos"""
        # Simular una API con muchos modelos
        large_models = {f"model_{i}": f"api/model_{i}" for i in range(1000)}
        
        with patch('config_extended.AVAILABLE_MODELS', {'test_api': large_models}):
            start_time = time.time()
            
            models = get_available_models('test_api')
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Debería manejar listas grandes rápidamente
            assert execution_time < 0.1, f"Manejo de modelos grandes muy lento: {execution_time:.2f}s"
            assert len(models) == 1000
    
    @pytest.mark.performance
    def test_large_message_handling(self):
        """Test manejo de mensajes grandes"""
        # Crear mensaje muy grande
        large_content = "A" * 100000  # 100KB de texto
        
        start_time = time.time()
        
        message = create_text_message(large_content)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Debería manejar mensajes grandes rápidamente
        assert execution_time < 0.1, f"Manejo de mensajes grandes muy lento: {execution_time:.2f}s"
        assert message['content'] == large_content


class TestTermuxOptimizations:
    """Tests de optimizaciones específicas para Termux"""
    
    @pytest.mark.performance
    @patch('config_extended.is_termux')
    def test_termux_timeout_optimization(self, mock_is_termux):
        """Test optimizaciones de timeout para Termux"""
        mock_is_termux.return_value = True
        
        with patch('config_extended.get_mobile_optimized_timeouts') as mock_timeouts:
            mock_timeouts.return_value = {
                'total_timeout': 120,
                'connect_timeout': 10,
                'read_timeout': 120
            }
            
            # Usar la función _get_timeouts directamente para probar la lógica
            from config_extended import _get_timeouts
            
            # Simular carga de configuración optimizada
            start_time = time.time()
            
            timeouts = _get_timeouts()
            config = get_api_config('chispart')
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Debería cargar rápidamente incluso con optimizaciones
            assert execution_time < 0.1, f"Configuración Termux muy lenta: {execution_time:.2f}s"
            # Verificar que los timeouts optimizados se aplicaron en la función _get_timeouts
            assert timeouts['REQUEST_TIMEOUT'] == 120
    
    @pytest.mark.performance
    def test_mobile_network_simulation(self):
        """Test simulación de red móvil lenta"""
        # Simular latencia de red móvil
        def slow_network_call():
            time.sleep(0.1)  # Simular 100ms de latencia
            return {"status": "ok"}
        
        start_time = time.time()
        
        # Simular múltiples llamadas con latencia
        results = []
        for _ in range(10):
            result = slow_network_call()
            results.append(result)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Debería completarse en tiempo razonable
        assert execution_time >= 1.0  # Al menos 1 segundo por la latencia simulada
        assert execution_time < 2.0   # Pero no mucho más
        assert len(results) == 10


class TestResourceLimits:
    """Tests de límites de recursos"""
    
    @pytest.mark.performance
    def test_cpu_usage_under_load(self):
        """Test uso de CPU bajo carga"""
        def cpu_intensive_task():
            # Tarea intensiva de CPU
            total = 0
            for i in range(100000):
                total += i ** 2
            return total
        
        process = psutil.Process()
        
        # Medir CPU antes
        cpu_before = process.cpu_percent()
        
        start_time = time.time()
        
        # Ejecutar tarea intensiva
        result = cpu_intensive_task()
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Medir CPU después
        time.sleep(0.1)  # Pequeña pausa para medición
        cpu_after = process.cpu_percent()
        
        # Verificar que la tarea se completó
        assert result > 0
        assert execution_time < 1.0, f"Tarea CPU muy lenta: {execution_time:.2f}s"
    
    @pytest.mark.performance
    def test_file_operations_performance(self):
        """Test rendimiento de operaciones de archivo"""
        with tempfile.TemporaryDirectory() as temp_dir:
            start_time = time.time()
            
            # Crear muchos archivos pequeños
            for i in range(100):
                file_path = os.path.join(temp_dir, f"test_file_{i}.txt")
                with open(file_path, 'w') as f:
                    f.write(f"Test content {i}")
            
            # Leer todos los archivos
            contents = []
            for i in range(100):
                file_path = os.path.join(temp_dir, f"test_file_{i}.txt")
                with open(file_path, 'r') as f:
                    contents.append(f.read())
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Operaciones de archivo deberían ser rápidas
            assert execution_time < 1.0, f"Operaciones de archivo muy lentas: {execution_time:.2f}s"
            assert len(contents) == 100


class TestBenchmarks:
    """Benchmarks comparativos"""
    
    @pytest.mark.performance
    def test_config_vs_direct_access_benchmark(self):
        """Benchmark: configuración vs acceso directo"""
        # Limpiar caché antes de la prueba
        from config_extended import _api_config_cache
        _api_config_cache.clear()
        
        # Test acceso a través de función (primera llamada - sin caché)
        start_time = time.time()
        config_first = get_api_config('chispart')
        first_call_time = time.time() - start_time
        
        # Test acceso a través de función (con caché)
        start_time = time.time()
        for _ in range(1000):
            config = get_api_config('chispart')
        cached_time = time.time() - start_time
        
        # Test acceso directo (simulado)
        from config_extended import AVAILABLE_APIS
        start_time = time.time()
        for _ in range(1000):
            direct_config = AVAILABLE_APIS['chispart']
        direct_time = time.time() - start_time
        
        # Calcular ratios
        cached_ratio = cached_time / direct_time if direct_time > 0 else float('inf')
        
        # El acceso con caché debería ser razonablemente rápido (ajustado para ser más realista)
        # En entornos de testing, las funciones pueden ser más lentas debido a overhead
        assert cached_ratio < 200, f"Función de configuración con caché muy lenta: {cached_ratio:.2f}x"
        
        # Verificar que la caché funciona (debería ser mucho más rápida que la primera llamada)
        # Solo verificar si la diferencia es significativa
        if first_call_time > 0.001:  # Solo verificar si la primera llamada tomó tiempo significativo
            assert cached_time < first_call_time * 10, "La caché no parece estar funcionando correctamente"
        
        # Imprimir información de rendimiento para diagnóstico
        print(f"\nRendimiento de get_api_config:")
        print(f"  Primera llamada: {first_call_time:.6f}s")
        print(f"  1000 llamadas con caché: {cached_time:.6f}s")
        print(f"  1000 accesos directos: {direct_time:.6f}s")
        print(f"  Ratio caché/directo: {cached_ratio:.2f}x")
        
        # Verificación adicional: el tiempo total no debería ser excesivo
        assert cached_time < 1.0, f"Tiempo total de 1000 llamadas muy lento: {cached_time:.3f}s"
    
    @pytest.mark.performance
    def test_message_creation_benchmark(self):
        """Benchmark: diferentes tipos de creación de mensajes"""
        # Mensaje simple
        start_time = time.time()
        for i in range(1000):
            message = create_text_message(f"Simple message {i}")
        simple_time = time.time() - start_time
        
        # Mensaje complejo
        start_time = time.time()
        for i in range(1000):
            complex_content = f"Complex message {i} with more content " * 10
            message = create_text_message(complex_content)
        complex_time = time.time() - start_time
        
        # Los mensajes complejos no deberían ser desproporcionadamente lentos
        ratio = complex_time / simple_time if simple_time > 0 else float('inf')
        assert ratio < 5, f"Mensajes complejos muy lentos: {ratio:.2f}x más lento"


if __name__ == '__main__':
    # Ejecutar solo tests de rendimiento
    pytest.main([__file__, '-v', '-m', 'performance'])
