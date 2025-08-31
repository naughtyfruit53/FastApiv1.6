import os
import re
import argparse
import subprocess
import shutil
from typing import List, Dict, Tuple

def run_eslint(folder_path: str, fix: bool = False) -> str:
    """Run ESLint on the given folder and return output."""
    cmd = ['eslint', f'{folder_path}/**/*{{.ts,.tsx,.js,.jsx}}', '.next/types/*.ts']
    if fix:
        cmd.append('--fix')
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, shell=True)
        return result.stdout + result.stderr
    except subprocess.CalledProcessError as e:
        return e.output
    except FileNotFoundError:
        return "Error: ESLint not found. Install it with 'npm install -g eslint'."

def parse_eslint_log(log_file: str) -> List[Dict[str, str]]:
    """Parse ESLint log file to extract errors."""
    errors = []
    current_file = None
    error_pattern = re.compile(r'(\d+):(\d+)\s+error\s+(.+?)\s+([\w-]+(?:\/[\w-]+)?)')
    
    try:
        with open(log_file, 'r') as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip()
                if line.startswith('D:\\FastApiV1.6\\V1.6\\frontend\\'):
                    current_file = line
                elif error_pattern.match(line) and current_file:
                    match = error_pattern.match(line)
                    line_num, col_num, error_msg, error_type = match.groups()
                    errors.append({
                        'file': current_file,
                        'line': int(line_num),
                        'column': int(col_num),
                        'message': error_msg,
                        'type': error_type
                    })
    except FileNotFoundError:
        print(f"Error: Log file '{log_file}' not found.")
        return []
    
    return errors

def backup_file(file_path: str) -> str:
    """Create a backup of the file before modifying."""
    backup_path = file_path + '.bak'
    shutil.copy(file_path, backup_path)
    return backup_path

def fix_no_unused_vars(file_path: str, line_num: int, variable: str) -> bool:
    """Remove unused variable or import from the file at the given line."""
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        # Check if the line is an import statement
        if lines[line_num - 1].strip().startswith('import'):
            # Remove the specific import
            import_line = lines[line_num - 1]
            if variable in import_line:
                lines[line_num - 1] = ''  # Remove the entire import line
        else:
            # Remove variable declaration (e.g., const data = ...;)
            if variable in lines[line_num - 1]:
                lines[line_num - 1] = ''  # Remove the variable line
        
        with open(file_path, 'w') as f:
            f.writelines([line for line in lines if line.strip()])
        return True
    except Exception as e:
        print(f"Error fixing no-unused-vars in {file_path}: {e}")
        return False

def fix_no_undef_react(file_path: str) -> bool:
    """Add import React statement if missing."""
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        # Check if React import already exists
        if not any('import * as React from \'react\'' in line for line in lines):
            lines.insert(0, "import * as React from 'react';\n")
            with open(file_path, 'w') as f:
                f.writelines(lines)
            return True
        return False
    except Exception as e:
        print(f"Error fixing no-undef in {file_path}: {e}")
        return False

def fix_no_use_before_define(file_path: str, line_num: int, function_name: str) -> bool:
    """Attempt to reorder function to fix no-use-before-define (simplified approach)."""
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        # Find the function definition
        func_start = None
        func_end = None
        func_lines = []
        for i, line in enumerate(lines):
            if function_name in line and ('function' in line or '=>' in line):
                func_start = i
                func_lines.append(line)
                # Simple heuristic: assume function ends at next closing brace
                brace_count = line.count('{') - line.count('}')
                j = i + 1
                while j < len(lines) and brace_count > 0:
                    func_lines.append(lines[j])
                    brace_count += lines[j].count('{') - lines[j].count('}')
                    j += 1
                func_end = j
                break
        
        if func_start is None or func_end is None:
            return False
        
        # Move function above the usage line
        if func_start > line_num - 1:
            func_block = lines[func_start:func_end]
            del lines[func_start:func_end]
            lines.insert(line_num - 1, ''.join(func_block))
            with open(file_path, 'w') as f:
                f.writelines(lines)
            return True
        return False
    except Exception as e:
        print(f"Error fixing no-use-before-define in {file_path}: {e}")
        return False

def apply_fixes(errors: List[Dict[str, str]]) -> Tuple[List[str], List[Dict[str, str]]]:
    """Apply fixes to files based on error types."""
    fixed_files = []
    remaining_errors = []
    
    for error in errors:
        file_path = error['file']
        line_num = error['line']
        error_type = error['type']
        error_msg = error['message']
        
        # Create backup before modifying
        if file_path not in fixed_files:
            backup_file(file_path)
            fixed_files.append(file_path)
        
        fixed = False
        if error_type == 'no-unused-vars':
            variable = error_msg.split("'")[1]  # Extract variable name
            fixed = fix_no_unused_vars(file_path, line_num, variable)
        elif error_type == 'no-undef' and 'React' in error_msg:
            fixed = fix_no_undef_react(file_path)
        elif error_type == 'no-use-before-define':
            function_name = error_msg.split("'")[1]  # Extract function name
            fixed = fix_no_use_before_define(file_path, line_num, function_name)
        
        if not fixed:
            remaining_errors.append(error)
    
    return fixed_files, remaining_errors

def main():
    parser = argparse.ArgumentParser(description="Check and fix ESLint errors from a log file.")
    parser.add_argument('log_file', type=str, help="Path to ESLint log file (e.g., lint_errors.log)")
    parser.add_argument('folder', type=str, help="Path to the folder to lint (e.g., ./src)")
    args = parser.parse_args()
    
    log_file = args.log_file
    folder_path = args.folder
    
    if not os.path.isfile(log_file):
        print(f"Error: Log file '{log_file}' not found.")
        return
    if not os.path.isdir(folder_path):
        print(f"Error: '{folder_path}' is not a valid folder.")
        return
    
    print(f"Running ESLint --fix on {folder_path}...")
    fix_output = run_eslint(folder_path, fix=True)
    print("Auto-fix complete. Parsing log file for remaining errors...")
    
    errors = parse_eslint_log(log_file)
    if not errors:
        print("No errors found in the log file.")
        return
    
    print(f"Found {len(errors)} errors. Attempting to fix...")
    fixed_files, remaining_errors = apply_fixes(errors)
    
    # Log remaining errors
    remaining_log = 'remaining_errors.log'
    with open(remaining_log, 'w') as f:
        for error in remaining_errors:
            f.write(f"{error['file']} {error['line']}:{error['column']} error {error['message']} {error['type']}\n")
    
    print(f"Fixed files: {', '.join(fixed_files) if fixed_files else 'None'}")
    print(f"Remaining errors logged to '{remaining_log}' ({len(remaining_errors)} errors).")
    if remaining_errors:
        print("Some errors (e.g., no-shadow, explicit-module-boundary-types) require manual fixing. Check the log.")
    else:
        print("All errors fixed successfully!")

if __name__ == "__main__":
    main()