import os
import ast
from typing import List, Dict, Union
from bootstrap import repo_root

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
    
    # Extract function docstring and return annotation
    docstring = ast.get_docstring(node)
    return_annotation = ast.get_type_annotation(node.returns) if node.returns else None
    
    # Extract function start and end line numbers
    start_lineno = node.lineno
    end_lineno = node.end_lineno

    # Extract the full function definition
    full_definition = get_full_definition(source, start_lineno, end_lineno)

    return {
        "name": node.name,
        "type": "function",
        "path": rel_path,
        "signature": signature,
        "docstring": docstring,
        "return_annotation": return_annotation,
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
    return_annotation = ast.get_type_annotation(node.returns) if node.returns else None

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
        "return_annotation": return_annotation,
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

    return {
        "name": node.name,
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