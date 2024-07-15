"""
This logic is largely copied from the Hendrycks' MATH release (math_equivalence), and borrowed from:
- https://github.com/microsoft/ProphetNet/tree/master/CRITIC
"""
import multiprocessing
from math import isclose
from typing import Union

from sympy import simplify, N
from sympy.parsing.sympy_parser import parse_expr
from sympy.parsing.latex import parse_latex


def is_digit(s):
    """
    Checks if the input can be converted to a float.

    Parameters
    ----------
    s : any
        The input to check.

    Returns
    -------
    bool
        True if the input can be converted to a float, False otherwise.

    Raises
    ------
    None
    """
    try:
        float(str(s).replace(",", ""))
        return True
    except ValueError:
        return False

def math_equal(prediction: Union[bool, float, str],
                reference: Union[float, str],
                include_percentage: bool = True,
                is_close: bool = True,
                timeout: bool = False,
                ) -> bool:
    """
    Determines if two math expressions are equal.

    Exact match of math if and only if:
    1. numerical equal: both can convert to float and are equal
    2. symbolic equal: both can convert to sympy expression and are equal

    Parameters
    ----------
    prediction : Union[bool, float, str]
        The predicted value.

    reference : Union[float, str]
        The reference value.

    include_percentage : bool, optional
        Whether to include percentage variations, by default True.

    is_close : bool, optional
        Whether to consider close match using relative tolerance, by default True.

    timeout : bool, optional
        Whether to apply timeout to the symbolic equal check, by default False.

    Returns
    -------
    bool
        True if the values are equal, False otherwise.

    Raises
    ------
    None
    """
    try: # 1. numerical equal
        if is_digit(prediction) and is_digit(reference):
            prediction = float(str(prediction).replace(",", ""))
            reference = float(str(reference).replace(",", ""))
            # number questions
            if include_percentage:
                gt_result = [reference / 100, reference, reference * 100]
            else:
                gt_result = [reference]
            for item in gt_result:
                try:
                    if is_close:
                        if isclose(item, prediction, rel_tol=1e-4):
                            return True
                    else:
                        if item == prediction:
                            return True
                except Exception:
                    continue
            return False
    except:
        pass

    if not prediction and prediction not in [0, False]:
        return False

    # 2. symbolic equal
    reference = str(reference).strip()
    prediction = str(prediction).strip()

    ## deal with [], (), {}
    pred_str, ref_str = prediction, reference
    if (prediction.startswith("[") and prediction.endswith("]") and not reference.startswith("(")) or \
        (prediction.startswith("(") and prediction.endswith(")") and not reference.startswith("[")):
        pred_str = pred_str.strip("[]()")
        ref_str = ref_str.strip("[]()")
    for s in ['{', "}", "(", ")"]:
        ref_str = ref_str.replace(s, "")
        pred_str = pred_str.replace(s, "")
    if pred_str == ref_str:
        return True

    ## [a, b] vs. [c, d], return a==c and b==d
    if (prediction.startswith("[") and prediction.endswith("]")) and (reference.startswith("[") and reference.endswith("]")) or \
        (prediction.startswith("(") and prediction.endswith(")")) and (reference.startswith("(") and reference.endswith(")")):
        pred_parts = prediction[1:-1].split(",")
        ref_parts = reference[1:-1].split(",")
        if len(pred_parts) == len(ref_parts):
            if all([math_equal(pred_parts[i], ref_parts[i], include_percentage, is_close) for i in range(len(pred_parts))]):
                return True

    # symbolic equal with sympy
    if timeout:
        if call_with_timeout(symbolic_equal_process, prediction, reference):
            return True
    else:
        if symbolic_equal(prediction, reference):
            return True

    return False


def math_equal_process(param):
    """
    Calls `math_equal` function with the provided parameters.

    Parameters
    ----------
    param : tuple
        Tuple containing parameters for `math_equal` function.

    Returns
    -------
    bool
        True if the values are equal, False otherwise.

    Raises
    ------
    None
    """
    return math_equal(param[-2], param[-1])


def symbolic_equal(a, b):
    """
    Checks if two expressions are symbolically equal using sympy.

    Parameters
    ----------
    a : str
        First expression.

    b : str
        Second expression.

    Returns
    -------
    bool
        True if the expressions are equal, False otherwise.

    Raises
    ------
    None
    """
    def _parse(s):
        for f in [parse_latex, parse_expr]:
            try:
                return f(s)
            except:
                pass
        return s
    a = _parse(a)
    b = _parse(b)

    try:
        if simplify(a-b) == 0:
            return True
    except:
        pass

    try:
        if isclose(N(a), N(b), rel_tol=1e-3):
            return True
    except:
        pass
    return False


def symbolic_equal_process(a, b, output_queue):
    """
    Checks if two expressions are symbolically equal using sympy.

    Parameters
    ----------
    a : str
        First expression.

    b : str
        Second expression.

    output_queue : multiprocessing.Queue
        Queue to store the result.

    Returns
    -------
    None

    Raises
    ------
    None
    """
    result = symbolic_equal(a, b)
    output_queue.put(result)  


def call_with_timeout(func, *args, timeout=1, **kwargs):
    """
    Calls a function with a specified timeout.

    Parameters
    ----------
    func : function
        The function to call.

    timeout : int, optional
        Timeout value in seconds, by default 1.

    *args : list
        Positional arguments for the function.
        
    **kwargs : dict
        Keyword arguments for the function.

    Returns
    -------
    bool
        True if the function call succeeds within the timeout, False otherwise.

    Raises
    ------
    None
    """ 
    output_queue = multiprocessing.Queue()  
    process_args = args + (output_queue,)  
    process = multiprocessing.Process(target=func, args=process_args, kwargs=kwargs)  
    process.start()  
    process.join(timeout)  
  
    if process.is_alive():  
        process.terminate()  
        process.join()  
        return False  
  
    return output_queue.get()

