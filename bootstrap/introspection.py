import os
import ast
from typing import List, Dict, Union
from bootstrap import repo_root
from langchain.agents import tool
import json


def get_full_definition(source: str, start_lineno: int, end_lineno: int) -> str:
    """
    Extracts the full definition of a code block from a given source code.

    Parameters:
        source (str): The source code to extract the full definition from.
        start_lineno (int): The starting line number of the code block to extract.
        end_lineno (int): The ending line number of the code block to extract.

    Returns:
        The full definition of the code block as a string.
    """
    source_lines = source.split('\n')
    full_definition_lines = source_lines[start_lineno-1:end_lineno]
    return '\n'.join(full_definition_lines).strip()

def extract_function_info(node: Union[ast.FunctionDef, ast.AsyncFunctionDef], source: str, rel_path: str) -> Dict[str, Union[str, List[Dict[str, Union[str, int]]], None]]:
    """
    Extracts information about a given function or async function node.

    Parameters:
        node (ast.FunctionDef or ast.AsyncFunctionDef): The function or async function node to extract information from.
        source (str): The source code of the module containing the function node.
        rel_path (str): The relative path of the module containing the function node.

    Returns:
        A dictionary containing the extracted information.
    """
    # Extract function signature
    args = [arg.arg for arg in node.args.args]
    vararg = node.args.vararg.arg if node.args.vararg else None
    kwarg = node.args.kwarg.arg if node.args.kwarg else None
    defaults = [ast.literal_eval(default) for default in node.args.defaults] if node.args.defaults else []
    signature = f"{node.name}({', '.join(args)}"
    if vararg:
        signature += f", *{vararg}"
    if kwarg:
        signature += f", **{kwarg}"
    if defaults:
        defaults_str = [repr(default) for default in defaults]
        signature += f", {', '.join(defaults_str)}"
    signature += ')'
    
    # get fully qualified name
    qualname = f"{rel_path.replace(os.path.sep, '.').replace('.py', '')}.{node.name}"
    
    # Extract function docstring and return annotation
    docstring = ast.get_docstring(node)
    
    # Extract function start and end line numbers
    start_lineno = node.lineno
    end_lineno = node.end_lineno

    # Extract the full function definition
    full_definition = get_full_definition(source, start_lineno, end_lineno)

    return {
        "name": node.name,
        "qualname": qualname,
        "type": "function",
        "path": rel_path,
        "signature": signature,
        "docstring": docstring,
        "start_lineno": start_lineno,
        "end_lineno": end_lineno,
        "full_definition": full_definition
    }

def extract_method_info(node: Union[ast.FunctionDef, ast.AsyncFunctionDef], source: str) -> Dict[str, Union[str, int, None]]:
    """
    Extracts information about a given method node.

    Parameters:
        node (ast.FunctionDef or ast.AsyncFunctionDef): The method node to extract information from.
        source (str): The source code of the module containing the method node.

    Returns:
        A dictionary containing the extracted information.
    """
    # Extract method signature
    signature = f"{node.name}({', '.join([arg.arg for arg in node.args.args])})"
    # Extract method docstring and return annotation
    docstring = ast.get_docstring(node)

    # Extract method start and end line numbers
    start_lineno = node.lineno
    end_lineno = node.end_lineno

    # Extract the full method definition
    full_definition = get_full_definition(source, start_lineno, end_lineno)

    return {
        "type": "method",
        "name": node.name,
        "signature": signature,
        "docstring": docstring,
        "start_lineno": start_lineno,
        "end_lineno": end_lineno,
        "full_definition": full_definition
    }
    
def extract_class_info(node: ast.ClassDef, source: str, rel_path: str) -> Dict[str, Union[str, List[Dict[str, Union[str, int, None]]]]]:
    """
    Extracts information about a given class node.Parameters:
        node (ast.ClassDef): The class node to extract information from.
        source (str): The source code of the module containing the class node.
        rel_path (str): The relative path of the module containing the class node.

    Returns:
        A dictionary containing the extracted information.
    """
    class_body = []

    # Process each class node in the class body
    for class_node in node.body:
        if isinstance(class_node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            class_body.append(extract_method_info(class_node, source))
        elif isinstance(class_node, ast.Assign):
            class_body.append({
                "type": "assignment",
                "name": class_node.targets[0].id,
                "lineno": class_node.lineno
            })
        elif isinstance(class_node, ast.Expr):
            class_body.append({
                "type": "expression",
                "value": ast.dump(class_node.value),
                "lineno": class_node.lineno
            })

    # Extract class docstring, signature, and start and end line numbers
    docstring = ast.get_docstring(node)
    signature = f"class {node.name}"
    start_lineno = node.lineno
    end_lineno = node.end_lineno

    # Extract the full class definition
    full_definition = get_full_definition(source, start_lineno, end_lineno)

    # get fully qualified name
    qualname = f"{rel_path.replace(os.path.sep, '.').replace('.py', '')}.{node.name}"

    return {
        "name": node.name,
        "qualname": qualname,
        "type": "class",
        "path": rel_path,
        "signature": signature,
        "docstring": docstring,
        "body": class_body,
        "start_lineno": start_lineno,
        "end_lineno": end_lineno,
        "full_definition": full_definition
    }

def process_nodes(module_ast: ast.Module, source: str, rel_path: str) -> List[Dict[str, Union[str, List[Dict[str, Union[str, int, None]]]]]]:
    """
    Processes all nodes in a given module AST.Parameters:
        module_ast (ast.Module): The module AST to process.
        source (str): The source code of the module.
        rel_path (str): The relative path of the module.

    Returns:
        A list of dictionaries containing the extracted information for all functions and classes in the module.
    """
    result = []

    # Process each node in the module AST
    for node in module_ast.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            result.append(extract_function_info(node, source, rel_path))
        elif isinstance(node, ast.ClassDef):
            result.append(extract_class_info(node, source, rel_path))
            
    return result


def extract_functions_and_classes(path: str) -> List[Dict[str, Union[str, List[Dict[str, Union[str, int, None]]]]]]:
    """
    Extracts information about all the functions and classes in a given path.Parameters:
        path (str): The path to the directory to search for Python modules.

    Returns:
        A list of dictionaries representing the functions and classes found in the modules.
    """
    functions_and_classes = []

    # Recursively search for Python modules in the given directory
    for root, dirs, files in os.walk(path):
        for filename in files:
            if filename.endswith('.py'):
                file_path = os.path.join(root, filename)

                with open(file_path, 'r') as file:
                    source = file.read()

                try:
                    module_ast = ast.parse(source)
                except SyntaxError:
                    # Ignore modules with syntax errors
                    continue

                # Extract information about all functions and classes in the module
                rel_path = os.path.relpath(file_path, path)
                functions_and_classes.extend(process_nodes(module_ast, source, rel_path))

    return functions_and_classes

def get_current_repo_functions_and_classes(*args, **kwargs) -> List[Dict[str, Union[str, List[Dict[str, Union[str, int, None]]]]]]:
    """
    Extracts information about all the functions and classes in the current repo.

    Returns:
        A list of dictionaries representing the functions and classes found in the repo modules.
    """
    return extract_functions_and_classes(repo_root)

@tool("get_current_repo_definitions_summary")
def get_current_repo_definitions_summary(*args, **kwargs):
    """
    Extracts names of all the functions and classes in the current repo. This tool takes no inputs.
    """
    info = get_current_repo_functions_and_classes()
    keep_keys = ['qualname', 'type', 'signature', 'docstring']
    return [{k:v for k,v in item.items() if k in keep_keys} for item in info]
    
def _get_parent_module_source_code(function_qualname: str) -> Union[str, None]:
    """
    Given a function or class qualname, returns the source code of the module in which it resides.

    Parameters:
        function_qualname (str): The qualname of the function or class.

    Returns:
        The source code of the parent module if found, otherwise None.
    """
    functions_and_classes = get_current_repo_functions_and_classes()
    for item in functions_and_classes:
        if item['qualname'] == function_qualname:
            rel_path = item.get('path', None)
            if rel_path:
                with open(os.path.join(repo_root, rel_path), 'r') as file:
                    source = file.read()
                return source
    return None


    
def _get_source_code(qualname: str) -> Union[str, None]:
    """
    Given a function or class qualname, returns its source code.

    Parameters:
        qualname (str): The qualname of the function or class.

    Returns:
        The source code of the function or class if found, otherwise None.
    """
    functions_and_classes = get_current_repo_functions_and_classes()

    for item in functions_and_classes:
        if item['qualname'] == qualname:
            return item.get('full_definition', None)
        
    all_qualnames = [item['qualname'] for item in functions_and_classes]
    return f"Could not find source code. Valid qualnames are: {all_qualnames}"

@tool("get_source_code")
def get_source_code(input:str):
    """
    Given a function or class qualname, returns its source code. The input to this tool should be formatted as follows:
    {'qualname': '<qualname of the function or class>'}
    """
    try:
        parsed_inputs = json.loads(input)
    except json.JSONDecodeError:
        parsed_inputs = {'qualname': input}
    return _get_source_code(**parsed_inputs)

def _edit_source_code(qualname: str, new_code: str) -> bool:
    """
    Replaces the source code of a function or class with new code and saves the module.

    Parameters:
        qualname (str): The qualname of the function or class.
        new_code (str): The new code to replace the original code.

    Returns:
        True if the source code was successfully updated, otherwise False.
   """
    functions_and_classes = get_current_repo_functions_and_classes()
    parent_module_source = _get_parent_module_source_code(qualname)
    if parent_module_source is None:
        return False

    function_info = None
    for item in functions_and_classes:
        if item['qualname'] == qualname:
            function_info = item
            break

    if function_info is None:
        return False

    start_lineno = function_info.get('start_lineno', None)
    end_lineno = function_info.get('end_lineno', None)
    rel_path = function_info.get('path', None)

    if start_lineno and end_lineno and rel_path:
        source_lines = parent_module_source.split('\n')
        updated_source_lines = source_lines[:start_lineno - 1] + new_code.split('\n') + source_lines[end_lineno:]
        updated_source = '\n'.join(updated_source_lines)

        try:
            ast.parse(updated_source)
            with open(os.path.join(repo_root, rel_path), 'w') as file:
                file.write(updated_source)
            return True
        except SyntaxError:
            return False

    return False

@tool("edit_source_code")
def edit_source_code(inputs: str) -> bool:
    """
    Replaces the source code of a function or class with new code and saves the module.
    
    The inputs to this tool should be a dictionary formatted as follows:
        {'qualname': '<qualname of the function or class>', 'new_code': '<new code>'}
    """
    try:
        parsed_inputs = json.loads(inputs)
    except json.JSONDecodeError:
        return """
Error parsing inputs. Please ensure that the inputs are formatted as follows:
{'qualname': '<qualname of the function or class>', 'new_code': '<new code>'}
"""
    return _edit_source_code(**parsed_inputs)

