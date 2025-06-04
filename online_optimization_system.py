import asyncio
import threading
import queue
import time
import json
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
import dspy
from concurrent.futures import ThreadPoolExecutor
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class OptimizationRequest:
    """Request to optimize model with new data"""
    training_data: List[Any]
    trigger_reason: str
    timestamp: datetime
    model_version: str

@dataclass
class InferenceResult:
    """Result from model inference"""
    prediction: Any
    confidence: float
    model_version: str
    latency_ms: float
    timestamp: datetime

class AsyncModelManager:
    """Manages model versions and hot-swapping"""
    
    def __init__(self):
        self.current_model = None
        self.current_version = "v0"
        self.model_lock = threading.RLock()
        self.performance_history = []
        
    def load_model(self, model_path: str, version: str) -> bool:
        """Thread-safe model loading"""
        try:
            with self.model_lock:
                # Load new model using the current model's class
                new_model = self.current_model.__class__.load(model_path)
                
                # Atomic swap
                old_model = self.current_model
                old_version = self.current_version
                
                self.current_model = new_model
                self.current_version = version
                
                logger.info(f"Model updated: {old_version} -> {version}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to load model {version}: {e}")
            return False
    
    def get_model(self):
        """Get current model for inference"""
        with self.model_lock:
            return self.current_model, self.current_version
    
    def record_performance(self, accuracy: float, latency: float):
        """Record model performance metrics"""
        self.performance_history.append({
            'version': self.current_version,
            'accuracy': accuracy,
            'latency': latency,
            'timestamp': datetime.now()
        })

class DataCollector:
    """Collects inference data for optimization"""
    
    def __init__(self, batch_size: int = 50):
        self.batch_size = batch_size
        self.data_buffer = []
        self.buffer_lock = threading.Lock()
        
    def add_example(self, input_data: Any, prediction: Any):
        """Add training example to buffer"""
        with self.buffer_lock:
            example = {
                'input': input_data,
                'prediction': prediction,
                'timestamp': datetime.now()
            }
            self.data_buffer.append(example)
            
    def get_batch(self) -> Optional[List[Any]]:
        """Get batch of data if ready"""
        with self.buffer_lock:
            if len(self.data_buffer) >= self.batch_size:
                batch = self.data_buffer[:self.batch_size]
                self.data_buffer = self.data_buffer[self.batch_size:]
                return batch
        return None

class OptimizationEngine:
    """Background SIMBA optimization engine"""
    
    def __init__(self, base_program: dspy.Module, metric_fn: Callable, model_manager: AsyncModelManager):
        self.base_program = base_program
        self.metric_fn = metric_fn
        self.model_manager = model_manager
        self.optimization_queue = queue.Queue()
        self.is_running = False
        self.worker_thread = None
        
    def start(self):
        """Start background optimization worker"""
        self.is_running = True
        self.worker_thread = threading.Thread(target=self._optimization_worker)
        self.worker_thread.start()
        logger.info("Optimization engine started")
    
    def stop(self):
        """Stop background optimization"""
        self.is_running = False
        if self.worker_thread:
            self.worker_thread.join()
        logger.info("Optimization engine stopped")
    
    def queue_optimization(self, request: OptimizationRequest):
        """Queue optimization request"""
        self.optimization_queue.put(request)
        logger.info(f"Queued optimization: {request.trigger_reason}")
    
    def _optimization_worker(self):
        """Background worker that processes optimization requests"""
        while self.is_running:
            try:
                # Get optimization request (timeout to check is_running)
                request = self.optimization_queue.get(timeout=1.0)
                
                logger.info(f"Starting optimization: {request.trigger_reason}")
                start_time = time.time()
                
                # Run SIMBA optimization
                optimized_model = self._run_simba_optimization(
                    request.training_data, 
                    request.model_version
                )
                
                duration = time.time() - start_time
                logger.info(f"Optimization completed in {duration:.2f}s")
                
                # Signal completion (could trigger model loading)
                self._on_optimization_complete(optimized_model, request)
                
            except queue.Empty:
                continue  # Check is_running and continue
            except Exception as e:
                logger.error(f"Optimization failed: {e}")
    
    def _run_simba_optimization(self, training_data: List[Any], 
                               base_version: str) -> dspy.Module:
        """Run SIMBA optimization on training data"""
        try:
            # Initialize SIMBA with online-friendly parameters
            simba = dspy.SIMBA(
                metric=self.metric_fn,
                max_steps=4,      # Reduced for faster optimization
                max_demos=min(10, len(training_data)))
            
            # Convert data to DSPy format
            trainset = self._prepare_trainset(training_data)
            
            # Run optimization
            optimized_program = simba.compile(
                self.base_program,
                trainset=trainset,
                seed=int(time.time())  # Different seed each time
            )
            
            return optimized_program
            
        except Exception as e:
            logger.error(f"SIMBA optimization failed: {e}")
            return self.base_program  # Return original if optimization fails
    
    def _prepare_trainset(self, training_data: List[Any]) -> List[Any]:
        """Convert collected data to DSPy training format"""
        trainset = []
        for example in training_data:
            # Use prediction as both input and output for latency optimization
            dspy_example = dspy.Example(
                input=example['input'],
                output=example['prediction']
            ).with_inputs('input')
            trainset.append(dspy_example)
        return trainset
    
    def _on_optimization_complete(self, optimized_model: dspy.Module, 
                                 request: OptimizationRequest):
        """Handle completed optimization by swapping model in memory"""
        try:
            new_version = f"v{int(time.time())}"
            
            # Safely swap model instance
            with self.model_manager.model_lock:
                self.model_manager.current_model = optimized_model
                self.model_manager.current_version = new_version
                
            logger.info(f"Optimized model loaded: {new_version}")
            print(f"\n🔥 OPTIMIZATION COMPLETE! New model: {new_version}")
                
        except Exception as e:
            logger.error(f"Optimization completion failed: {e}")
            print(f"\n❌ OPTIMIZATION ERROR: {str(e)[:50]}...")

class OnlineOptimizationSystem:
    """Main system that coordinates inference and optimization"""
    
    def __init__(self, base_program: dspy.Module, metric_fn: Callable, 
                 batch_size=30, optimization_interval=3600, performance_trigger_count=100):
        self.model_manager = AsyncModelManager()
        self.data_collector = DataCollector(batch_size=batch_size)
        self.optimization_engine = OptimizationEngine(base_program, metric_fn, self.model_manager)
        
        # Optimization triggers
        self.inference_count = 0
        self.last_optimization = time.time()
        self.optimization_interval = optimization_interval
        self.performance_threshold = 0.8   # Trigger if accuracy drops below 80%
        self.performance_trigger_count = performance_trigger_count
        
        # Initialize with base model
        self.model_manager.current_model = base_program
        
    def start(self):
        """Start the online optimization system"""
        self.optimization_engine.start()
        logger.info("Online optimization system started")
    
    def stop(self):
        """Stop the online optimization system"""
        self.optimization_engine.stop()
        logger.info("Online optimization system stopped")
    
    async def inference(self, input_data: Any) -> InferenceResult:
        """
        Primary inference method - responds immediately to inputs
        This is what you call for real-time predictions
        """
        start_time = time.time()
        
        # Get current model (thread-safe)
        model, version = self.model_manager.get_model()
        
        # Run inference
        try:
            prediction = model(input_data)
            confidence = getattr(prediction, 'confidence', 1.0)
            
            latency_ms = (time.time() - start_time) * 1000
            
            result = InferenceResult(
                prediction=prediction,
                confidence=confidence,
                model_version=version,
                latency_ms=latency_ms,
                timestamp=datetime.now()
            )
            
            # Collect data for future optimization (non-blocking)
            self._collect_inference_data(input_data, prediction)
            
            # Check optimization triggers (non-blocking)
            self._check_optimization_triggers()
            
            return result
            
        except Exception as e:
            # Graceful degradation: fallback to simple response
            logger.error(f"Inference failed: {e}")
            return InferenceResult(
                prediction="System is optimizing, try again shortly",
                confidence=0.0,
                model_version="fallback",
                latency_ms=0,
                timestamp=datetime.now()
            )
    
    
    def _collect_inference_data(self, input_data: Any, prediction: Any):
        """Collect inference data for optimization"""
        self.data_collector.add_example(input_data, prediction)
        self.inference_count += 1
    
    def _check_optimization_triggers(self):
        """Check if optimization should be triggered"""
        current_time = time.time()
        
        # Time-based trigger
        if current_time - self.last_optimization > self.optimization_interval:
            batch = self.data_collector.get_batch()
            if batch:
                self._trigger_optimization("scheduled_interval", batch)
        
        # Data availability trigger
        batch = self.data_collector.get_batch()
        if batch:
            self._trigger_optimization("data_batch_ready", batch)
        # Performance-based trigger
        elif self.inference_count > self.performance_trigger_count:
            recent_performance = self._estimate_recent_performance()
            if recent_performance < self.performance_threshold:
                batch = self.data_collector.get_batch()
                if batch:
                    self._trigger_optimization("performance_degradation", batch)
    
    def _trigger_optimization(self, reason: str, batch: List[Any]):
        """Trigger background optimization with available batch"""
        request = OptimizationRequest(
            training_data=batch,
            trigger_reason=reason,
            timestamp=datetime.now(),
            model_version=self.model_manager.current_version
        )
        
        self.optimization_engine.queue_optimization(request)
        self.last_optimization = time.time()
    
    def _estimate_recent_performance(self) -> float:
        """Estimate recent model performance from recorded history"""
        if not self.model_manager.performance_history:
            return 1.0  # Default to perfect performance
        
        # Use average accuracy of last 20 inferences
        recent_history = self.model_manager.performance_history[-20:]
        total_accuracy = sum(entry['accuracy'] for entry in recent_history)
        return total_accuracy / len(recent_history)
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status"""
        return {
            'current_model_version': self.model_manager.current_version,
            'inference_count': self.inference_count,
            'data_buffer_size': len(self.data_collector.data_buffer),
            'optimization_queue_size': self.optimization_engine.optimization_queue.qsize(),
            'last_optimization': self.last_optimization,
            'uptime': time.time() - getattr(self, 'start_time', time.time())
        }

# Moved to top-level scope with other demo code

if __name__ == "__main__":
    print("="*60)
    print("ONLINE OPTIMIZATION DEMO")
    print("="*60)
    print("This demo shows how a system can continuously improve its model:")
    print("1. Solve multiplication problems (e.g., 'What is 23 times 45?')")
    print("2. Use '/replay N' to generate N random problems")
    print("3. System collects data automatically")
    print("4. When enough data is collected, optimization triggers")
    print("5. New models are hot-swapped without downtime")
    print("Watch for model version changes during the session")
    print("Type 'exit' to quit\n")
    
    # Configure DSPy with DeepSeek Chat
    llm = dspy.LM(model='deepseek/deepseek-chat')
    dspy.settings.configure(lm=llm)
    
    import random

    class MultiplicationModule(dspy.Module):
        def __init__(self):
            self.generate_answer = dspy.ChainOfThought("question -> answer")
            
        def forward(self, question):
            return self.generate_answer(question=question)
    
    def multiplication_metric(example, prediction, trace=None):
        try:
            # Parse numbers from input (works for both questions and assignments)
            numbers = [int(n) for n in example.split() if n.isdigit()]
            if len(numbers) < 2:
                return 0.0
            a, b = numbers[:2]
            correct_answer = a * b
            
            # Parse model's answer - look for last number in response
            numbers_in_answer = [int(n) for n in str(prediction.answer).split() if n.isdigit()]
            if not numbers_in_answer:
                return 0.0
            model_answer = numbers_in_answer[-1]
            
            return 1.0 if model_answer == correct_answer else 0.0
        except:
            return 0.0
    
    # Initialize system with demo-friendly settings
    base_program = MultiplicationModule()
    system = OnlineOptimizationSystem(
        base_program,
        multiplication_metric,
        batch_size=32,             # Increased to meet SIMBA minimum
        optimization_interval=30,  # Longer interval to reduce triggers
        performance_trigger_count=32
    )
    
    # Define helper function for the demo
    async def run_question(system, question, last_version, latency_history):
        """Run a question through the system and handle output"""
        # Track input details
        print(f"⤵️ Input: {question}")
        
        # Run inference
        start_time = time.time()
        result = await system.inference(question)
        latency_ms = result.latency_ms
        
        # Track latency
        latency_history.append(latency_ms)
        if len(latency_history) > 10:
            latency_history.pop(0)
        avg_latency = sum(latency_history) / len(latency_history)
        
        # Show answer
        if hasattr(result.prediction, 'answer'):
            print(f"🖼️  Model: {result.model_version} | 🔥 Answer: {result.prediction.answer}")
        else:
            print(f"🖼️  Model: {result.model_version}| 🔥 Answer: {result.prediction}")
            
        print(f"⏱️  Latency: {latency_ms:.2f}ms | 📈 Avg: {avg_latency:.2f}ms")
        
        # Show optimization status
        status = system.get_system_status()
        print(f"📊 Buffer: {status['data_buffer_size']}/{system.data_collector.batch_size} | Queued: {status['optimization_queue_size']}")
        
        # Show version updates
        if last_version != result.model_version:
            print(f"\n🚀 MODEL UPDATED: {last_version} → {result.model_version}")
            last_version = result.model_version
        return last_version
    
    async def main():
        """Interactive demo showing online optimization"""
        # Start system
        system.start()
        print("System started. Type questions or commands.")
        
        try:
            latency_history = []  # Track last 10 latencies
            last_version = system.model_manager.current_version
            while True:
                # Get user input
                question = await asyncio.get_event_loop().run_in_executor(
                    None, input, "\nAsk a multiplication question (or type '/replay N' to optimize, 'exit' to quit): "
                )
                
                if question.lower() == 'exit':
                    break
                    
                if question.startswith('/replay'):
                    # Generate 40 problems to reliably fill buffer
                    try:
                        for _ in range(40):
                            # Generate random multiplication problem
                            a = random.randint(10, 99)
                            b = random.randint(10, 99)
                            random_question = f"What is {a} times {b}?"
                            last_version = await run_question(system, random_question, last_version, latency_history)
                    except:
                        print("Error occurred during replay")
                    continue
                    
                # Use common function for user questions
                last_version = await run_question(system, question, last_version, latency_history)
                    
        finally:
            system.stop()
            print("System stopped")
    
    asyncio.run(main())
