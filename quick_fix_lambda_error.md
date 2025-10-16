# Lambda Error Fix

## Error Analysis
The error `<lambda>() got an unexpected keyword argument 'script_data'` suggests that somewhere a lambda function is receiving keyword arguments when it only expects positional arguments.

## Root Cause
The issue is likely in the `run_in_thread` method where the lambda function is defined with a default argument but somewhere it's being called with keyword arguments.

## Quick Fix
The lambda functions in `run_in_thread` need to be able to accept any arguments:

```python
# Current (problematic):
lambda result=result: self.handle_thread_result(result)

# Should be:
lambda r=result: self.handle_thread_result(r)
```

Or better yet, ensure the lambda can handle any argument style.

## Alternative Solution
Instead of using lambdas with default arguments, use functools.partial or a different approach to avoid variable capture issues.

