from functools import wraps
from typing import Callable, Any, Dict, Optional
import time
import logging
from .telemetry import get_tracer, telemetry

logger = logging.getLogger(__name__)

def trace_method(operation_name: Optional[str] = None, 
                record_args: bool = True,
                record_result: bool = True):
    """
    Decorator to add distributed tracing to methods
    
    Args:
        operation_name: Custom operation name (defaults to method name)
        record_args: Whether to record method arguments as span attributes
        record_result: Whether to record result metadata as span attributes
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            tracer = get_tracer()
            span_name = operation_name or func.__name__
            
            with tracer.start_as_current_span(span_name) as span:
                # Record method arguments
                if record_args:
                    _record_method_args(span, func, args, kwargs)
                
                try:
                    # Execute the method
                    result = func(*args, **kwargs)
                    
                    # Record result metadata
                    if record_result:
                        _record_result_metadata(span, result, func.__name__)
                    
                    span.set_attribute("result", "success")
                    return result
                    
                except Exception as e:
                    span.record_exception(e)
                    span.set_attribute("result", "error")
                    span.set_attribute("error_type", type(e).__name__)
                    logger.error(f"Error in {func.__name__}: {e}")
                    raise
                    
        return wrapper
    return decorator

def measure_yfinance_call(ticker_arg: str = "ticker"):
    """
    Decorator specifically for yfinance API calls
    
    Args:
        ticker_arg: Name of the argument containing the ticker symbol
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extract ticker from arguments
            ticker = _extract_ticker_from_args(args, kwargs, ticker_arg, func)
            
            # Measure execution time
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Record successful call
                telemetry.record_yfinance_request(duration, ticker, success=True)
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                
                # Record failed call
                telemetry.record_yfinance_request(duration, ticker, success=False)
                raise
                
        return wrapper
    return decorator

def record_prediction_metrics(ticker_arg: str = "ticker", 
                            days_arg: str = "days",
                            model_type: str = "random_forest"):
    """
    Decorator to record prediction metrics
    
    Args:
        ticker_arg: Name of the argument containing the ticker symbol
        days_arg: Name of the argument containing prediction days
        model_type: Type of ML model being used
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extract arguments
            ticker = _extract_ticker_from_args(args, kwargs, ticker_arg, func)
            days = _extract_arg_from_args(args, kwargs, days_arg, func, default=7)
            
            # Record prediction request
            telemetry.record_prediction_request(ticker, days, model_type)
            
            return func(*args, **kwargs)
                
        return wrapper
    return decorator

def time_operation(operation_name: Optional[str] = None):
    """
    Decorator to measure and log operation duration
    
    Args:
        operation_name: Custom operation name for logging
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            op_name = operation_name or func.__name__
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                logger.debug(f"{op_name} completed in {duration:.3f}s")
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"{op_name} failed after {duration:.3f}s: {e}")
                raise
                
        return wrapper
    return decorator

def log_method_call(log_level: int = logging.INFO, 
                   include_args: bool = False,
                   include_result: bool = False):
    """
    Decorator to log method calls
    
    Args:
        log_level: Logging level to use
        include_args: Whether to include arguments in log
        include_result: Whether to include result summary in log
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            method_name = func.__name__
            
            # Log method entry
            if include_args:
                args_str = _format_args_for_logging(args, kwargs)
                logger.log(log_level, f"Calling {method_name} with args: {args_str}")
            else:
                logger.log(log_level, f"Calling {method_name}")
            
            try:
                result = func(*args, **kwargs)
                
                # Log method completion
                if include_result:
                    result_summary = _summarize_result_for_logging(result)
                    logger.log(log_level, f"{method_name} completed: {result_summary}")
                else:
                    logger.log(log_level, f"{method_name} completed successfully")
                
                return result
                
            except Exception as e:
                logger.error(f"{method_name} failed: {e}")
                raise
                
        return wrapper
    return decorator

# Helper functions

def _record_method_args(span, func: Callable, args: tuple, kwargs: dict):
    """Record method arguments as span attributes"""
    try:
        # Get function signature
        import inspect
        sig = inspect.signature(func)
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()
        
        # Record specific arguments
        for param_name, value in bound_args.arguments.items():
            if param_name == 'self':
                continue
                
            # Convert common types to string for span attributes
            if isinstance(value, (str, int, float, bool)):
                span.set_attribute(f"arg.{param_name}", value)
            elif hasattr(value, '__len__'):
                span.set_attribute(f"arg.{param_name}_length", len(value))
            else:
                span.set_attribute(f"arg.{param_name}_type", type(value).__name__)
                
    except Exception as e:
        logger.debug(f"Failed to record method args: {e}")

def _record_result_metadata(span, result, method_name: str):
    """Record result metadata as span attributes"""
    try:
        if result is None:
            span.set_attribute("result_type", "None")
        elif isinstance(result, (list, tuple)):
            span.set_attribute("result_length", len(result))
            span.set_attribute("result_type", type(result).__name__)
        elif hasattr(result, '__len__'):
            span.set_attribute("result_length", len(result))
            span.set_attribute("result_type", type(result).__name__)
        elif isinstance(result, (str, int, float, bool)):
            span.set_attribute("result_value", str(result))
        else:
            span.set_attribute("result_type", type(result).__name__)
            
    except Exception as e:
        logger.debug(f"Failed to record result metadata: {e}")

def _extract_ticker_from_args(args: tuple, kwargs: dict, ticker_arg: str, func: Callable) -> str:
    """Extract ticker symbol from method arguments"""
    try:
        # Try kwargs first
        if ticker_arg in kwargs:
            return kwargs[ticker_arg]
        
        # Try positional args
        import inspect
        sig = inspect.signature(func)
        param_names = list(sig.parameters.keys())
        
        if ticker_arg in param_names:
            ticker_index = param_names.index(ticker_arg)
            if ticker_index < len(args):
                return args[ticker_index]
        
        return "unknown"
        
    except Exception:
        return "unknown"

def _extract_arg_from_args(args: tuple, kwargs: dict, arg_name: str, func: Callable, default=None):
    """Extract any argument from method arguments"""
    try:
        # Try kwargs first
        if arg_name in kwargs:
            return kwargs[arg_name]
        
        # Try positional args
        import inspect
        sig = inspect.signature(func)
        param_names = list(sig.parameters.keys())
        
        if arg_name in param_names:
            arg_index = param_names.index(arg_name)
            if arg_index < len(args):
                return args[arg_index]
        
        return default
        
    except Exception:
        return default

def _format_args_for_logging(args: tuple, kwargs: dict) -> str:
    """Format arguments for logging (sanitized)"""
    try:
        # Skip 'self' argument
        log_args = args[1:] if args and hasattr(args[0], '__class__') else args
        
        # Truncate long arguments
        formatted_args = []
        for arg in log_args:
            if isinstance(arg, str) and len(arg) > 50:
                formatted_args.append(f"{arg[:47]}...")
            else:
                formatted_args.append(str(arg))
        
        # Format kwargs
        formatted_kwargs = []
        for key, value in kwargs.items():
            if isinstance(value, str) and len(value) > 50:
                formatted_kwargs.append(f"{key}={value[:47]}...")
            else:
                formatted_kwargs.append(f"{key}={value}")
        
        all_args = formatted_args + formatted_kwargs
        return ", ".join(all_args)
        
    except Exception:
        return "args formatting failed"

def _summarize_result_for_logging(result) -> str:
    """Summarize result for logging"""
    try:
        if result is None:
            return "None"
        elif isinstance(result, (list, tuple)):
            return f"{type(result).__name__}(length={len(result)})"
        elif hasattr(result, '__len__'):
            return f"{type(result).__name__}(length={len(result)})"
        elif isinstance(result, (str, int, float, bool)):
            return f"{type(result).__name__}: {result}"
        else:
            return f"{type(result).__name__}"
            
    except Exception:
        return "result summary failed"
